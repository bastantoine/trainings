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

<img src="../Attachements/Terraform%20report.png" width="80%" class="center" style="margin-top: 10px;" />

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
