@echo off
cd /d "C:\Users\sithi\Desktop\Collage Mini Project"

if not exist .git (
    git init
    git remote add origin https://github.com/Sithija-Kalhara/Collage-Mini-Project.git
    git branch -M main
    git pull origin main --allow-unrelated-histories
)

git add .
git commit -m "Auto update at startup: %date% %time%"
git push origin main

pause