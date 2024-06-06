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
![bg left:40% 80%](https://about.gitlab.com/images/press/logo/svg/gitlab-logo-500.svg)

# **Gitlab CI** <!-- omit from toc -->

Bastien ANTOINE

---

# 1. Architecture avancée

- [Accélération de l'exécution des jobs](#11-accélération-de-lexécution-des-jobs)
- [Factorisation de la config](#12-factorisation-de-la-config)
- [Dépendances inter-jobs](#13-dépendances-inter-jobs)
- [Downstream pipelines](#14-downstream-pipelines)
- [Services](#15-services)

---

# 1.1 Accélération de l'exécution des jobs

---

## 1.1.a Mise en cache
Gitlab CICD propose une solution de mise en cache de certains fichiers afin de pouvoir accélérer l'exécution des jobs.

L'idée est de **stocker des fichiers ou des dépendances qui changent peu souvent**.

---

### Comparaison avec les artifacts

|                                | Cache | Artifacts |
|--------------------------------|:-----:|:---------:|
| Entre jobs de la même pipeline | ✓ (1) |     ✓     |
| Entre pipelines du même projet | ✓ (2) |     ✗     |
| Entre projets                  |   ✗   |     ✗     |

1. seulement si les dépendances sont identiques
2. seulement si le cache n'a expiré, pas été invalidé, et que les dépendances sont identiques

---

### Définition des fichiers à mettre en cache

<div class="columns">
<div>

La définition des fichiers ou dossiers à collecter pour la mise en cache se fait au niveau du job **via la clé `[job].cache.paths`**.

Cette clé accepte une liste de paths ou pattern identifiant une ou plusieurs fichiers ou dossiers.

</div>
<div>

```yaml
job:
  script:
    - echo "This job uses a cache."
  cache:
    paths:
      - ...
```

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/#cachepaths)

</div>
</div>

---

### Définition des fichiers à mettre en cache

> ℹ️ **Note** : Les fichiers pouvant être mis en cache doivent **nécessairement se trouver au sein du dossier où le projet est cloné et où le job fonctionne** (identifié par `$CI_PROJECT_DIR`).
>
> Ainsi il peut être nécessaire d'adapter la manière dont le cache est géré afin que le(s) fichier(s) et/ou dossier(s) à mettre en cache soient présent au bon endroit.

---

### Définition de la clé du cache

<div class="columns">
<div>

La clé du cache est **un nom permettant d'identifier le cache à stocker et/ou récupérer** du runner. Sa définition se fait avec la clé `[job].cache.key`.

**Tous les jobs qui utilisent la même clé de cache vont référencer le même cache**, quelque soit leur pipeline.

</div>
<div>

```yaml
job:
  script:
    - echo "This job uses a cache."
  cache:
    key: my-cache-key
    paths:
      - ...
```

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/#cachekey)

</div>
</div>

---

### Définition de la clé du cache

La clé de cache étant évaluée au sein du runner, il est possible d'utiliser des variables dans la définition.

Ainsi **on peut définir et utiliser différents caches selon différentes conditions** : même cache pour toute une branche, pour un même job pour toutes les branches...

[\[ref\]](https://docs.gitlab.com/ee/ci/caching/index.html#common-use-cases-for-caches)

---

#### Utilisation de fichiers pour la clé du cache

<div class="columns">
<div>

Il est **possible d'utiliser un ou plusieurs fichiers pour déterminer la clé du cache**.

Ainsi **si au moins un des fichiers listé est changé, la clé change et le cache est invalidé** et doit donc être regénéré.

[\[ref\]](https://docs.gitlab.com/ee/ci/caching/index.html#compute-the-cache-key-from-the-lock-file)

</div>
<div>

```yaml
cache:
  key:
    files:
      - package-lock.json
    paths:
      - .npm/
```

Cela permet notamment d'associer la gestion du cache à des systèmes de gestion de dépendances basés sur des lockfiles.

</div>
</div>

---

### Stockage du cache

À la différence des artifacts **le cache est stocké au sein du runner**.

Les combinaisons des tags des jobs d'une pipeline peuvent faire qu'on se retrouve dans un cas où un job génère le cache sur un runner, et le job suivant, étant lancé sur un autre runner, n'a pas accès à ce cache.

Ainsi **il peut être nécessaire de mettre en place un partage du cache entre les runners** afin de s'assurer que les caches soient accessibles pour tous les jobs.

[\[ref\]](https://docs.gitlab.com/ee/ci/caching/index.html#where-the-caches-are-stored)

---

### Stockage du cache

<img src="Attachements/Cache/Cache%201.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="Attachements/Cache/Cache%202.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="Attachements/Cache/Cache%203.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="Attachements/Cache/Cache%204.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="Attachements/Cache/Cache%205.svg" width="70%" class="center" />

---

### Stockage du cache

> ⚠️ **Attention** : Le cache **peut ne pas être disponible**. Ainsi **les jobs ne doivent pas en dépendre et doivent être capables de régénérer les fichiers** manquant si besoin.
>
> Si les jobs sont dépendants de fichiers générés à des étapes antérieures, et qu'ils ne peuvent pas les générer eux mêmes, il faut utiliser les artefacts.
>
> [\[ref\]](https://docs.gitlab.com/ee/ci/caching/index.html#cache-mismatch)

---

### Politique de récupération et mise à jour du cache

Par défaut, **tous les jobs utilisant du cache vont tenter de récupérer le cache associé**, et une fois leur exécution terminée, **vont uploader une nouvelle version du cache** si des fichiers et/ou dossiers associés au cache ont été modifiés.

Ce processus **peut conduire à des situations où le cache est mis à jour trop fréquemment** et pour des raisons parfois inutiles.

---

### Politique de récupération et mise à jour du cache

Dans ces cas là, il faut agir sur la **politique de récupération et mise à jour du cache**. Ce paramètre se contrôle via le keyword `[job].cache.policy`. **Par défaut la politique est en `pull-push`**, ce qui signifie tenter de récupérer le cache en début de job et le mettre à jour à la fin si nécessaire.

Une **autre politique est `pull`**, qui va simplement tenter de récupérer le cache, mais ne pas le mettre à jour, même si des fichiers associés au cache ont été modifiés.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/#cachepolicy)

---

## 1.1.b Parallélisation des jobs

Certains jobs peuvent être très long à exécuter et donc être très coûteux en temps. Lorsque c'est possible, **on peut découper les tâches à réaliser en un nombre donné de sous-tâches**, et **exécuter chacune de ces sous-tâches en parallèle** les unes des autres afin de gagner du temps.

---

## 1.1.b Parallélisation des jobs

Pour cela on utilise le keyword `parallel`. Ce keyword permet d'indiquer combien de sous-jobs lancer en parallèle.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#parallel)

```yaml
test:
  parallel: 3
  script:
    - pip install pytest-split
    - pytest --splits $CI_NODE_TOTAL --group $CI_NODE_INDEX
```

---

## 1.1.b Parallélisation des jobs

> ℹ️ **Note** : `$CI_NODE_INDEX` et `$CI_NODE_TOTAL` sont deux variables accessibles par un job lorsque celui ci introduit de la parallélisation.
> - `$CI_NODE_TOTAL` indique le nombre total de sous-jobs lancés en parallèle.
> - `$CI_NODE_INDEX` indique l'index du sous-job actuel au sein de la liste des sous-jobs parallelisés.
>
> [\[ref\]](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)

---

## 1.1.b Parallélisation des jobs

Il est également possible de **configurer une matrice de valeurs afin de configurer les différents sous-jobs** à lancer.

Pour cela on utilise le **keyword `parallel:matrix`**. Ce keyword permet de **définir une ou plusieurs variables avec leurs différentes valeurs possibles**. À partir des différentes valeurs des différentes variables, une matrice à N dimensions est générée avec la liste de toutes les combinaisons possibles, et **un job est lancé pour chacune de ces combinaisons**.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#parallelmatrix)

---

## 1.1.b Parallélisation des jobs

Les **variables définies au sein de la matrice sont accessibles et utilisables comme des variables classiques** pour la configuration du job.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#parallelmatrix)

---

## 1.1.b Parallélisation des jobs

```yaml
stages:
  - test

tests:
  stage: test
  parallel:
    matrix:
    - IMAGE: python
      VERSION: ['3.10', '3.11']
      OS: ['bullseye', 'alpine']
  image: ${IMAGE}:${VERSION}-${OS}
  script:
  - uname -a
  - python3 --version
```

---

## 1.1.b Parallélisation des jobs

<img src="Attachements/Parallel%20matrix/Parallel%20matrix%201.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="Attachements/Parallel%20matrix/Parallel%20matrix%202.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="Attachements/Parallel%20matrix/Parallel%20matrix%203.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="Attachements/Parallel%20matrix/Parallel%20matrix%204.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="Attachements/Parallel%20matrix/Parallel%20matrix%205.svg" width="85%" style="margin-top: 70px;" class="center" />

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

<img src="Attachements/Job%20inheritance%20process/Job%20inheritance%20process.svg" width="70%" class="center" style="margin-top: 50px;" />

---

#### Processus d'inclusion
Quelques notes sur le processus d'inclusions des fichiers externes :
- Les fichiers externes sont inclus les uns après les autres, dans l'ordre de leur déclaration
- Si un paramètre est défini dans plusieurs fichiers de configuration, la valeur du dernier fichier le définissant est celle utilisée

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/includes.html#merge-method-for-include)

---

#### Processus d'inclusion
<img src="Attachements/Job%20inheritance%20process/Job%20inheritance%20process%201.svg" width="100%" class="center" style="margin-top: 100px;" />

---

#### Processus d'inclusion
<img src="Attachements/Job%20inheritance%20process/Job%20inheritance%20process%202.svg" width="100%" class="center" style="margin-top: 100px;" />

---

#### Processus d'inclusion
<img src="Attachements/Job%20inheritance%20process/Job%20inheritance%20process%203.svg" width="100%" class="center" style="margin-top: 100px;" />

---

## Exercices

- [Exercice 8](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex8)

- [Exercice 9](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex9)

- [Exercice 10](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex10)

---

# 1.3 Dépendances inter-jobs

À l'aide du **keyword `[job]:needs`, il est possible de définir un DAG** (*Directed Acyclic Graph*, *Graphe Orienté Acyclique*). Cette fonctionnalité permet de **sortir de l'exécution séquentielle classique** où les stages s'exécutent les uns après les autres, selon la configuration prédéfinie.

En définissant un DAG, on indique des dépendances entre des jobs, ce qui permet d'accélérer l'exécution de la pipeline. **Un job qui a certaines dépendances d'indiquées va s'exécuter dès lors que le(s) job(s) dont il dépend auront été exécuté(s) avec succès**.

---

## 1.3.a Impact sur la récupération des artefacts

<div class="columns">
<div>

Tout comme [`[job]:dependencies`](https://docs.gitlab.com/ee/ci/yaml/#dependencies), lorsqu'un job déclare une ou plusieurs dépendance(s), **il ne va récupérer que les artefacts produits par le(s) job(s) dont il dépend**.

Il est **possible de ne récupérer aucun artefacts des dépendances**, tout en conservant celles-ci.

</div>
<div>

```yaml
test job:
  stage: test
  needs:
    - job: "build job"
      artifacts: false
```

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/#needsartifacts)
</div>
</div>

---

# 1.4 Downstream pipelines

Les pipelines downstream sont une fonctionnalité permettant de **lancer une ou plusieurs pipelines depuis une autre pipeline**.

<div class="columns">
<div>

1. Les **pipelines parent-enfants**
2. Les **pipelines multi-projets**

</div>
<div>

<img src="Attachements/Downstream%20pipelines/Parent-child%20vs%20multi-projects.svg" width="100%" class="center" style="margin-top: 20px;" />

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

---

# 1.5 Services

Les services sont des conteneurs lancés en parallèle d'un job et auxquels le job a accès. Ils peuvent être utilisés, par exemple, pour mettre à disposition une base de donnée à des jeux de tests.

Cela peut permettre par exemple de lancer une base de donnée en parallèle du job lançant les tests, afin que ceux-ci puissent y avoir accès.

---

# 1.5 Services

<div class="columns">
<div>

⚠️ **Attention** : Ce mécanisme ne peut être utilisé que pour des services accessibles via le réseau. Tout autre moyen d'interaction avec le service additionnel n'est pas possible.

</div>
<div>

Le job suivant ne fonctionne pas :
```yaml
job:
  services:
    - php:7
    - node:latest
    - golang:1.10
  image: alpine:3.7
  script:
    - php -v
    - node -v
    - go version
```

</div>
</div>

---

## 1.5.a Configuration
Comme tout conteneur Docker, la configuration des services se fait via des variables d'environnement.

Toutes les variables accessibles par le job seront automatiquement mises à disposition des services créés. Il est possible de définir des variables fournies uniquement au service pour leur configuration.

Les services ont accès au fichiers du job puisque le dossier du job est monté en tant que volume au path `/build`.

---

# Exemple

```yaml
test:
  stage: test
  image: python:3.11
  variables:
    MYSQL_USER: user
    MYSQL_PASSWORD: password
    MYSQL_DATABASE: database
  script:
    - export MYSQL_HOST=mysql
    - python script.py
  services:
    - name: mysql:latest
      variables:
        MYSQL_ROOT_PASSWORD: password
```

---

## 1.5.b Accès au service depuis le job

Lors du lancement des conteneurs pour le job et le(s) service(s) configurés, l'executor du runner va créer un lien entre les différents conteneurs afin qu'il soient tous accessibles les uns des autres.

Lorsque les services sont lancés, chacun est accessible via deux hostnames déterminés automatiquement à partir de l'image utilisée.

<img src="Attachements/Service%20name%20aliases.svg" width="70%" class="center" style="margin-top: 10px;" />

---

## 1.5.b Accès au service depuis le job

> ℹ️ **Note** : Chaque service dispose de deux alias avec lesquels il est joignable. L'alias secondaire est nécessaire puisque les hostname contenant des underscores ne sont pas valides, et ainsi peuvent causer des comportements imprévus selon les systèmes.

> ℹ️ **Note** : Il est possible de fournir un autre alias au service, via le keyword `[job].services.alias`. Ainsi le service en question sera joignable via cet alias, et uniquement celui ci.

---

## 1.5.c Disponibilité de la fonctionnalité
Puisque le mécanisme de services se base sur des conteneurs Docker, il ne peut nécessaire que fonctionner sur des runners avec des executors Docker ou Kubernetes.

---

## Exercices

- [Exercice 11](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex11)

---

# 2. Runner executors

- [Shell](#21-shell)
- [SSH](#22-ssh)
- [VirtualBox, Parallels](#23-virtualbox-parallels)
- [Docker](#24-docker)
- [Docker Machine, Docker Autoscaler](#25-docker-machine-docker-autoscaler)
- [Kubernetes](#26-kubernetes)
- [Custom](#27-custom)
- [Comparaison](#28-comparaison)


---

# 2. Runner executors

<div class="columns">
<div>

L'executor est le programme qui tourne sur le runner et qui est en charge d'executer les jobs.

Il existe différent types d'executors.

</div>
<div>

- Shell
- SSH
- VirtualBox, Parallels
- Docker
- Docker Machine, Docker Autoscaler
- Kubernetes
- Custom

</div>
</div>

---

## 2.1 Shell

L'executor Shell est l'un des executors les plus simples. Il va simplement exécuter le script du job dans un shell au sein de la machine où l'executor est installé et configuré.

Tous les outils qui peuvent être nécessaires pour l'exécution des jobs doivent être installés au préalable sur la machine

> ℹ️ **Note** : Puisque les jobs s'exécutent directement dans un shell sur la machine où est installé l'executor, il est nécessaire d'avoir `git` installé et accessible dans le `PATH`.

---

## 2.2 SSH

L'executor SSH est assez similaire à l'executor Shell, mais va exécuter les commandes des jobs dans une machine distante via une connexion SSH. Il supporte l'authentification via username/mot de passe ou par une clé SSH.

> ℹ️ **Note** : Puisque l'executor ne se base pas sur une image de base pour préparer l'environnement, il est nécessaire d'avoir `git` installé et accessible dans le `PATH` de la machine où le runner est installé.

---

## 2.3 VirtualBox, Parallels

Les executors VirtualBox et Parallels permettent d'utiliser des VM pour executer les scripts des jobs.

L'executor se base sur une VM de base qui doit être créée au préalable. L'executor va réaliser une copie de cette VM pour chacun des jobs, et executer leurs scripts au sein de ces VM.

> ℹ️ **Note** : Puisque l'executor ne se base pas sur une image de base pour préparer l'environnement, il est nécessaire d'avoir `git` installé et accessible dans le `PATH` de la machine où le runner est installé.

---

## 2.4 Docker

Avec l'executor Docker, chacun des jobs va s'exécuter dans un conteneur dédié, à partir d'une image donnée. Au total 3 conteneurs seront créés pour chaque job :

1. Un conteneur pour les étapes de pré-build : clone du repo, récupération des artifacts et du cache
2. Un conteneur basé sur l'image spécifiée dans le job, ou une image par défaut, pour l'exécution des étapes du job
3. Un conteneur pour les étapes de post-build : récupération des artifacts et du cache

---

## 2.5 Docker Machine, Docker Autoscaler

Docker Machine et Docker Autoscaler sont deux executors basés sur l'executor Docker, mais qui fournissent en plus des fonctionnalités d'autoscaling de la capacité du runner, afin de supporter des charges variables.

À mesure que la charge du runner va varier, l'executor va créer plus ou moins de hosts Docker sur lesquels les jobs vont pouvoir s'executer.

[\[ref\]](https://docs.gitlab.com/runner/executors/docker_machine.html) [\[ref\]](https://docs.gitlab.com/runner/executors/docker_autoscaler.html)

---

## 2.5 Docker Machine, Docker Autoscaler

Ces executors s'appuient sur des solutions de virtualisations qui sont en charge de gérer les hosts sur lesquels tournent les jobs.

Docker Machine supporte de nombreux outils de virtualisation : AWS, Azure, GCP, OpenStack, HyperV... ([liste complète](https://gitlab.com/gitlab-org/ci-cd/docker-machine/-/tree/main/drivers))

Docker Autoscaler est similaire à Docker Machine, mais supporte, pour le moment, moins de provider (AWS, Azure, GCP, Parallels)

---

## 2.5 Docker Machine, Docker Autoscaler

> ⚠️ **Attention** : Docker Machine était un outil proposé par Docker, mais déprécié depuis septembre 2021 [\[ref\]](https://github.com/docker/machine). Gitlab maintient un fork uniquement pour corriger des bugs critiques affectant le fonctionnement même de l'executor

> ⚠️ **Attention** : Docker Autoscaler est un executor relativement récent et encore en version alpha.

---

## 2.6 Kubernetes

L'executor Kubernetes permet de faire fonctionner les jobs au sein de pods sur un cluster Kubernetes. Un pod avec 3 conteneurs sera créé pour le job :

1. Un conteneur pour les étapes de pré-build : clone du repo, récupération des artifacts et du cache
2. Un conteneur basé sur l'image spécifiée dans le job, ou une image par défaut, pour l'exécution des étapes du job
3. Un conteneur pour les étapes de post-build : récupération des artifacts et du cache

---

## 2.7 Custom

Gitlab permet l'utilisation d'executors custom afin de permettre le support de cas qui ne sont pas couverts par les executors déjà présents, comme par exemple l'utilisation de LXD ou libvirt pour la construction de conteneurs.

Pour cet executor, il est nécessaire de configurer les commandes à exécuter pour les différentes étapes des jobs.

---

## 2.7 Custom

```yaml
runners:
  - name: custom runner
    url: 'https://gitlab.com'
    token: <RUNNERS TOKEN>
    executor: custom
    custom:
      config_exec: /path/to/config.sh
      config_args: [SomeArg]
      prepare_exec: /path/to/script.sh
      prepare_args: [SomeArg]
      run_exec: /path/to/binary
      run_args: [SomeArg]
      cleanup_exec: /path/to/executable
      cleanup_args: [SomeArg]
```

[\[ref\]](https://docs.gitlab.com/runner/executors/custom.html)

---

## 2.8 Comparaison

<style scoped>
table {
  font-size: 23px;
}
</style>

| Executor                                                      |  SSH   | Shell  | VirtualBox/Parallels | Docker | Kubernetes |
|---------------------------------------------------------------|:------:|:------:|:--------------------:|:------:|:----------:|
| Environnement de build dédié à chaque job                     |   ✗    |   ✗    |          ✓           |   ✓    |     ✓      |
| Réutilisation du projet précédement cloné                     |   ✓    |   ✓    |          ✗           |   ✓    |     ✗      |
| Protection de l'accès aux fichiers du runner                  |   ✓    |   ✗    |          ✓           |   ✓    |     ✓      |
| Support des jobs concurents sans configuration supplémentaire |   ✗    | ✗ (1)  |          ✓           |   ✓    |     ✓      |
| Environnements de build complexes                             |   ✗    | ✗ (2)  |          ✓           |   ✓    |     ✓      |
| Debug des problèmes des jobs                                  | facile | facile |      difficile       | moyen  |   moyen    |

[\[ref\]](https://docs.gitlab.com/runner/executors/#selecting-the-executor)

---

# 3. Intégration avec des outils externes

- [Gestion des environnements de déploiement](#31-gestion-des-environnements-de-déploiement)
- [Intégration de Terraform](#32-intégration-de-terraform)
- [Gestion des secrets avec Vault](#33-gestion-des-secrets-avec-vault)

---

# 3.1 Gestion des environnements de déploiement

Gitlab offre la possibilité de suivre les différents déploiements des applications sur différents environnements.

Cela permet d'avoir l'historique des déploiements sur les différents environnements, ainsi que permettre de suivre ce qui est déployé.

[\[ref\]](https://docs.gitlab.com/ee/ci/environments/)

---

## 3.1.a Création d'un déploiement

<div class="columns">
<div>

Pour créer un déploiement il est nécessaire d'associer le job ayant réalisé le déploiement sur un environnement à cet environnement, en utilisant le keyword `[job]:environment`.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/#environment)

</div>
<div>

```yaml
deploy app:
  environment: production
  script: echo "Deploying app"
```

Le lancement du job va créer un nouveau déploiement sur l'environnement en question.

</div>
</div>

---

## 3.1.a Création d'un déploiement

> ℹ️ **Note** : Si un job spécifie un environnement qui n'existe pas, cet environnement est créé au sein du projet.

> ℹ️ **Note** : L'implémentation du déploiement en lui même est laissé libre. Un projet peut vouloir déployer via Ansible tandis qu'un autre va déployer avec Flux ou ArgoCD sur un cluster Kubernetes.

---

## 3.1.b Visualisation des environnements

Les différents environnements actifs sont listés au sein de la page *Deployments > Environments*.

On y retrouve, pour chacun des environnements actifs, le dernier déploiement en date, ainsi que la possibilité d'agir dessus.

<img src="Attachements/Environnements/Interface/Env infos.png" width="80%" class="center" />

---

## 3.1.b Visualisation des environnements

Le clic sur un environnement permet d'afficher la liste des différents déploiements qui y ont eu lieu, ainsi que la possibilité d'un rollback sur ces différents déploiements.

<img src="Attachements/Environnements/Interface/Env details.png" width="80%" class="center" style="margin-top: 50px;" />

---

## 3.1.b Visualisation des environnements

Lorsque le job de déploiement vers un environnement est lancé dans une pipeline associée à une merge request, la page de résumé de la pipeline indique le lien vers le déploiement en question.

<img src="Attachements/Environnements/Interface/Merge request.png" width="80%" class="center" style="margin-top: 50px;" />

---

## 3.1.c Lien avec l'application déployée

<div class="columns">
<div>

En règle générale, les applications qui sont déployées sont accessibles par une URL via une navigateur.

Il est possible de lier un environnement à son URL, afin de faciliter l'accès à l'application déployée.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#environmenturl)

</div>
<div>

```yaml
deploy app:
  environment:
    name: production
    url: https://my-app.com
  script: echo "Deploying app"
```

</div>
</div>

---

## 3.1.c Lien avec l'application déployée

<img src="Attachements/Environnements/Interface/Env infos with link.png" width="80%" class="center" style="margin-top: 100px;"  />

---

## 3.1.c Lien avec l'application déployée

<img src="Attachements/Environnements/Interface/Env details with link.png" width="80%" class="center" style="margin-top: 50px;"  />

<img src="Attachements/Environnements/Interface/Merge request with link.png" width="80%" class="center" style="margin-top: 50px;" />

---

## 3.1.d Environnements dynamiques

Il est possible d'utiliser des variables dans les noms et URL des environnements. Ainsi, en utilisant des variables de CICD spécifiques à chaque pipeline, on peut créer des environnements dynamiques.

```yaml
deploy app:
  stage: deploy
  script: echo "Deploying app"
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_ENVIRONMENT_SLUG.example.com
  rules:
    - if: $CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH
```

---

## 3.1.e Arrêt d'un environnement

Durant le cycle de vie d'une application, on peut vouloir l'arrêter pour différentes raisons. Lorsque son déploiement est suivi par Gitlab, il est possible de définir un job réalisant l'arrêt de l'application.


Pour ce faire, il faut définir un job en charge d'effectuer l'arrêt, l'associer à l'environnement en question, indiquer qu'il est en charge de l'arrêt via le keyword `[job]:environment:action`, et en le liant au job chargé du déploiement avec `[jbo]:environment:on_stop`.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#environmenton_stop) [\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#environmentaction)

---

```yaml
deploy app:
  stage: deploy
  script:
    - echo "Deploy a review app"
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_ENVIRONMENT_SLUG.example.com
    on_stop: "stop app"

stop app:
  stage: deploy
  script:
    - echo "Remove review app"
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  when: manual
```

---

## 3.1.f Déploiement dans un cluster Kubernetes

Gitlab permet la connexion de clusters Kubernetes afin de réaliser la gestion d'applications déployées sur ces clusters directement via Gitlab.

Une fois le cluster connecté, il est possible d'utiliser des versionner les manifests des applications à déployer et utiliser les pipelines CICD Gitlab pour gérer leur cycle de vie.

---

## Exercices

- [Exercice 12](https://gitlab.com/bastien-antoine/orness/formation-gitlab/exercises/-/tree/ex12)

---

# 3.2 Intégration de Terraform

Terraform est un outil permettant de gérer de l'infrastructure à travers différents fichiers de configuration. Ce fonctionnement permet de mettre en place ce qu'on appelle de l'*Infrastructure as code*.

Pour pouvoir correctement fonctionner, terraform s'appuie, entre autres, sur le fichier de state qui lui permet de stocker une référence et suivre l'état de l'infrastructure. Lorsque plusieurs personnes travaillent sur la même infrastructure, il leur faut un moyen de pouvoir travailler avec la même référence.

---

# 3.2 Intégration de Terraform

Terraform propose la possibilité de stocker le state sur des espaces distants afin que plusieurs personnes puissent travailler ensemble sur la même infrastructure.

Gitlab permet le stockage et la gestion du state au sein de chaque projet.

---

## 3.2.a Stockage du state sur Gitlab

Aucune config particulière n'est à faire côté Gitlab.

Côté Terraform, il faut configurer le backend remote :
```diff
terraform {
+  backend "http" {
+    address = "https://gitlab.com/api/v4/projects/<project ID or path>/terraform/state/<state name>"
+    username = "<username>"
+    password = "<personal access token>"
+  }
}
```

---

## 3.2.a Stockage du state sur Gitlab

Il est possible d'omettre les paramètres, mais dans ce cas il sera nécessaire de les fournir à l'initialisation du backend [\[ref\]](https://docs.gitlab.com/ee/user/infrastructure/iac/terraform_state.html#set-up-the-initial-backend) :
```shell
PROJECT_ID="<project ID or path>"
TF_USERNAME="<username>"
TF_PASSWORD="<personal access token>"
TF_ADDRESS="https://gitlab.com/api/v4/projects/${PROJECT_ID}/terraform/state/<state name>

terraform init \
  -backend-config=address=${TF_ADDRESS} \
  -backend-config=lock_address=${TF_ADDRESS}/lock \
  -backend-config=unlock_address=${TF_ADDRESS}/lock \
  -backend-config=username=${TF_USERNAME} \
  -backend-config=password=${TF_PASSWORD} \
  -backend-config=lock_method=POST \
  -backend-config=unlock_method=DELETE \
  -backend-config=retry_wait_min=5
```

---

## 3.2.a Stockage du state sur Gitlab

Côté CICD, il est possible d'utiliser une image dédiée contenant un script helper facilitant l'utilisation de Terraform :

`registry.gitlab.com/gitlab-org/terraform-images/releases/1.4:v1.0.0`

La configuration de l'authentification à l'API de gestion des states est faite automatiquement via la variable `$CI_JOB_TOKEN`.

[\[ref\]](https://docs.gitlab.com/ee/user/infrastructure/iac/gitlab_terraform_helpers.html)

---

```yaml
image:
  name: "$CI_TEMPLATE_REGISTRY_HOST/gitlab-org/terraform-images/releases/1.4:v1.0.0"
variables:
  TF_ROOT: "${CI_PROJECT_DIR}"
  TF_STATE_NAME: default
cache:
  key: "${TF_ROOT}"
  paths:
  - "${TF_ROOT}/.terraform/"

stages:
- build
- deploy

build:
  stage: build
  script:
  - gitlab-terraform plan
  - gitlab-terraform plan-json
  artifacts:
    paths:
    - "${TF_ROOT}/plan.cache"
    reports:
      terraform:
      - "${TF_ROOT}/plan.json"
```

---

## 3.2.b Intégration de la planification Terraform

Parmi les nombreux types de rapports extraits d'artifacts de jobs que Gitlab est capable de gérer, il y a les plans Terraform.

Si un job génère un plan Terraform lors d'une pipeline associée à une merge request, Gitlab peut afficher le résultat de la planification de Terraform au sein de la merge request.

[\[ref\]](https://docs.gitlab.com/ee/ci/yaml/artifacts_reports.html#artifactsreportsterraform)

<img src="Attachements/Terraform%20report.png" width="80%" class="center" style="margin-top: 10px;" />

---

## 3.2.b Intégration de la planification Terraform

```yaml
plan:
  stage: build
  image: alpine
  script:
    - apk --no-cache add jq terraform
    - alias convert_report='jq -r ...'
    - terraform init
    - terraform plan -out=plan.cache
    - terraform show --json plan.cache | convert_report > plan.json
  artifacts:
    reports:
      terraform: plan.json
```

---

# 3.3 Gestion des secrets avec Vault

Vault est un outil développé par Hashicorp pour gérer des secrets et données sensibles.

Pour pouvoir récupérer des données stockées dans Vault depuis l'extérieur, il faut s'authentifier, et donc avoir un jeu de credentials.

---

# 3.3 Gestion des secrets avec Vault

Si l'idée d'utiliser Vault pour ne plus stocker aucune donnée sensible dans les variables de CICD, la nécessité de stocker des credentials pour pouvoir accéder aux secrets de Vault est un peu contradictoire.

Il est possible d'utiliser un JWT généré par Gitlab pour s'authentifier auprès de Vault, et pouvoir ensuite récupérer les credentials.

[\[ref\]](https://docs.gitlab.com/ee/ci/secrets/)

---

## 3.3.a Mécanisme d'authentification

<div class="columns">
<div>

Lors de la préparation d'un job, Gitlab va fournir un JWT dédié pour le job (`$CI_JOB_JWT`) , avec des informations sur le job en question, et son contexte.

Il est possible de s'authentifier sur Vault avec un JWT. Ainsi on peut, dans la CICD, utiliser ce JWT pour s'authentifier, et par la suite récupérer des données sensibles.

</div>
<div>

```json
{
  "jti": "c82eeb0c-5c6f-4a33-abf5-4c474b92b558",
  "iss": "gitlab.example.com",
  "iat": 1585710286,
  "nbf": 1585798372,
  "exp": 1585713886,
  "sub": "job_1212",
  "namespace_id": "1",
  "namespace_path": "mygroup",
  "project_id": "22",
  "project_path": "mygroup/myproject",
  "user_id": "42",
  "user_login": "myuser",
  "user_email": "myuser@example.com",
  "pipeline_id": "1212",
  "pipeline_source": "web",
  "job_id": "1212",
  "ref": "auto-deploy-2020-04-01",
  "ref_type": "branch",
  "ref_path": "refs/heads/auto-deploy-2020-04-01",
  "ref_protected": "true",
  "environment": "production",
  "environment_protected": "true"
}
```
</div>
</div>

---

## 3.3.a Mécanisme d'authentification

Côté Vault, on peut restreindre l'accès à des espaces selon des informations contenues dans le JWT. Il est possible, par exemple, de restreindre l'accès à l'espace `my-project/production` aux JWT émis au sein du projet `my-group/my-project`, soit ceux dont `JWT['project_path'] = "mygroup/myproject"`.

---

## 3.3.a Mécanisme d'authentification

<img src="Attachements/Vault/Vault%201.svg" width="50%" class="center" style="margin-top: 20px;" />

---

## 3.3.a Mécanisme d'authentification

<img src="Attachements/Vault/Vault%202.svg" width="50%" class="center" style="margin-top: 20px;" />

---

## 3.3.a Mécanisme d'authentification

<img src="Attachements/Vault/Vault%203.svg" width="50%" class="center" style="margin-top: 20px;" />

---

## 3.3.a Mécanisme d'authentification

<img src="Attachements/Vault/Vault%204.svg" width="50%" class="center" style="margin-top: 20px;" />

---

## 3.3.a Mécanisme d'authentification

<img src="Attachements/Vault/Vault%205.svg" width="50%" class="center" style="margin-top: 20px;" />

---

## 3.3.a Mécanisme d'authentification

<img src="Attachements/Vault/Vault%206.svg" width="50%" class="center" style="margin-top: 20px;" />

---

## 3.3.a Mécanisme d'authentification

<img src="Attachements/Vault/Vault%207.svg" width="50%" class="center" style="margin-top: 20px;" />

---

## 3.3.a Mécanisme d'authentification

> ℹ️ **Note** : L'utilisation des JWT via la variables `$CI_JOB_JWT` est dépréciée et est prévue d'être remplacée par les ID token pour permettre l'utilisation d'OpenID Connect.

---

## 3.3.b Utilisation des ID tokens pour l'authentification à des services externes

Le problème de stockage de credentials au sein des variables de CICD est assez courant, et n'est pas limité qu'à Vault.

Dès lors qu'un job souhaite utiliser un service extérieur nécessitant de l'authentification, il est nécessaire de stocker quelque part accessible par le job les données nécessaires à l'authentification.

---

## 3.3.b Utilisation des ID tokens pour l'authentification à des services externes

Certains services permettent de s'authentifier à l'aide de token JWT, et plus précisément en utilisant des ID tokens et le mécanisme OpenID Connect.

Gitlab peut générer ces ID tokens, et permettre l'authentification à différents services, comme AWS, GCP ou Azure.

[\[ref\]](https://docs.gitlab.com/ee/ci/cloud_services/index.html) [\[ref\]](https://docs.gitlab.com/ee/ci/yaml/index.html#id_tokens)

---

<div style="text-align: center; margin-top: 220px;">

## Des questions ?

</div>

---

<div style="text-align: center; margin-top: 220px;">

## Merci !

</div>

---

