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

# Git objects

- [Blob](#blob)
- [Tree](#tree)
- [Commit](#commit)
- [Branches, tags and references](#branches-tags-and-references)
- [The index](#the-index)
- [Plumbing vs porcelain commands](#plumbing-vs-porcelain-commands)

---

## Blob

A blob (*binary large object*) represents the content of a file.

- They store the raw data of the file without any metadata (no filename, timestamp...).
- They are identified by a SHA-1 hash (20 bytes).
- They are immutable.

---

## Tree

<div class="columns">
<div>

A tree object represents the state of a directory at a specific point in time.

- They contain references to blobs and other trees.
- They contain metadata about the blobs and trees referenced (filename, timestamp...).
- They are identified by a SHA-1 hash.

</div>
<div>

```shell
> tree .
.
├── dir
│   ├── bar.txt
│   └── wan.txt
├── foo.txt
└── obi.txt
> git log --oneline
e7087d9 (HEAD -> main) init
> git ls-tree e7087d9
040000 tree 3723b9 dir
100644 blob 5716ca foo.txt
100644 blob 495cc9 obi.txt
```

</div>
</div>

---

## Commit

<div class="columns">
<div>

A snapshot of the state of the repository, representing a specific point in the project's history.

It is identified by its **SHA-1 hash** computed from various attributes.

</div>
<div>

1. **Commit Message**
2. **Author Information**
3. **Timestamp**
4. **Parent Commit(s)**
5. **Tree Object**

</div>
</div>

---

## Commit

<div class="columns">
<div>

The commit doesn't store new blobs and trees all the time.

It only stores new references to the modified blobs and trees, and keep the existing references to the untouched one.

</div>
<div>

```shell
> git init
> touch foo bar
> git add .
> git commit -am init
[main (root-commit) 240e67d] init
> git ls-tree 240e67d
100644 blob e69de2 bar
100644 blob e69de2 foo
> echo foo > foo
> git commit -am update
[main 20bfefd] update
> git ls-tree 20bfefd
100644 blob e69de2 bar
100644 blob 257cc5 foo
```

</div>
</div>

---

## Branches, tags and references

Branches are a way to diverge from an other branch to work in isolation. They help developers work in parallel on the same code base.

Tags are references to specific commits in the project history and are often used to mark specific milestones in the project.

---

## Branches, tags and references

<div class="columns">
<div>

References (*refs*) are aliases to specific commits. They have user-friendly names that are easier to remember and manipulate than the SHA-1 hash of the commits.

They are used mostly for branches and tags.

[\[ref\]](https://git-scm.com/book/en/v2/Git-Internals-Git-References)

</div>
<div>

```shell
> git branch feat/my-feature
> git tag v0.0.1
> tree .git
.git
├── HEAD
└── refs
    ├── heads
    │   ├── main
    │   └── feat
    │       └── my-feature
    └── tags
        └── v0.0.1
> cat .git/refs/head/feat/my-feature
fcd97dac87212932af83101fd0413a7195356f4a
> cat .git/refs/tags/v0.0.1
202af46197f6a42b2fa9c1315904e040cfc8cd27
```

</div>
</div>

---

### Symbolic references

<div class="columns">
<div>

Symbolic references are refs that points to other refs.

The most known and useful one is `HEAD`. It is a reference to the current branch being used.

[\[ref\]](https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefHEADaHEAD)

</div>
<div>

```bash
> cat .git/HEAD
ref: refs/heads/target
```

</div>
</div>

---

## The index

<!-- https://stackoverflow.com/questions/4084921/what-does-the-git-index-contain-exactly?noredirect=1&lq=1 -->

<div class="columns">
<div>

The index (or the staging area) acts as an intermediate space between the working directory and the repository.

Changes that should/will be committed are first added to the staging area.


</div>
<div>

```
WORK DIR              STAGING           REPO
    |------ git add ---->|                |
    |                    |                |
    |<---- git reset ----|                |
    |                    |                |
    |                    |-- git commit ->|
    |                    |                |
    |     git reset --soft HEAD~1         |
    |                    |      |         |
    |                    |<-----+---------|
    |                    |                |
    |<-------- git reset HEAD~1 ----------|
```

</div>
</div>

---

## Plumbing vs porcelain commands

<div class="columns">
<div>

**Plumbing**

`rev-parse`, `cat-file`, `update-ref`, `update-index`...

Commands used to manipulate the internals objects of Git, rarely used by the end user.

</div>
<div>

**Porcelain**

`init`, `log`, `clone`, `add`, `commit`, `checkout`, `merge`, `push`...

Commands used on a daily basis, sometimes wrappers around one or more plumbing commands.

</div>
</div>

[\[ref\]](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)

<!-- ---

## Plumbing vs porcelain commands

Some useful plumbing commands:

[`git rev-parse`](https://git-scm.com/docs/git-rev-parse): the SHA-1 hash of a given reference (branch, tag)

`git update-ref refs/<type>/<name> <hash>`: update the ref `name` to point to the new `hash`

`git symbolic-ref <ref>`: manipulate symbolic refs -->

<!-- ---

# Crafting a commit by hand -->
