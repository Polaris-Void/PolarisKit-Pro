@echo off
setlocal enabledelayedexpansion
title Image Batch Renamer -- JPG Renamer
:: ==============================================================
::  IMAGE BATCH RENAMER
::  Renames all recognized image file extensions to .jpg
::  Scope       : Script directory + ALL subdirectories (recursive)
::  Exclusion   : .jpg (already the target format)
::  Removed     : .gif is no longer processed
::  Conflict    : If a target .jpg already exists, the source file
::                is renamed to "BaseName (1).jpg", "BaseName (2).jpg", etc.
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
echo  [START]  Image Batch Renamer
echo  [DIR]    %~dp0  (including all subfolders)
echo  ============================================================
echo.
for /r "%~dp0" %%f in (
*.png   *.webp  *.avif  *.jxl
*.jpeg  *.jpe   *.jfif
*.bmp   *.tiff  *.tif
*.mng
*.heic  *.heif  *.heics *.heifs
*.svg   *.svgz
*.ico   *.cur
*.psd   *.psb
*.tga   *.exr   *.hdr   *.dpx   *.cin
*.sgi   *.rgb   *.rgba
*.jp2   *.j2k   *.jpc   *.jpx   *.jpf   *.j2c
*.jxr   *.wdp   *.hdp
*.pcx   *.pnm   *.pbm   *.pgm   *.ppm   *.pam
*.xbm   *.xpm   *.wbmp  *.dds
*.ai    *.eps
*.raw   *.dng
*.cr2   *.cr3   *.crw
*.nef   *.nrw
*.arw   *.sr2   *.srf
*.raf
*.orf
*.rw2
*.pef   *.ptx
*.dcr   *.kdc   *.k25   *.dcs   *.drf
*.mrw   *.mdc   *.srw
*.3fr   *.fff
*.iiq   *.cap   *.eip
*.rwl   *.bay   *.erf
*.mef   *.mos   *.x3f
*.r3d   *.rwz   *.braw
*.ari   *.gpr
) do (
if /i not "%%~xf"==".jpg" (
if exist "%%~dpnf.jpg" (
call :ResolveUniqueName "%%~dpf" "%%~nf"
ren "%%f" "!resolvedName!.jpg" 2>nul && (
echo  [DUP]    %%~nxf  --^>  !resolvedName!.jpg  --  duplicate avoided
set /a "duplicates+=1"
) || (
echo  [FAIL]   %%~nxf  --  Access denied or file locked
set /a "failed+=1"
)
) else (
ren "%%f" "%%~nf.jpg" 2>nul && (
echo  [OK]     %%~nxf  --^>  %%~nf.jpg
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
if exist "!dirPart!!namePart! (!suffix!).jpg" (
set /a "suffix+=1"
goto RUN_loop
)
endlocal & set "resolvedName=%namePart% (%suffix%)"
goto :eof