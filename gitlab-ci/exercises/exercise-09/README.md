# Exercices de la formation Gitlab CI

## Scénario

Les différents exercices vont vous placer dans la peau d'un ingénieur DevOps chargé de mettre en place une chaine de CICD à l'aide de Gitlab CICD pour une petite application (désolé si ça vous rappelle des souvenirs du travail 😇).

## Application

L'application utilisée pour les exercices est une API toute simple faite en Python à l'aide de Flask.

Le code source de l'application est disponible dans le dosser `accounting/`.

Quelques tests sont présents et utilisent le framework `pytest`. Ils sont disponibles dans le dossier `tests/`.

### Préparation de l'environnement

Un fichier `requirements.txt` est disponible pour créer un environnement virtuel Python. Les dépendances sont valides pour Python >= 3.8.

Pour préparer l'environnement :

```shell
python3 -m venv .venv

# Ne pas oublier d'activer l'environnement virtuel (ie. utiliser le Python de cet environnement au lieu de celui de la machine)
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Lancement de l'application

Pour lancer l'application Flask :

```shell
source .venv/bin/activate
export FLASK_APP=accounting.app:setup_app
flask run --debug
```

## Exercice 1

Vous avez été missionné pour mettre en place de manière progressive une chaine de CICD pour une application.

La première tâche qu'on vous a confié est de faire en sorte que l'ensemble des tests unitaires soit lancés de manière automatique à chaque fois que quelqu'un push un changement sur le projet.

### Notes pour la mise en place de la CICD

Les tests utilisent le framework `pytest` pour fonctionner.

Pour les faire lancer, il faut dans un premier temps **s'assurer d'être dans un environnement virtuel Python activé** avec les **dépendances du projet d'installées**. Voir section `Préparation de l'environnement` ci-dessus pour les commandes nécessaires à l'installation.

Pour lancer les tests, **il suffit de lancer la commande `pytest` à la racine du projet** :

```shell
> pytest

=================== test session starts ===================
platform linux -- Python 3.11.3, pytest-7.3.1, pluggy-1.0.0
rootdir: ...
configfile: pytest.ini
plugins: cov-4.1.0
collected 4 items

tests/test_expenses.py ..                            [ 50%]
tests/test_incomes.py ..                             [100%]

=================== 4 passed in 0.17s =====================
```

Une **image Docker avec Python >= 3.8 est nécessaire** afin de faire tourner le job.

Vous pouvez prendre n'importe laquelle, les images officielles conviennent parfaitement :
- `python:3.8`
- `python:3.9`
- `python:3.10`
- `python:3.11`

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

## Exercice 2

La tâche suivante est de mettre en place des contrôles de qualité du code de l'application (aka du lint).

Vous avez décidé d'utiliser [`flake8`](https://flake8.pycqa.org/en/latest/) pour contrôler le code produit.

### Notes pour la mise en place de la CICD

