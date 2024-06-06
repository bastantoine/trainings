---
marp: true
theme: gaia
_class: lead
paginate: false
backgroundImage: url('https://marp.app/assets/hero-background.svg')
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }

  .columns-3 {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
  }

  img.center {
    display: block;
    margin: 0 auto;
  }
---

# 1.4 Downstream pipelines

Les pipelines downstream sont une fonctionnalité permettant de **lancer une ou plusieurs pipelines depuis une autre pipeline**.

<div class="columns">
<div>

1. Les **pipelines parent-enfants**
2. Les **pipelines multi-projets**

</div>
<div>

<img src="../Attachements/Downstream%20pipelines/Parent-child%20vs%20multi-projects.svg" width="100%" class="center" style="margin-top: 20px;" />

</div>
</div>

---

## 1.4.a Exemples

Pipeline parent-enfant :
```yaml
trigger_job:
  trigger:
    include:
      - local: path/to/child-pipeline.yml
```

Pipeline multi-projets
```yaml
trigger_job:
  trigger:
    project: project-group/my-downstream-project
```

---

<div class="columns">
<div>

## 1.4.b Configuration

Il est possible de fournir des variables aux pipelines downstream, afin d'agir sur leur configuration.

**Toutes les variables accessibles au niveau du job réalisant le trigger sont accessibles au sein de la pipeline downstream**.

</div>
<div>

Dans le cas où une variable est définie dans les deux pipelines, **celle de la pipeline upstream aura la précédence**.

```yaml
variables:
  VERSION: "1.0.0"

staging:
  variables:
    ENVIRONMENT: staging
  stage: deploy
  trigger:
    include:
      - local: path/to/child-pipeline.yml
```

</div>
</div>

---

## 1.4.b Configuration

<div class="columns">
<div>

Il est possible de bloquer la transmission des variables de CICD aux pipelines downstream en utilisant le keyword `[job]:inherit:variables`.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#inheritvariables)

</div>
<div>

```yaml
variables:
  GLOBAL_VAR: value

trigger-job:
  inherit:
    variables: false
  variables:
    JOB_VAR: value
  trigger:
    include:
      - local: path/to/child-pipeline.yml
```

</div>
</div>

---

> ⚠️ **Attention** : Dans le cas des pipelines multi-projets, **la configuration des variables de CICD définies au niveau du projet parent n'est pas transmise à la pipeline downstream**.
>
> Ainsi **une variable définie comme masquée au sein du projet upstream ne le sera pas nécessairement au sein du projet downstream**.
>
> Les pipelines parent-enfants ne sont pas concernées par cette limitation puisque dans ce cas les pipelines upstream et downstream s'exécutent au sein du même project.

---

## 1.4.c Influence des pipelines downstream sur les pipelines upstream

Une fois le job de trigger de la pipeline downstream lancé, **son statut n'aura pas d'influence sur le statut de la pipeline upstream**.

Dès lors que la pipeline downstream est créée, le job de création est marqué en succès, et l'exécution de la pipeline upstream continue.

Ainsi **si une pipeline downstream est en échec, la pipeline upstream pourra tout de même être en succès**.

---

## 1.4.c Influence des pipelines downstream sur les pipelines upstream

<div class="columns">
<div>

Il est possible d'indiquer une **dépendance d'une pipeline upstream envers une ou plusieurs de ses pipelines downstream**, à l'aide du keyword `trigger:strategy`.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#triggerstrategy)

</div>
<div>

Dans ce cas, **le job ayant lancé la pipeline downstream ne sera terminé que lorsque celle-ci sera terminée**. Son statut sera celui de la pipeline lancée.

```yaml
trigger_job:
  trigger:
    include: path/to/child-pipeline.yml
    strategy: depend
```

</div>
</div>

---

## 1.4.d Exécution conditionnelle
Comme le trigger est configuré au sein d'un job, **il est possible de lui ajouter des rules pour contrôler dans quel cas il est ajouté**, et donc dans quel cas la pipeline downstream est lancée.

```yaml
build:
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  trigger:
    include:
      - local: pipelines/build.yml
```

---

### Source des pipelines downstream
Lorsqu'une pipeline downstream est lancée, sa source, accessible via  [`$CI_PIPELINE_SOURCE`](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html) est définie à une valeur spécifique :
- `pipeline` pour les pipelines multi-projects.
- `parent_pipeline` pour les pipelines parent-enfants.

**Cette source est la même pour tous les jobs de la pipeline downstream**.

---

### Source des pipelines downstream

Cette configuration permet de **concevoir des jobs qui ne s'ajoutent que dans le cas où la pipeline a été lancée via une pipeline upstream**.

```yaml
job1:
  rules:
    - if: $CI_PIPELINE_SOURCE == "pipeline"
job2:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
job3:
  rules:
    - if: $CI_PIPELINE_SOURCE == "pipeline"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

---

## 1.4.e Utilisation de l'API pour le trigger

Parfois le lancement de pipelines multi-projets n'est pas possible en utilisant le keyword `[job]:trigger:project`.

Il est **possible d'utiliser l'API de trigger afin de lancer la pipeline** désirée.

```yaml
trigger_pipeline:
  stage: deploy
  script:
    - curl --request POST \
      --form "token=$CI_JOB_TOKEN" \
      --form ref=main \
      "https://<gitlab instance>/api/v4/projects/<project ID or path>/trigger/pipeline"
```

---

## 1.4.e Utilisation de l'API pour le trigger

L'authentification à cet endpoint peut se faire à l'aide du `CI_JOB_TOKEN`. [\[ref\]](https://docs.gitlab.com/ee/ci/jobs/ci_job_token.html)

> ℹ️ **Notes** : Le `$CI_JOB_TOKEN` est un **token généré automatiquement par Gitlab lors du lancement d'un job**. Il permet de s'authentifier sur certains endpoint de l'API Gitlab.
>
> Il n'est **utilisable que lors de l'exécution du job**, et est invalidé une fois son exécution terminée. Il **possède les mêmes droits que la personne ayant lancé la pipeline** dont le job fait partie.

---

## 1.4.e Utilisation de l'API pour le trigger

Il est possible de fournir une ou plusieurs variables à la pipeline downstream qui est lancée à l'aide du endpoint de trigger. Pour se faire, il suffit de fournir le(s) variable(s) à transmettre à la pipeline downstream en tant que paramètre de formulaire :

```bash
curl --request POST \
     --form "token=$CI_JOB_TOKEN" \
     --form ref=main \
     --form "variables[VAR1]=value1" \
     --form "variables[VAR2]=value2" \
     "https://<gitlab instance>/api/v4/projects/<project ID or path>/trigger/pipeline"
```

[\[ref\]](https://docs.gitlab.com/ee/api/pipeline_triggers.html#trigger-a-pipeline-with-a-token)
