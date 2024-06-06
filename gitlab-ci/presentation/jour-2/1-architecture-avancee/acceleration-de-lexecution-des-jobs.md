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

<img src="../Attachements/Cache/Cache%201.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="../Attachements/Cache/Cache%202.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="../Attachements/Cache/Cache%203.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="../Attachements/Cache/Cache%204.svg" width="70%" class="center" />

---

### Stockage du cache

<img src="../Attachements/Cache/Cache%205.svg" width="70%" class="center" />

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

<img src="../Attachements/Parallel%20matrix/Parallel%20matrix%201.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="../Attachements/Parallel%20matrix/Parallel%20matrix%202.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="../Attachements/Parallel%20matrix/Parallel%20matrix%203.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="../Attachements/Parallel%20matrix/Parallel%20matrix%204.svg" width="85%" style="margin-top: 70px;" class="center" />

---

## 1.1.b Parallélisation des jobs

<img src="../Attachements/Parallel%20matrix/Parallel%20matrix%205.svg" width="85%" style="margin-top: 70px;" class="center" />


