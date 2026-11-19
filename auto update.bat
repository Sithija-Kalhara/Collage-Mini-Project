@echo off
chcp 65001 > nul
setlocal

:: ===== Add your repo folders here (one per line) =====
call :sync "C:\Users\sithi\Desktop\Collage Mini Project"
:: call :sync "C:\Users\sithi\Desktop\Another Project"
:: call :sync "D:\Projects\eyerone"
:: =====================================================

echo.
echo All done!
pause
exit /b


:sync
echo.
echo ==================================================
echo  %~1
echo ==================================================

if not exist "%~1\.git" (
    echo [SKIP] Not a git repo: %~1
    exit /b
)
cd /d "%~1"

:: Detect current branch (main / master / anything)
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"
echo Branch: %BRANCH%

git add -A

git diff --cached --quiet
if not errorlevel 1 (
    echo No local changes. Skipping commit.
    goto do_sync
)

powershell -NoProfile -Command "$f = git -c core.quotepath=false diff --cached --name-status; $add=@(); $upd=@(); $del=@(); foreach ($l in $f) { $p = $l -split [char]9; $n = Split-Path $p[-1] -Leaf; switch ($p[0].Substring(0,1)) { 'A' { $add += $n } 'D' { $del += $n } default { $upd += $n } } }; function J($x) { if ($x.Count -gt 3) { ($x[0..2] -join ', ') + ' +' + ($x.Count - 3) + ' more' } else { $x -join ', ' } }; $msg=@(); if ($upd) { $msg += 'Update ' + (J $upd) }; if ($add) { $msg += 'Add ' + (J $add) }; if ($del) { $msg += 'Remove ' + (J $del) }; $m = $msg -join '; '; Write-Host ('Commit: ' + $m); git commit -m $m"

:do_sync
git pull origin %BRANCH% --rebase
git push origin %BRANCH%
exit /b