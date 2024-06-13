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
