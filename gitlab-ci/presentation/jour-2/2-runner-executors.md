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