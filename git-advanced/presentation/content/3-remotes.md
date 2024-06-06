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

# Dealing with remotes

---

## Managing remotes

Remotes are distant repositories hosted on distant servers. They allow collaboration between multiple devs.

They allow to push commits to existing branches, create new ones, pull commits from distant branches into new or existing branches.

---

## Managing remotes

When you clone a repository, you have automatically one remote configured.

```bash
> git clone https://github.com/bastantoine/tests
Cloning into 'tests'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (3/3), done.
> cd tests
> git remote -v
origin	https://github.com/bastantoine/tests (fetch)
origin	https://github.com/bastantoine/tests (push)
```

---

## Using remote branches

To be able to push and pull changes to and from a remote, a local branch must be configured to track a remote one.

If you create a new branch locally, you can configure it to automatically be mapped to a distant one:

```bash
> git branch --set-upstream-to=origin/<distant-branch> <local-branch>
```

[\[ref\]](https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---set-upstream-toltupstreamgt)

---

## Using remote branches

This can also be setup when pushing the local branch for the first time:

```bash
> git push --set-upstream <local-branch>
```

[\[ref\]](https://git-scm.com/docs/git-push#Documentation/git-push.txt---set-upstream)

---

## Using remote branches

This mapping can also be automatically set for branches pushed for the first time

```bash
> git config [--global|--local] push.autoSetupRemote true
```

[\[ref\]](https://git-scm.com/docs/git-config#Documentation/git-config.txt-pushautoSetupRemote)

---

## Using remote branches

If you checkout a distant branch locally, the newly created local branch will automatically be setup to track the remote one:

```bash
> git branch --all
* main
  test
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
  remotes/origin/remote-branch
  remotes/origin/test
> git checkout remote-branch
branch 'remote-branch' set up to track 'origin/remote-branch'.
Switched to a new branch 'remote-branch'
```

---

## Using remote branches

```bash
> git remote show origin
* remote origin
  Fetch URL: https://github.com/bastantoine/tests
  Push  URL: https://github.com/bastantoine/tests
  HEAD branch: main
  Remote branches:
    main          tracked
    test          tracked
  Local branches configured for 'git pull':
    main          merges with remote main
    test          merges with remote test
  Local refs configured for 'git push':
    main          pushes to main          (fast-forwardable)
    test          pushes to test          (up to date)
```

---

## Staying up-to-date

Working with Git in a team, you'll need to frequently stay up-to-date with the changes brought by the other contributors, and have them on your local repo.

This can be done by fetching changes from the remote and merging/rebasing them locally.

---

## Staying up-to-date

```bash
> git fetch
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), 962 bytes | 240.00 KiB/s, done.
From https://github.com/bastantoine/tests
   4583b61..b697983  test       -> origin/test
> # Remote changes are fetched...
> git log --oneline origin/test
b697983 (origin/test) Create tests
4583b61 (HEAD -> test) Updated framework to the lattest version
e849f3f (origin/main, origin/HEAD) Initial commit
> # ...but not merged in the local branch
> git log --oneline test
4583b61 (HEAD -> test) Updated framework to the lattest version
e849f3f (origin/main, origin/HEAD) Initial commit
```

---

## Staying up-to-date

```bash
> git log --oneline origin/test
b697983 (origin/test) Create tests
4583b61 (HEAD -> test) Updated framework to the lattest version
e849f3f (origin/main, origin/HEAD) Initial commit
```

<div class="columns">
<div>

**Using merge**

```bash
> git merge origin/test
Updating 4583b61..b697983
Fast-forward
 tests | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 tests
> git log --oneline test
b697983 (HEAD -> test, origin/test) Create tests
4583b61 Updated framework to the lattest version
e849f3f (rigin/main, origin/HEAD) Initial commit
```

</div>
<div>

**Using rebase**

```bash
> git rebase origin/test
Successfully rebased and updated refs/heads/test.
> git log --oneline test
b697983 (HEAD -> test, origin/test) Create tests
4583b61 Updated framework to the lattest version
e849f3f (rigin/main, origin/HEAD) Initial commit
```

</div>
</div>

---

## Staying up-to-date

The `git fetch` command will simply get all the changes from the remote repository, but will not merge them. They can later be brought into the local repo with either `merge` or `rebase`.

When a branch is configured to track a remote branch, the `git pull` command can fetch and update it at once:

- `git fetch` + `git merge` = `git pull`
- `git fetch` + `git rebase` = `git pull --rebase`

---

## Staying up-to-date

> ⚠️ **Warning** : Be careful when rebasing a local branch that is configured to track a remote one.
>
> Because the rebase creates new commits, in the wrong setup you can end up changing commits that have already been push to the remote

---

## Staying up-to-date

*Initial state*

<div class="columns">
<div>

**Local**

```
.. A -- B -- C -- D .. main
```

</div>
<div>

**Remote**

```
.. A -- B -- C -- D .. origin/main
```

</div>
</div>

---

## Staying up-to-date

A local rebase creates `E` based on `C` and points `main` to it

<div class="columns">
<div>

**Local**

```
               D
              /
.. A -- B -- C -- E .. main
```

</div>
<div>

**Remote**

```
.. A -- B -- C -- D .. origin/main
```

</div>
</div>

---

## Staying up-to-date

A push sends the new commit `E` and updates `origin/main` (the option `--force` would be needed)

<div class="columns">
<div>

**Local**

```
               D
              /
.. A -- B -- C -- E .. main
```

</div>
<div>

**Remote**

```
.. A -- B -- C -- E .. origin/main
```

</div>
</div>

The problem is that `D` has effectively disappeared from `origin`.

This can cause issues when commits and/or branches depended on the missing commit.

---

## Staying up-to-date

<div class="columns">
<div>

![width:550px](https://i.miximum.fr/i/2014/12/1X9YPBFMK8_l.png)

</div>
<div>

> ⚠️ **Warning** : Be *really* careful when force pushing stuff. By rewriting the remote history, you may accidentally break the team members' local repo, or perhaps even the entire repo.
>
> *The safest solution is to simply never do it*.

</div>
</div>

<!-- ---

## Working with multiple remotes

A local repository can be configured to pull and push changes to and from multiple remote repos. -->

---
