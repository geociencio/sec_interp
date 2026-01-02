---
description: How to commit changes cleanly (handling hooks)
---
This workflow describes the process for committing changes, ensuring code quality standards are met without getting blocked by pre-commit hook conflicts.

1. **Pre-Format**: Manually run `ruff` to fix any linting or formatting issues *before* committing. This prevents the pre-commit hook from modifying files mid-commit, which can cause the commit to fail.

   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```
   // turbo-all

2. **Stage Changes**: Add all modified files to the staging area.
   ```bash
   git add .
   ```
   *Note: Be specific with `git add <files>` if you don't want to stage everything.*

3. **Verify Status**: Check what is going to be committed.
    ```bash
    git status
    ```

4. **Commit**: Commit the changes following Conventional Commits guidelines.
   ```bash
   git commit -m "type: description" -m "detailed body"
   ```

   *If the pre-commit hook fails and modifies files:*
   1. The hook has automatically fixed issues.
   2. Run `git add <modified_files>` again.
   3. Run the `git commit` command again.
