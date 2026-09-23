@echo off
setlocal enabledelayedexpansion
title Video Batch Renamer -- MP4 Renamer
:: ==============================================================
::  VIDEO BATCH RENAMER
::  Renames all recognized video file extensions to .mp4
::  Scope       : Script directory + ALL subdirectories (recursive)
::  Exclusion   : .mp4 (already the target format)
::  Conflict    : If a target .mp4 already exists, the source file
::                is renamed to "BaseName (1).mp4", "BaseName (2).mp4", etc.
::                so it is still renamed -- no file is ever
::                overwritten or deleted.
::  Status tags : [OK] [DUP] [FAIL]
::  Standards   : Windows Batch -- Delayed Expansion + Error Handling
:: ==============================================================
pushd "%~dp0"
set "count=0"
set "duplicates=0"
set "failed=0"
echo.
echo  [START]  Video Batch Renamer
echo  [DIR]    %~dp0  (including all subfolders)
echo  ============================================================
echo.
for /r "%~dp0" %%f in (
*.avi   *.mov   *.wmv   *.flv   *.f4v
*.mkv   *.webm  *.m4v   *.3gp   *.3g2
*.mpg   *.mpeg  *.mpe   *.m1v   *.m2v   *.mpv
*.m2t   *.m2ts  *.mts   *.ts    *.vob
*.ogv   *.ogm   *.divx  *.asf
*.rm    *.rmvb  *.nsv   *.amv   *.dat
*.mod   *.tod   *.dv    *.yuv   *.y4m   *.qt
*.mxf   *.gxf
*.r3d   *.braw  *.ari   *.crm
*.bik   *.roq
) do (
if /i not "%%~xf"==".mp4" (
if exist "%%~dpnf.mp4" (
call :ResolveUniqueName "%%~dpf" "%%~nf"
ren "%%f" "!resolvedName!.mp4" 2>nul && (
echo  [DUP]    %%~nxf  --^>  !resolvedName!.mp4  --  duplicate avoided
set /a "duplicates+=1"
) || (
echo  [FAIL]   %%~nxf  --  Access denied or file locked
set /a "failed+=1"
)
) else (
ren "%%f" "%%~nf.mp4" 2>nul && (
echo  [OK]     %%~nxf  --^>  %%~nf.mp4
set /a "count+=1"
) || (
echo  [FAIL]   %%~nxf  --  Access denied or file locked
set /a "failed+=1"
)
)
)
)
echo.
set /a "total=count+duplicates+failed"
echo  ============================================================
echo   Renamed   : !count!
echo   Suffixed  : !duplicates!
echo   Failed    : !failed!
echo   ------------------------------------------------------------
echo   Total     : !total!
echo  ============================================================
echo.
popd
timeout /t 10
endlocal
goto :eof
:ResolveUniqueName
:: %1 = directory of the source file (trailing backslash included)
:: %2 = base file name without extension
:: Returns a collision-free base name in "resolvedName"
setlocal enabledelayedexpansion
set "dirPart=%~1"
set "namePart=%~2"
set "suffix=1"
:RUN_loop
if exist "!dirPart!!namePart! (!suffix!).mp4" (
set /a "suffix+=1"
goto RUN_loop
)
endlocal & set "resolvedName=%namePart% (%suffix%)"
goto :eof