@echo off
echo Cleaning up Git repository...

REM Remove Python cache files
git rm -r --cached backend/**/__pycache__/
git rm -r --cached **/*.pyc
git rm -r --cached **/*.pyo
git rm -r --cached **/*.pyd

REM Remove node_modules and other frontend build artifacts
git rm -r --cached frontend/node_modules/
git rm -r --cached frontend/package-lock.json
git rm -r --cached frontend/package.json
git rm -r --cached frontend/tailwind.config.js
git rm -r --cached frontend/vite.config.js
git rm -r --cached frontend/src/

REM Remove IDE files
git rm -r --cached .vscode/
git rm -r --cached .idea/

REM Add all remaining files
git add .

echo.
echo Files have been removed from Git tracking but kept in your working directory.
echo Now you can commit these changes with:
echo git commit -m "Remove unnecessary files from Git tracking"
echo.
echo After committing, these files will no longer be tracked by Git.
echo.
pause