Le job nécessite Python >= 3.8 pour fonctionner. Il faut dans un premier temps **s'assurer d'être dans un environnement virtuel Python activé** avec les **dépendances du projet d'installées**. Voir section `Préparation de l'environnement` ci-dessus pour les commandes nécessaires à l'installation.

`flake8` n'est pas présent dans les dépendances du projet telles qu'elles sont indiquées dans le `requirements.txt`. Il faut donc l'installer au préalable dans le job avant de pouvoir l'utiliser :
```shell
pip install flake8
```

Pour lancer le lint, **il suffit de lancer la commande `flake8` en indiquant le dossier à analyser** :

```shell
> flake8 accounting
accounting/model/income.py:11:80: E501 line too long (81 > 79 characters)
```

Une **image Docker avec Python >= 3.8 est nécessaire** afin de faire tourner le job.

Vous pouvez prendre n'importe laquelle, les images officielles conviennent parfaitement :
- `python:3.8`
- `python:3.9`
- `python:3.10`
- `python:3.11`

> **Note :** Dans l'état actuel du code, le job lançant `flake8` sera probablement en échec, dû à une erreur de mise en forme dans le code. **C'est normal.**

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible à l'exercice précédent. Ne pas hésiter à adapter la solution à ce que vous avez produit à l'exercice précédent.

> **Note :** flake8 doit normalement remonter une erreur au sein du fichier `accounting/model/income.py`. Il peut être nécessaire de corriger cette erreur afin que ce job ne bloque plus les pipelines futures.
>
> ```diff
>   # accounting/model/income.py
>   class Income(Transaction):
>       def __init__(self, description: str, amount: str):
> -         super(Income, self).__init__(description, amount, TransactionType.INCOME)
> +         super(Income, self).__init__(
>               description,
>               amount,
>               TransactionType.INCOME,
>           )
> ```

## Exercice 3

Après quelques temps d'utilisation de la pipeline que vous avez mis en place, vous avez eu quelques retours qui nécessitent que vous l'adaptiez un peu :
1. Le job de lint du code qui est bloquant est un peu contraignant
2. C'est assez lourd de lancer tous les tests à chaque action effectuées sur le projet.

Voici ce qui a été décidé :
1. Ces deux jobs ne doivent être **lancés que quand la pipeline est lancée pour une branche différente de la branche principale et qui a au moins une merge request d'ouverte associée**. Il a été estimé que le process de vérification du code et de protection des différentes branches autorisait de ne lancer les tests que sur les branches avant de merger sur la branche principale.
2. Le job de lint du code **ne doit plus être bloquant**

### Notes pour la mise en place de la CICD

Pour faire en sorte qu'un job ne soit ajouté que lorsque sa pipeline est associée à une branche donnée, il faut **ajouter une règle sur la valeur de la variable `CI_COMMIT_BRANCH`**. On peut récupérer le **nom de la branche par défaut dans la variable `CI_DEFAULT_BRANCH`**.

Il est également possible de récupérer une **liste des merge requests associées à la branche en question via la variable `CI_OPEN_MERGE_REQUESTS`**.

Un job non bloquant est un job dont le résultat (succès ou échec) n'influe pas sur le résultat final de la pipeline. Autrement dit c'est un **job qui est autorisé à terminer en échec**.

Tous ces paramètres se **contrôlent via les [`rules`](https://docs.gitlab.com/ee/ci/yaml/#rules)** du job.

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible aux exercices précédents. Ne pas hésiter à adapter la solution à ce que vous avez produit aux exercices précédents.

**Quelques explications :**

La règle, identique au deux jobs, se découpe en 3 parties :
- `$CI_COMMIT_BRANCH`: ici on ne souhaite ajouter le job que dans le cas d'une pipeline lancée pour une branche. La documentation nous indique : *Available in branch pipelines, including pipelines for the default branch. Not available in merge request pipelines or tag pipelines*.
- `$CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH`: la documentation de la variable précédente nous indique que celle-ci est définie aussi pour les pipelines lancées pour la branche par défaut. Comme on ne souhaite lancer ces jobs que pour les branches autres que celle par défaut, il faut filtrer sur le nom de la branche.
- `$CI_OPEN_MERGE_REQUESTS`: on souhaite de plus ne lancer que les jobs pour les branches qui ont au moins une merge request associée. la documentation de cette variable nous indique: *A comma-separated list of up to four merge requests that use the current branch and project as the merge request source. For example, gitlab-org/gitlab!333,gitlab-org/gitlab-foss!11.*. Ici on est pas intéressé par le(s) merge request(s) associée(s), seulement savoir s'il y en a.

## Exercice 4

Place au déploiement ! Votre application se modernise et il vous faut maintenant la conteneuriser dans une image Docker. On vous a fourni un Dockerfile qui encapsule votre application et ses dépendances, il faut maintenant mettre en place un job qui va builder votre image et la pousser sur une registry.

Les règles pour la mise en place du job de build sont les suivantes:
- Si la **pipeline est lancée sur une branche différente de la branche par défaut, et à laquelle est associée au moins une merge request** d'ouverte, alors il faut **seulement builder l'image, et ne pas la pousser sur la registry**.
- Si la **pipeline est lancée sur la branche par défaut**, il faut **builder l'image et la pousser sur la registry**.

### Notes pour la mise en place de la CICD

Pour effectuer le build de notre image, il nous faut un outil capable de construire des images Docker. Comme notre job tourne déjà au sein d'un conteneur Docker, il nous faut un outil qui soit capable de le faire dans ce contexte.

Plusieurs possibilités :
- [*"Docker-in-docker" (`dind`)*](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html#use-docker-in-docker)
- [kaniko](https://docs.gitlab.com/ee/ci/docker/using_kaniko.html)

Nous allons utiliser la deuxième méthode.

Pour utiliser kaniko au sein d'un job Gitlab CI, il faut **utiliser une image dédiée** :

```yaml
build:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.9.0-debug
    entrypoint: [""]
  script: ...
