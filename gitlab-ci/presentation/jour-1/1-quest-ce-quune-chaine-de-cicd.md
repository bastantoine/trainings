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

# 1. Qu'est-ce qu'une chaine de CICD ?

- [Définition](#11-définition)
- [Les principes clés](#12-les-principes-clés)
- [Les outils à disposition](#13-les-outils-à-disposition)
- [Gitlab](#14-gitlab)

---

# 1.1 Définition

<div class="columns">
<div>

La CI/CD est une méthode **automatisée** de développement et de déploiement d'applications qui **vise à améliorer l'efficacité et la fiabilité du processus** en **intégrant régulièrement le code** et en **automatisant le déploiement** dans les différents environnements.

</div>
<div>

<img src="https://gotestr.com/wp-content/uploads/2022/09/cicd-gotestr.png" class="center" style="position: relative; top: 30%; width: 100%;" />

</div>

---

# 1.2 Les principes clés

1) Automatisation
2) Amélioration continue
3) Intégration continue
4) Déploiement continu
5) Gestion de version

---

# 1.3 Les outils à disposition

<div class="columns">
<div>

Un grand nombre d'outils permettent de mettre en place des chaines de CICD.

Certains proposent uniquement des fonctionnalités de CICD, tandis que d'autres intégrent les fonctionnalités de CICD au sein d'une plateforme de développement logiciel plus complète.

</div>
<div>

- Jenkins
- Circle CI
- Travis CI
- Azure Pipelines
- Github Actions
- Gitlab CICD
- ...

</div>

---

# 1.4 Gitlab

Gitlab est une plateforme de développement logiciel intégrant toutes les étapes de développement logiciel, depuis la conception et la planification, jusqu'à la livraison, en passant par le développement collaboratif du code et la gestion des incidents.

Gitlab est disponibles sous plusieurs offres et versions :
- Saas ([gitlab.com](https://gitlab.com)) vs self-hosted
- Community Edition vs Entreprise Edition vs Ultime Edition

[\[ref\]](https://about.gitlab.com/pricing/), [\[détails\]](https://about.gitlab.com/company/pricing/)

---

# 1.4 Gitlab

<div style="text-align: center; margin-top: 150px;">

## Room tour !

</div>

---

# 1.4.a Quelques précisions sur le contexte de la formation

Cette formation portera sur ce qu'il est possible de mettre en place au sein de l'offre **SaaS communautaire** ([gitlab.com](https://gitlab.com))

Les versions Entreprise et Ultimate apportent relativement peu de nouvelles fonctionnalités par rapport à ce qui est déjà proposé dans l'offre gratuite.

La version self-hosted est très proche de l'offre SaaS en terme de fonctionnalités disponibles.

---

# 1.4.a Quelques précisions sur le contexte de la formation

La documentation de Gitlab ([docs.gitlab.com](https://docs.gitlab.com)) indique la disponibilité des différentes fonctionnalités selon les version de Gitlab utilisées.

<div class="columns-3" style="margin-top: 30px;">
<div>

<img src="attachements/Versions%20doc/All%20tiers.png" width="90%" class="center" />

</div>
<div>

<img src="attachements/Versions%20doc/Premium.png" width="90%" class="center" />

</div>
<div>

<img src="attachements/Versions%20doc/Ultimate.png" width="90%" class="center" />

</div>
