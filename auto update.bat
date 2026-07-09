@echo off
cd /d "C:\Users\sithi\Desktop\Collage Mini Project"

if not exist .git (
    git init
    git remote add origin https://github.com/Sithija-Kalhara/Collage-Mini-Project.git
    git branch -M main
    git pull origin main --allow-unrelated-histories
)

git add .

for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set "TIMESTAMP=%%i"

git commit --allow-empty -m "Auto update at startup: %TIMESTAMP%"

git push origin main

pause