```

**La commande à lancer est la suivante** :
```bash
/kaniko/executor
  --context "${CI_PROJECT_DIR}"
  --dockerfile "${CI_PROJECT_DIR}/Dockerfile"
  --destination "${CI_REGISTRY_IMAGE}:${CI_COMMIT_TAG}"
```

> **Note :** cette exercice utilise la fonctionalité de [registry de conteneur intégrée à Gitlab](https://docs.gitlab.com/ee/user/packages/container_registry/index.html). L'offre SaaS communautaire (ie. [gitlab.com](https://gitlab.com) gratuit) a une limite de 5 Go de stockage total par utilisateur. Les images stockées sur la registry de conteneurs comptent dans le calcul de cette limite. **Pensez à supprimer les images si vous atteignez les limites de l'offre**.

Par défaut, kaniko va construire l'image et la pousser vers la registry indiquée. **Si on ne veut pas pousser l'image, il faut rajouter l'option `--no-push`**.

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible aux exercices précédents. Ne pas hésiter à adapter la solution à ce que vous avez produit aux exercices précédents.

**Quelques explications :**

On souhaite ajouter notre job de build dans deux cas, on a donc deux règles :
1. `if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH`: ici on souhaite ajouter le job lorsque la pipeline est lancée sur la branche par défaut
2. `if: $CI_COMMIT_BRANCH && $CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH && $CI_OPEN_MERGE_REQUESTS`:
  - Le cas est le même que pour l'exercice précédent, voir ci-dessus pour une explication détaillée de la règle
  - Dans ce cas, on souhaite uniquement construire l'image et ne pas la pousser vers la registry. On peut définir une variable qui va contenir l'option `--no-push` et qui ne sera définie que dans ce cas. Ainsi dans le cas de la règle 1., la variable ne sera pas définie, et sera donc remplacée par une string vide avant l'execution de la commande.

## Exercice 5

Votre image est construite, il est maintenant temps de la déployer. Vous faîtes les choses bien et vous la déployez sur 3 environnement distincts : dev, recette et prod, via un commit sur 3 branches distinctes, `deploy/dev`, `deploy/rct` et `deploy/prd`.

Il faut donc rajouter 3 jobs pour procéder au déploiement.

Les règles pour ces jobs de déploiements sont les suivants:
- Le job de déploiement dans un environnement donné ne doit être ajouté que dans le cas où la pipeline est lancée pour sa branche (ie. `deploy/dev` pour déployer en dev...). Le job ne doit pas être ajouté dans les autres cas.
- Le déploiement sur l'environnement de production ne doit pas être automatique.
- Le déploiement nécessite des variables `DEPLOY_USER` et `DEPLOY_TOKEN`. Ces variables ne doivent pas être visibles dans la config de la CI ni dans les logs.
- Le push des images Docker doit être autorisé pour les pipelines lancées pour une de ces 3 branches.

### Notes pour la mise en place de la CICD

Un déploiement non automatique est un **déploiement manuel**. Ce paramètre se **contrôle via les [`rules`](https://docs.gitlab.com/ee/ci/yaml/#rules)** du job.

Pour faire en sorte que des variables ne soient pas visibles dans le fichier de config, il faut qu'elles soient définies comme variable de CI au sein du projet : `[mon projet] > Settings > CI/CD > Variables > Add variable`

> **Note :** bien penser à décocher *Protect variable* lors de la création des variables

Il est également possible de marquer une variable comme sensible afin qu'elle ne soit pas affichée dans les logs des jobs.

Pour ces jobs, il n'y a pas de déploiement réel mis en place, vous pouvez simplement faire un `echo "Deploying to <my env>"` pour simuler l'action.

Vous pouvez également ajouter une ligne `echo "Using credentials $DEPLOY_USER with token $DEPLOY_TOKEN"` pour vous assurer que la valeur est correctement masquée dans les logs.

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible aux exercices précédents. Ne pas hésiter à adapter la solution à ce que vous avez produit aux exercices précédents.

**Quelques explications :**

Chacune des rules des jobs de déploiements sont similaires, à la seule exception de la règle pour la production qui a en plus `when: manual` pour permettre le lancement du job uniquement à la main.

Deux variables de CI, `DEPLOY_USER` et `DEPLOY_TOKEN`; ont été créées dans le projet, toutes deux marqués comme masquée.

3 nouvelles règles ont été rajoutées au job de build Docker, pour permettre le build et push pour les 3 nouvelles branches. À noter qu'il aurait été possible de regrouper les 4 dernière règles au sein d'une même rule, puisque leur impact sur l'ajout du job est identique. Néanmoins elles ont été séparées pour des soucis de lisibilité.

```yaml
job:
  stage: stage
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_BRANCH == "deploy/dev"
    - if: $CI_COMMIT_BRANCH == "deploy/rct"
    - if: $CI_COMMIT_BRANCH == "deploy/prod"
  script: ...

