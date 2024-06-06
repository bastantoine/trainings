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

# 1.2 Factorisation de la config

---

## 1.2.a Paramètres globaux
Certains paramètres des jobs peuvent être définis au niveau global de la pipeline. Leur définition affecte l'ensemble des jobs de la pipeline.

Les paramètres définis au niveau global peuvent être redéfinis au niveau de chaque job, auquel cas la valeur définie dans le job aura précédence. Il est possible de contrôler quels paramètres sont hérités, voire désactiver complètement l'héritage des paramètres globaux pour un job donné avec, `[job].inherit.default` et `[job].inherit.variables` [\[ref\]](https://docs.gitlab.com/ee/ci/jobs/index.html#control-the-inheritance-of-default-keywords-and-global-variables).

---

## 1.2.a Paramètres globaux

```yaml
default:
  retry: 2
  image: ruby:3.0
  interruptible: true

job1:
  script: echo "This job does not inherit any default keywords."
  inherit:
    default: false

job2:
script: echo "This job inherits only the two listed default keywords. It does not inherit 'interruptible'."
  inherit:
     default:
      - retry
      - image
```

---

## 1.2.a Paramètres globaux

Les paramètres pouvant être définis au niveau global sont, notamment :
* [`artifacts`](https://docs.gitlab.com/ee/ci/yaml/#artifacts)
* [`cache`](https://docs.gitlab.com/ee/ci/yaml/#cache)
* [`image`](https://docs.gitlab.com/ee/ci/yaml/#image)
* [`services`](https://docs.gitlab.com/ee/ci/yaml/#services)
* [`tags`](https://docs.gitlab.com/ee/ci/yaml/#tags)

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/#default)

---

## 1.2.b Héritage de jobs

Plusieurs manières sont possibles pour faire en sorte qu'un job hérite d'un autre :
1. À l'aide des références YAML
2. À l'aide du keyword `extends`
3. À l'aide du tag `!reference`
4. À l'aide inclusions externes

---

### Références YAML
Le langage YAML propose une fonctionnalité de références, permettant de faire référence à certaines portions d'un fichier YAML au sein du même fichier, afin de les réutiliser à différents endroits.

En utilisant les jobs cachés (ie. des jobs dont le nom commence par un point), on peut définir des templates réutilisables à différents endroits du fichier de config.

---

### Références YAML

- `&< key >`: permet d'associer une clé `key` à un mapping clé-valeur ou une liste
- `*< key >`: insert la configuration identifiée par la clé `key` comme valeur d'une clé donnée dans le cas d'un mapping, ou comme élément d'une liste dans le cas d'une liste
- `<<: *< key >`: insert la configuration identifiée par la clé `key` au sein du mapping clé-valeur actuel

Lors de l'utilisation de références YAML, il est possible de redéfinir une valeur héritée d'une référence. Il suffit pour cela de fournir une nouvelle valeur.

---

### Références YAML

<div class="columns">
<div>

```yaml
.job_template: &job_configuration
  script:
    - test project
  tags:
    - dev

.postgres_services:
  services: &postgres_configuration
    - postgres
    - ruby

.mysql_services:
  services: &mysql_configuration
    - mysql
    - ruby

test:postgres:
  <<: *job_configuration
  services: *postgres_configuration
  tags:
    - postgres

test:mysql:
  <<: *job_configuration
  services: *mysql_configuration
```

</div>
<div>

```yaml
test:postgres:
  script:
    - test project
  services:
    - postgres
    - ruby
  tags:
    - postgres

test:mysql:
  script:
    - test project
  services:
    - mysql
    - ruby
  tags:
    - dev
```

</div>
</div>

---

<div class="columns">
<div>

⚠️ **Attention** : Si un paramètre est défini au sein d'une référence, ainsi que là où la référence est utilisée, c'est la dernière valeur qui est pris en compte.

Ainsi pour que la surcharge du paramètre soit correctement effectuée, il faut qu'il soit redéfini après l'utilisation de la référence YAML.

</div>
<div>

Avec la config suivante, une fois les références résolues, le `job-1` aura comme image `python:3.11` alors que le `job-2` utilisera `python:3.10` :
```yaml
.default-python-image: &default-python-image
  image: python:3.10

job-1:
  <<: *default-python-image
  image: python3.11

job-2:
  image: python3.11
  <<: *default-python-image
```

</div>
</div>

---

### Utilisation du keyword `extends`

<div class="columns">
<div>

Gitlab propose le keyword `extends` afin de permettre la réutilisation de différentes portion de config. Son utilisation est similaires aux ancres YAML, mais plus simple et plus flexible dans son usage.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#extends)

</div>
<div>

```yaml
.tests:
  script: rake test
  stage: test
  only:
    refs:
      - branches

rspec:
  extends: .tests
  script: rake rspec
  only:
    variables:
      - $RSPEC
```

</div>
</div>

---

### Utilisation du keyword `extends`

Il est possible d'étendre plusieurs configurations à la fois :
```yaml
.only-important:
  tags: [production]
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
.in-docker:
  tags: [docker]
  image: alpine

build:
  extends:
    - .only-important
    - .in-docker
  script: echo
```

---

### Utilisation du keyword `extends`

⚠️ **Attention** : Dans le cas où des paramètres hérités de configurations référencées via `extends` sont redéfinis au niveau du job, c'est toujours la valeur du job qui sera prise en compte, et ce quelque soit l'ordre dans lequel la déclaration du `extends` et la redéfinition du paramètre sont faits.

Cependant, dans le cas où un job hérite de plusieurs configurations via `extends`, si un paramètre est défini dans plusieurs configurations à la fois, seule la dernière définition sera prise en compte (ie. la configuration la plus proche de la fin de la liste des héritages).

---

### Utilisation du keyword `extends`

Ainsi dans la configuration suivante, les deux jobs `job-1`et `job-2` auront tout deux `python:3.11` comme image :
```yaml
.default-python-image:
  image: python:3.10

job-1:
  extends: .default-python-image
  image: python3.11

job-2:
  image: python3.11
  extends: .default-python-image
```

---

### Utilisation du tag `!reference`

<div class="columns">
<div>

Gitlab propose le tag YAML custom `!reference` permettant de réutiliser des portions de configuration dans la définition des jobs. Cette syntaxe est similaire aux références YAML, mais est plus flexible.
[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/yaml_optimization.html#reference-tags)

</div>
<div>

```yaml
.vars:
  variables:
    URL: "http://my-url.internal"
    IMPORTANT_VAR: "the details"

test-vars-1:
  variables: !reference [.vars, variables]
  script:
    - printenv

test-vars-2:
  variables:
    MY_VAR: !reference [.vars, variables, IMPORTANT_VAR]
  script:
    - printenv
```

</div>
</div>

---

### Inclusions externes

Avec les références YAML, `extends` et `!reference`, il est possible de réutiliser des configurations au sein d'un même fichier.

Le keyword [`include`](https://docs.gitlab.com/ee/ci/yaml/index.html#include) permet d'inclure des fichiers externes au sein d'un fichier de configuration.

```yaml
include: '/templates/cicd-template.yml'
```

---

### Inclusions externes

Plusieurs types d'inclusions sont possibles :
* `include:local` : inclure un fichier présent dans le projet courant [\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#includelocal)
* `include:remote` : inclure un fichier accessible via une URL HTTP ou HTTPS [\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#includeremote)
* `include:project` : inclure un fichier présent dans un autre projet [\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#includeproject)

---

### Inclusions externes

- Les fichiers accessibles via une URL pour les inclusions remote doivent être accessible par une requête GET sans authentification.
- Lorsqu'un fichier référencé via un `include:project` est privé, l'utilisateur qui lance la pipeline doit être membre des deux projets pour que l'inclusion puisse se faire.
- Si le type d'inclusion n'est pas indiqué, les liens commençant par `http://` ou `https://` seront considérés comme des remote, tandis que les autres seront considérés comme des inclusions de fichiers locaux.

---

### Inclusions externes

Il est possible d'inclure plusieurs fichiers externes en les listant les uns après les autres :

```yaml
include:
  - local: '/templates/cicd-template-1.yml'
  - remote: 'https://my.service.com/gitlab/templates/cicd-template-2.yml'
  - project: 'my-group/my-project'
    ref: main
    file: '/templates/cicd-template-3.yml'

stages:
  ...
```

---

### Inclusions externes

Il est possible de redéfinir certains paramètres hérités de config externes, que ça soit au niveau global de la pipeline, ou au niveau local d'un job.

Dans ce cas, la valeur définie au sein du fichier de config aura la précédence sur celle provenant d'une inclusion externe.

Des configs importées via un `include` peuvent être réutilisées avec `extends` et `!reference`, mais pas avec les références YAML.

---

### Inclusions externes

> ⚠️ **Attention** : Le mécanisme d'inclusions externes ne doit pas être utilisé comme un mécanisme de sécurité permettant de contraindre l'utilisation de certains jobs. En effet, de part son fonctionnement, n'importe qui ayant accès au projet peut avoir accès aux fichiers inclus, qu'ils soient locaux, en remote où bien d'un autre projet. Ainsi il serait techniquement possible pour cette personne de récupérer le contenu de ces fichiers et de les modifier afin de contourner un ou plusieurs jobs.

---

#### Contrôler les inclusions externes

<div class="columns">
<div>

Il est possible de rajouter des règles qui conditionnent l'inclusion de configurations externes, avec les keywords `include:rules:if` et `include:rules:exists`. Les règles sont les mêmes qu'avec les  rules des jobs.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/includes.html#use-rules-with-include)

</div>
<div>

```yaml
include:
  - local: builds.yml
    rules:
      - if: $INCLUDE_BUILDS == "true"
  - local: deploys.yml
    rules:
      - if: $CI_COMMIT_BRANCH == "main"

test:
  stage: test
  script: exit 0
```

</div>
</div>

---

#### Processus d'inclusion

<img src="../Attachements/Job%20inheritance%20process/Job%20inheritance%20process.svg" width="70%" class="center" style="margin-top: 50px;" />

---

#### Processus d'inclusion
Quelques notes sur le processus d'inclusions des fichiers externes :
- Les fichiers externes sont inclus les uns après les autres, dans l'ordre de leur déclaration
- Si un paramètre est défini dans plusieurs fichiers de configuration, la valeur du dernier fichier le définissant est celle utilisée

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/includes.html#merge-method-for-include)

---

#### Processus d'inclusion
<img src="../Attachements/Job%20inheritance%20process/Job%20inheritance%20process%201.svg" width="100%" class="center" style="margin-top: 100px;" />

---

#### Processus d'inclusion
<img src="../Attachements/Job%20inheritance%20process/Job%20inheritance%20process%202.svg" width="100%" class="center" style="margin-top: 100px;" />

---

#### Processus d'inclusion
<img src="../Attachements/Job%20inheritance%20process/Job%20inheritance%20process%203.svg" width="100%" class="center" style="margin-top: 100px;" />

---

## Exercices

- [Exercice 8](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex8)

- [Exercice 9](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex9)

- [Exercice 10](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex10)
