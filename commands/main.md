---
name: main
description: Close the session branch and merge it into main as one clean commit
disable-model-invocation: true
---

Close the current session branch and merge it into `main` as a single squashed commit.

Invoking this command is the authorization to merge, commit, and push. Do not stop to
ask for a second confirmation — run the steps in order, show what you do, and report at
the end. Stop only if a check fails.

**1. Pre-flight**
- Confirm the current directory is a git repository. If not, stop.
- Confirm the current branch is NOT `main`/`master`. If it is, stop and say so — there is nothing to merge.
- Commit any uncommitted changes first, following the commit convention: scope prefix + short imperative description, in English, one subject per commit.

**2. Show what will land on main**
Present, in one block:
- The commits on this branch not on `main` (`git log main..HEAD --oneline`)
- The files touched and the diff stat (`git diff main...HEAD --stat`)

**3. Squash merge**
- `git checkout main`
- `git merge --squash <session-branch>`
- `git commit -m "<message>"` — scope prefix + short imperative summary of the whole session, in English. Pick it yourself from the branch's commits.

**4. Clean up**
- Delete the session branch (`git branch -D <session-branch>`).

**5. Push**
- `git push origin main`.

**6. Report**
Show the resulting commit on `main` (`git log -1 --stat`) as evidence.