# équivalent

job:
  stage: stage
  rules:
    - if: ($CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH) || ($CI_COMMIT_BRANCH == "deploy/dev") || ($CI_COMMIT_BRANCH == "deploy/rct") || ($CI_COMMIT_BRANCH == "deploy/prod")
  script: ...
```

## Exercice 6

L'application dont vous avez la charge est une API REST, elle fourni donc un [swagger](https://swagger.io/specification/v3/). On vous a donné comme tâche de trouver une manière de s'assurer que le swagger généré est de bonne qualité et respecte la norme (aka du lint).

Vous avez trouvé [spectral](https://stoplight.io/open-source/spectral), un outil en CLI qui semble pouvoir répondre au besoin.

Les contraintes pour mettre en place ce job sont les suivantes :
- Ce job de contrôle de la qualité du swagger **ne doit pas être bloquant**.
- Ce job doit être **lancé dans les mêmes conditions que le job de lint précédent**.
- Pour pouvoir lancer le linter, **il faut avoir généré le swagger de l'API au préalable**, via la commande `FLASK_APP=accounting.app:setup_app flask swagger > swagger.json`.

### Notes pour la mise en place de la CICD

> **Note :** le fichier `.spectral.yaml`, nécessaire au bon fonctionnement de Spectral a été rajouté. Bien penser à le récupérer

Pour pouvoir utiliser la CLI `spectral`, **il faut utiliser une image Docker qui contient cet outil** :

```yaml
lint:
  stage: lint
  image:
    name: stoplight/spectral
    entrypoint: [""]
  script: ...
