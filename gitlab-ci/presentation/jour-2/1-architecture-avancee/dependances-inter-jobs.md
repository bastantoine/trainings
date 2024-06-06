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