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

  img.center {
    display: block;
    margin: 0 auto;
  }
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

<img src="../Attachements/Environnements/Interface/Env infos.png" width="80%" class="center" />

---

## 3.1.b Visualisation des environnements

Le clic sur un environnement permet d'afficher la liste des différents déploiements qui y ont eu lieu, ainsi que la possibilité d'un rollback sur ces différents déploiements.

<img src="../Attachements/Environnements/Interface/Env details.png" width="80%" class="center" style="margin-top: 50px;" />

---

## 3.1.b Visualisation des environnements

Lorsque le job de déploiement vers un environnement est lancé dans une pipeline associée à une merge request, la page de résumé de la pipeline indique le lien vers le déploiement en question.

<img src="../Attachements/Environnements/Interface/Merge request.png" width="80%" class="center" style="margin-top: 50px;" />

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

<img src="../Attachements/Environnements/Interface/Env infos with link.png" width="80%" class="center" style="margin-top: 100px;"  />

---

## 3.1.c Lien avec l'application déployée

<img src="../Attachements/Environnements/Interface/Env details with link.png" width="80%" class="center" style="margin-top: 50px;"  />

<img src="../Attachements/Environnements/Interface/Merge request with link.png" width="80%" class="center" style="margin-top: 50px;" />

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