```

Ensuite il suffit de **lancer la commande `spectral lint swagger.json`**, `swagger.json` étant un fichier contenant le swagger de l'API généré au préalable.

Pour pouvoir générer le swagger, il faut lancer une commande via l'application Flask (voir au dessus pour la commande à lancer). Cela veut donc dire qu'**il faut un environnement Python avec les dépendances de l'application d'installées**.

Il est **recommandé de faire un job séparé qui se base sur Python pour générer le swagger**, le stocker dans un fichier `swagger.json`, et **le transmettre au job de lint via un artefact**.

Il serait techniquement possible de tout faire dans un seul job, mais ça nécessite soit d'installer Python dans l'image contenant spectral, soit d'installer la CLI dans une image Python.

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible aux exercices précédents. Ne pas hésiter à adapter la solution à ce que vous avez produit aux exercices précédents.

**Quelques explications :**

Ici on se retrouve avec deux stages qui ont les mêmes règles d'ajout à la pipeline que les autres.

L'utilisation de deux stages séparés permet de se simplifier la vie dans la préparation du job. On se base sur une image Python pour le job nécessitant de générer le swagger puisqu'on a besoin de Flask, et on se base sur une image contenant notre outil CLI pour pouvoir effectuer l'analyse.

La transmission du fichier `swagger.json` entre les deux jobs se fait via un artifact déclaré au niveau du job générant ce fichier.

> **Note :** la solution proposée ajoute dans le job de lint une dépendances au job de génération du swagger. Cette pratique fait le job de lint du swagger ne va récupérer que les artifacts de ce job là, et aucun autre. En l'occurence ici ça n'a pas d'impact, puisqu'au autre job précédent ne génère d'artifact.

## Exercice 7

Afin d'améliorer la vie des développeurs de votre application, vous avez découvert qu'il est possible de récolter les résultats des tests Python et de les afficher dans les merge requests.

Vous découvrez qu'il est aussi possible de récupérer, via les tests, des informations sur la couverture du code.

En explorant la documentation de `spectral`, vous vous apercevez que cet outil peut générer des rapports similaires aux rapports des tests Python, et qui peuvent donc être affichés dans une merge request.

### Notes pour la mise en place de la CICD

Afin de pouvoir générer les rapports de tests avec pytest, il faut **rajouter l'option `--junitxml=report.xml`** à la commande de lancement des tests. Cette option va **générer un fichier `report.xml` au format JUnit**.

Pour générer le rapport de couverture, **il faut au préalable installer le package `pytest-cov`**. Il n'est pas nécessaire de rajouter cette dépendances dans le fichier `requirements.txt`, il suffit de l'installer dans le job.

Pour générer ce rapport, il faut ensuite rajouter quelques options à la commande de lancement des tests : **`--cov --cov-report term --cov-report xml:coverage.xml`**. Un **fichier `coverage.xml` sera généré au format Cobertura**.

La **commande complète à lancer est donc `pytest --junitxml=report.xml --cov --cov-report term --cov-report xml:coverage.xml`**.

Ces deux fichiers doivent être **identifiés comme des rapports**, un de test et un de couverture, dans la [section des artifacts](https://docs.gitlab.com/ee/ci/yaml/#artifacts) du job.

Pour générer le rapport au format JUnit pour spectral, **il faut rajouter l'option `-f stylish -f junit --output.junit report.xml`**

La commande totale est donc `spectral lint swagger.json -f stylish -f junit --output.junit report.xml`

Cette option va **générer un fichier `report.xml` au format JUnit** qui pourra être **marqué comme un rapport de tests dans les artifacts du job**.

> **Note :** l'option `-f stylish` permet de continuer d'afficher le résultat des tests dans les logs du job

> **Note :** pour pouvoir tester le résultat de la CI, il faut créer une branche et une merge request associée. Les rapports seront affichés dans l'interface de la merge request

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible aux exercices précédents. Ne pas hésiter à adapter la solution à ce que vous avez produit aux exercices précédents.

## Exercice 8

Avant de rajouter des éléments nouveaux dans votre pipeline, il va falloir la simplifier pour éviter de la redondance et faciliter sa maintenance.

### Notes pour la mise en place de la CICD

Quelques propositions de simplifications possibles à appliquer sur le fichier de configuration :

- Plusieurs jobs ont une même règles conditionnant leut ajout à la pipeline, il est donc possible d'u**tiliser un job caché définissant la règle, et faire en sorte que tous les jobs qui en ont besoin héritent de ce job**.
- La majorité des jobs utilisent la même image pour fonctionner : `python:3.11`. Il serait **possible de la définir comme image par défaut** pour toute la pipeline.
- Les scripts des 3 jobs simulant un déploiement sont très similaires. Là aussi on pourrait **faire en sorte que ces 3 jobs héritent d'un job caché avec le script de déploiement**.

> **Note :** La définition du fichier de config CICD de Gitlab fait que tous les mapping définis à la racine du fichier sont tous considérés comme des définitions de job (sauf pour [quelques exceptions](https://docs.gitlab.com/ee/ci/yaml/#keywords)). Cette contrainte fait que si un mapping défini à la racine a certains de ses attributs requis manquant, Gitlab indiquera une erreur de syntaxe dans le fichier, et refusera de lancer la moindre pipeline.
>
> Ce point fait que si on veut définir des configurations réutilisables au sein de notre fichier de config, il faut faire en sorte que Gitlab ne les considère pas comme des jobs. Pour cela on peut ***"cacher"* le job : il suffit de mettre un point `.` au début de son nom**.
>
> Ainsi la config suivante est invalide puisqu'il manque un script.
> ```yaml
> my-job:
>   image: python
> ```
>
> Le YAML suivant est accepté par Gitlab, et ne produit aucun job :
> ```yaml
> .my-job:
>   image: python
>
> my-job:
>  extends: .my-job
>  script: echo
> ```
> [\[ref\]](https://docs.gitlab.com/ee/ci/jobs/#hide-jobs)

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

Il peut sembler que la factorisation proposée rajoute plus de lignes de config que ce qu'elle enlève ([...](https://i.giphy.com/media/9MJ6xrgVR9aEwF8zCJ/giphy.webp)). L'idée derrière cette opération n'est pas nécessairement d'avoir moins de lignes, mais surtout de faciliter la maintenabilité du fichier.

Si demain, l'image de base venait à changer pour passer de `python:3.11` à `python:3.12`, le fait d'avoir défini cette image comme image par défaut fait qu'il n'y aurait qu'un seul endroit à change.

De même si les règles d'ajout des jobs à la pipeline évoluent, il sera assez facile de les changer à un seul endroit.

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible aux exercices précédents. Ne pas hésiter à adapter la solution à ce que vous avez produit aux exercices précédents.

## Exercice 9

Après analyse, vous remarquez que les jobs utilisant Python passent une bonne partie de leur temps à préparer leur environnement et installer les dépendances. Afin d'accélérer leur exécution, vous décider de rajouter un job qui sera en charge de préparer un environnement Python avec les dépendances d'installées et de le mettre à disposition des autres jobs via le cache.

### Notes pour la mise en place de la CICD

pip, le gestionnaire de dépendances de Python, installe les packages téléchargés au sein d'un dossier de cache. Pour pouvoir correctement mettre en cache les dépendances de notre environnement, il faut que ce dossier soit au présent dans le dossier courant de notre job (identifié par la variable `$CI_PROJECT_DIR`). Pour indiquer l'emplacement du dossier que pip peut utiliser pour le cache, on peut utiliser la variable `PIP_CACHE_DIR`.

On aura donc **`PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"`**. On peut définir cette **variable comme globale à toute la pipeline** afin que tous les jobs utilisant du Python y aient accès.

