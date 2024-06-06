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

<img src="../Attachements/Service%20name%20aliases.svg" width="70%" class="center" style="margin-top: 10px;" />

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