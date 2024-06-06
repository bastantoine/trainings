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

# 1. Architecture avancée

- [Accélération de l'exécution des jobs](#11-accélération-de-lexécution-des-jobs)
- [Factorisation de la config](#12-factorisation-de-la-config)
- [Dépendances inter-jobs](#13-dépendances-inter-jobs)
- [Downstream pipelines](#14-downstream-pipelines)
- [Services](#15-services)