Le **dossier à indiquer pour la définition de notre cache est donc `$CI_PROJECT_DIR/.cache/pip`** (ou simplement `.cache/pip` puisque notre cache est nécessairement présent au sein de `$CI_PROJECT_DIR`).

Afin de faire en sorte que notre cache soit automatiquement invalidé, et donc regénéré, lorsqu'on rajoute de nouvelles dépendances, la **clé du cache doit être calculée à l'aide du fichier `requirements.txt`**.

La configuration du cache se fait à l'aide du keyworkd [`[job]:cache`](https://docs.gitlab.com/ee/ci/yaml/#cache).

L'installation des dépendances et la création du cache doit se faire **dans un job dédié exécuté dans un stage antérieur aux jobs qui ont besoin de l'environnement Python**.

### Solution proposée

Une solution possible à la tâche demandée est proposée dans le fichier `.gitlab-ci-solution.yml`

On a bien un job supplémentaire, dans un stage supplémentaire `prepare` ajouté avant les stages de `test` et `code quality` où des jobs ayant besoin du cache sont présent.

On a deux définitions du cache, très similaire l'une de l'autre :
- La clé du cache est calculée à partir du fichier `requirements.txt`
- Le dossier associé au cache est bien `.cache/pip`

Un détail différencie les deux définitions :
1. La première définition n'indique aucune politique de récupération et mise à jour du cache, ce qui veut dire qu'elle utilise la valeur par défaut `pull-push`. Cette politique signifie d'essayer de récupérer le cache au lancement, et le mettre à jour à la fin si besoin.
2. La deuxième définition indique `policy: pull`, ce qui signifie que le job va uniquement essayer de récupérer le cache, mais ne jamais le mettre à jour.
  - Cette politique est très pratique pour les jobs qui ont besoin d'une dépendances particulière, comme par exemple le job de lint. Ce job utilise `flake8`, qui est donc installé au début du job. Avec la politique `policy: pull`, on évite de changer le cache avec cette nouvelle dépendances qui ne sera pas utile pour les autres jobs.

> **Note :** Le fichier est nommé ainsi afin qu'il ne soit pas executé automatiquement par Gitlab lors des différentes actions effectuée sur le projet.

> **Note :** Ce fichier contient aussi une solution possible aux exercices précédents. Ne pas hésiter à adapter la solution à ce que vous avez produit aux exercices précédents.

