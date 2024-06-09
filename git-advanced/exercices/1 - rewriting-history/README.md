# Rewriting history

We will play a bit with the rebase, interactive rebase and commit amend.

## Rebase

Using https://learngitbranching.js.org/?locale=fr_FR&NODEMO=, http://git-school.github.io/visualizing-git/#free, or in a local repo, try to manipulate some branches, rebase them against the others to see what happens.

You can try other options of the `git rebase` command

Try to predict what the result will be.

https://git-scm.com/docs/git-rebase

## Interactive rebase

In a local repo, using the interactive rebase mode, try to change the order of a few commits, squash some together, rename one...

https://git-scm.com/docs/git-rebase#_interactive_mode

## Commit amend

In a local repo try to amend the latest commit:
- by adding new changes
- by changing its message

Try to see what happens to the previous commit. You can use the `git cat-file` command.

https://git-scm.com/docs/git-commit

https://git-scm.com/docs/git-cat-file
