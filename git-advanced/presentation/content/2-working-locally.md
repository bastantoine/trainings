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

# Working locally

- [Dealing with branches](#dealing-with-branches)
- [Tags](#tags)
- [Cherry-pick](#cherry-pick)
- [Stashes](#stashes)
- [Commit selection](#commit-selection)
- [Hooks](#hooks)
- [Aliases](#aliases)
<!-- - [`reflog`](#reflog) -->

---

## Dealing with branches

- [Creation](#creation)
- [(Re)writing the history](#rewriting-the-history)
  - [Amending a commit](#amending-a-commit)
  - [Rebasing](#rebasing)
- [Merging](#merging)
  - [Fast forward merge](#fast-forward-merge)
  - [True merge](#true-merge)
  - [Squash merging](#squash-merging)
  - [Octopus merging](#octopus-merging)

---

### Creation

<div class="columns">
<div>

The easy way:

`git branch [branch name]` (will only create the branch but will not update `HEAD` to point to the new ref)

`git checkout -b [branch name]` (will create the branch and update `HEAD` to point to the new ref)

</div>
<div>

The hard (and funny) way:

`echo [commit long SHA1] > .git/refs/heads/[branch name]`

</div>
</div>

---

### (Re)writing the history

(Re)writing the history of a branch can help keep it clean and understanable and can help minimizing the risk of conflicts when merging.

This can be done by:
- amending commits
- rebasing the branch

---

#### Amending a commit

Amending a commit means editing it to change its message and/or its content.

`git commit --amend` will add all staged changes to the commit at `HEAD` and prompt to change the commit message.

`git commit --amend --no-edit` will simply add all staged changes to the commit at `HEAD` and keep the same commit message.

---

#### Rebasing

Rebasing a branch from an other branch means changing the starting point of the source branch to point to a new starting point.

This effectively rewrites the history of the branch.

<div class="columns">
<div>

**Before**
```
.... B -- D -- E .. target*
    /
.. A -- C ......... source
```

</div>
<div>

</div>
</div>

[\[ref\]](https://git-scm.com/docs/git-rebase)

---

#### Rebasing

Rebasing a branch from an other branch means changing the starting point of the source branch to point to a new starting point.

<div class="columns">
<div>

**Before**
```
.... B -- D -- E .. target*
    /
.. A -- C ......... source
```

</div>
<div>

**After `git rebase source`**
```
......... B'-- D'-- E' .. target*
         /
.. A -- C ............... source
```

</div>
</div>

[\[ref\]](https://git-scm.com/docs/git-rebase)

---

#### Rebasing

We can switch the target branch when rebasing.

<div class="columns">
<div>

**Before**
```
.... B -- E -- F .. target-1*
    /
.. A -- C -- G .... source
         \
......... D -- H .. target-2
```

</div>
<div>

</div>
</div>

---

#### Rebasing

We can switch the target branch when rebasing.

<div class="columns">
<div>

**Before**
```
.... B -- E -- F .. target-1*
    /
.. A -- C -- G .... source
         \
......... D -- H .. target-2
```

</div>
<div>

**After `git rebase target-2`**
```
.. A -- C -- G.................. source
         \
......... D -- H ............... target-2
                \
................ B'-- E'-- F' .. target-1*
```

</div>
</div>

---

##### Interactive rebasing

The interactive rebasing allows to edit specific commits when rebasing. It allows to:
- Change their order
- Edit the message and/or the content of the commit
- Squash some of them together
- Drop selected ones

`git rebase -i/--interactive <ref>`

---

### Merging

<div class="columns">
<div>

Merging a branch into an other branch means bringing the changes of the source branch into the target branch.

`git merge [branch name(s)]`

</div>
<div>

There are 4 different types of merges:
1. Fast forward
2. True merge
3. Squash
4. Octopus

</div>
</div>

---

#### Fast forward merge

Change the ref of the target branch to point to the head of the source branch

Only possible when the head of the target is the starting commit of the source branch.

<div class="columns">
<div>

**Before**
```
.... B -- C -- D source
    /
.. A ........... target*
```

</div>
<div>

</div>
</div>

---

#### Fast forward merge

Change the ref of the target branch to point to the head of the source branch

Only possible when the head of the target is the starting commit of the source branch.

<div class="columns">
<div>

**Before**
```
.... B -- C -- D source
    /
.. A ........... target*
```

</div>
<div>

**After `git merge --ff source`**
```

.. A -- B -- C -- D target*,source

```

</div>
</div>

---

#### True merge

Create a commit in the target branch with the heads of the source and target as parents of the commit.

<div class="columns">
<div>

**Before**
```
.... B -- C -- D source

.. A -- E ...... target*
```

</div>
<div>

</div>
</div>

---

#### True merge

Create a commit in the target branch with the heads of the source and target as parents of the commit.

<div class="columns">
<div>

**Before**
```
.... B -- C -- D source

.. A -- E ...... target*
```

</div>
<div>

**After `git merge --no-ff source`**
```
.... B -- C -- D source
                \
.. A -- E ------ F target*
```

</div>
</div>

---

#### Squash merging

Squash of all the commits of the source branch in a new commit, and put it at the top of the target branch.

<div class="columns">
<div>

**Before**
```
.... B -- C -- D source

.. A -- E ...... target*


```

</div>
<div>

</div>
</div>

---

#### Squash merging

Squash of all the commits of the source branch in a new commit, and put it at the top of the target branch.

<div class="columns">
<div>

**Before**
```
.... B -- C -- D source

.. A -- E ...... target*


```

</div>
<div>

**After `git merge --squash source`**
```
.... B -- C -- D source

.. A -- E ------ F target*
                / \
             B + C + D
```

</div>
</div>

---

#### Octopus merging

There's *technically* no limit to the number of branches to merge at once. A merge of 3 or more branches at once is called an *octopus  merge*.

<div class="columns">
<div>

**Before**
```
... E -- F -- G src-2

... B -- C -- D src-1

... A ......... target*
```

</div>
<div>

</div>
</div>

---

#### Octopus merging

There's *technically* no limit to the number of branches to merge at once. A merge of 3 or more branches at once is called an *octopus  merge*.

<div class="columns">
<div>

**Before**
```
... E -- F -- G src-2

... B -- C -- D src-1

... A ......... target*
```

</div>
<div>

**After `git merge src-1 src-2`**

```
... E -- F -- G   src-2
               \
... B -- C -- D | src-1
               \|
... A --------- H target*
```

</div>
</div>

---

#### Octopus merging

The real life usage of octopus merges are really rare. The risk of merge conflicts are much higher.

The Linux kernel repo has some octopus merges of a lot of branches: [`9b25d60`](https://github.com/torvalds/linux/commit/9b25d604182169a08b206306b312d2df26b5f502) with *27 branches* or even [`2cde51f`](https://github.com/torvalds/linux/commit/2cde51fbd0f3) with *66 branches* (**!**).

> *There's clearly a balance between "octopus merges are fine" and "Christ, that's not an octopus, that's a Cthulhu merge".*
> Linus Torvalds [[*src*]](https://lkml.org/lkml/2014/1/21/361)

---

### Renaming and deleting

Renaming a branch can (*technically*) be done in two different ways:

<div class="columns">
<div>

`git branch -m <new ref>`

</div>
<div>

```
echo $(git rev-parse HEAD) > .git/refs/heads/[new ref] && \
echo 'ref: refs/heads/[new ref]' > .git/HEAD && \
rm -rf .git/refs/heads/[old ref]
```

</div>
</div>


Deleting a branch is pretty straightforward:

<div class="columns">
<div>

`git branch -d/-D <ref>`

</div>
<div>

`rm -rf .git/refs/heads/[ref]`

</div>
</div>

---

## Tags

Creation can be fairly easly... but can be hard as well
<div class="columns">
<div>

`git tag [tag name]`

`git tag [tag name] [commit]`

</div>
<div>

`echo [commit long SHA1] > .git/refs/tags/[tag name]`

</div>
</div>

[\[ref\]](https://git-scm.com/docs/git-tag)

---

## Tags

Tags can have a message as well: `git tag [tag name]`.

In this case `.git/refs/tags/[tag name]` points to a `tag object` instead of a `commit`.

```bash
> git tag v0.0.0 -m "this is a message"
> git cat-file -p $(git rev-parse v0.0.0)
object 202af46197f6a42b2fa9c1315904e040cfc8cd27
type commit
tag v0.0.0
tagger xxx

this is a message
```

---

## Cherry-pick

Cherry-picking one or more commits means applying the changes introduced in all of them in new commits in the current branch.

<div class="columns">
<div>

**Before**
```
.... B -- C ..... target-1
    /
.. A -- D -- F .. source
         \
......... E ..... target-2*
```


</div>
<div>

</div>
</div>

---

## Cherry-pick

Cherry-picking one or more commits means applying the changes introduced in all of them in new commits in the current branch.

<div class="columns">
<div>

**Before**
```
.... B -- C ..... target-1
    /
.. A -- D -- F .. source
         \
......... E ..... target-2*
```

</div>
<div>

**After `git cherry-pick B C`**
```
.... B -- C ............. target-1
    /
.. A -- D -- F .......... source
         \
......... E -- B'-- C' .. target-2*
```

</div>
</div>

---

### Cherry-pick vs rebase

Cherry-pick and rebase are both methods to move commits, but with different behavior on the commits and branches

|                | Rebase                 | Cherry-pick |
|----------------|------------------------|-------------|
| Target commits | new commits            | new commits |
| Source commits | deleted                | kept        |
| Source branch  | moved with new commits | untouched   |

---

## Stashes

Stashes are a way to keep work-in-progress changes but not commit them, and being able to bring them back when needed. [\[ref\]](https://git-scm.com/docs/git-stash/en)

- `git stash`: creates a new stash storing all changes to the files in the work dir and the index, and reset the dir to `HEAD`
- `git stash list`: list all the stashes created
- `git stash apply [stash@{x}]`: applies the changes recorded in the given stash to the current directory
- `git stash pop [stash@{x}]`: same as `apply`, but drops the related stash as well

<!-- ---

## Managing conflicts

#ToDo -->

---

## Commit selection

There are a few ways to provide the ref to a command that needs one:
1. With the SHA-1 (long or short) or the commit
2. With the name of the ref pointing to the commit
3. Through one of its ancestor:

[\[ref\]](https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection)

---

## Commit selection

<div class="columns">
<div>

```
... F -- G -- H   branch-2
               \
... C -- D -- E | branch-1
               \|
... A -- B ---- I main
```

</div>
<div>

- `I^`, `I~` : `B`
- `I^2` : `E`
- `I~2` : `A`
- `I^2~` : ?

</div>
</div>

---

### Commit range selection

Some commands can accept a range of refs as input (like `git log`, `git rebase`, `git cherry-pick`...)

- `refA..refB`: select all the commits that are in `refB` but not in `refA`
- `refA...refB`: select all the commits that are in `refA` or `refB`, but not both

[\[ref\]](https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection)

---

### Commit range selection

<div class="columns">
<div>

```
......... C -- D ...... refB
         /
.. A -- B -- E -- H ... main
             \
............. F -- G .. refC
```

</div>
<div>

- `main..refB`: `C`, `D`
- `refB..refC`: `E`, `F`, `G`
- `refB...refC`: ?

</div>
</div>

---

## Hooks

<div class="columns">
<div>

Hooks are programs placed in the hooks directory of the repo to trigger actions at certain points in the repo lifecycle. [\[ref\]](https://git-scm.com/docs/githooks)

For example: `.git/hooks/pre-commit` will be executed during the execution of `git commit`, but before the commit is created.

</div>
<div>

```bash
> tree .git/hooks
.git/hooks
├── applypatch-msg.sample
├── commit-msg.sample
├── fsmonitor-watchman.sample
├── post-update.sample
├── pre-applypatch.sample
├── pre-commit.sample
├── pre-merge-commit.sample
├── pre-push.sample
├── pre-rebase.sample
├── pre-receive.sample
├── prepare-commit-msg.sample
├── push-to-checkout.sample
└── update.sample
```

</div>
</div>

---

## Aliases

Like aliases in a Unix-like shell, git support defining aliases to customize the user experience to everyone's needs and wishes.

They can be defined in the user's `.gitconfig` file, or on a specific repo's `.git/config` file.

They can also be externale executable found in the `$PATH`. They must be named like `git-<alias name>`, in which case they can be invoked with `git <alias-name>`.

---

## Aliases

```bash
> cat $HOME/.gitconfig
...
[alias]
    res = "!r() { git reset HEAD~$1; }; r"
    wip = commit -am WIP
    go = "!f() { git checkout -b \"$1\" 2> /dev/null || git checkout \"$1\"; }; f"
...
> cat $(which git-random)
touch $(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
git add .
git commit -m "$(curl -s https://whatthecommit.com/index.txt)"
```

---

## Undoing commits

There are a few ways to undo one or more commits.

`git reset <commit(s)>`: this will reset the given commit(s) and put their changes back in the working tree
  - the `--soft` option allows to keep the changes in the stage area, instead of the working tree
  - the `--hard` option will permanently discard all changes of the commit(s)

[\[ref\]](https://git-scm.com/docs/git-reset)

---

## Undoing commits

Commits can also be reverted, instead of undone.

`git revert <commit(s)>`: this will created a new commit with changes opposites of the provided commits, effectively canceling them.

[\[ref\]](https://git-scm.com/docs/git-revert)

<!-- ---

## `reflog`

#ToDo -->
