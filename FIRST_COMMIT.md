# Installing this package

Target repository: https://github.com/wasam0110/AgentHive_FYP.git

Extract the ZIP contents into your local clone without replacing its .git directory. This archive contains no .git directory and does not push anything. If existing files differ, review changes before overwriting them.

The package contains all four local instruction files for distribution. Give each teammate their own file and keep the matching progress file in Git. If an assistant sees several local instructions, specify the member name. Every filename is case-sensitive: shizza uses lowercase as requested.

Run from the repository root:

```powershell
git add .
git status
git ls-files -- '*-instructions.md' AGENTS.local.md submissions/private
```

The last command must produce no output. If a personal file was already tracked, remove that exact file from the index with `git rm --cached -- <path>`; do not delete your local copy. Verify the shared progress files remain staged.

```powershell
git diff --cached --check
git commit -m "chore: add FYP plans, team progress, academic drafts and starter CI"
git push -u origin HEAD
```

Check the current branch and remote before pushing. Use a pull request if the repository already has an established default branch. No history is changed by this package. Personal files are included in the ZIP for distribution but ignored by Git; sharing the ZIP itself shares those files.

Original university templates remain unfilled. Report chapters are honest starting drafts, not completed submissions. No signatures, official screening reports, approved SDG mappings or evaluation results have been fabricated.
