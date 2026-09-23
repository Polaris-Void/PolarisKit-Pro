@echo off
chcp 65001 > nul
setlocal EnableExtensions
title Directory Tree, Metadata & SHA-256 Auditor

:: دریافت مسیرها
set "LOGFILE=%~dp0File List Log.txt"
set "TARGET_DIR=%~dp0"

cls
echo.
echo    ╔════════════════════════════════════════════════════════════════════════╗
echo    ║                DIRECTORY AUDITOR ^& FILE STRUCTURE TREE                 ║
echo    ║               High-Precision File Metadata ^& SHA-256 Report             ║
echo    ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo     Target Path  :  %TARGET_DIR%
echo     Output File  :  %LOGFILE%
echo.
echo    ──────────────────────────────────────────────────────────────────────────
echo     STATUS       :  Scanning directory structure, metadata ^& SHA-256...
echo    ──────────────────────────────────────────────────────────────────────────

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$OutputEncoding=[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; $t=$env:TARGET_DIR; if($t.Length -gt 3){$t=$t.TrimEnd([char]92)}; $log=$env:LOGFILE; $sw=[System.Diagnostics.Stopwatch]::StartNew(); " ^
    "$global:d=0; $global:f=0; $global:sz=[long]0; " ^
    "function F-Sz([long]$b){ if($b -ge 1GB){return ('{0:N2} GB' -f ($b/1GB))} if($b -ge 1MB){return ('{0:N2} MB' -f ($b/1MB))} if($b -ge 1KB){return ('{0:N2} KB' -f ($b/1KB))} return ('{0} B' -f $b) }; " ^
    "$records=[System.Collections.Generic.List[PSObject]]::new(); $root=Get-Item -LiteralPath $t -ErrorAction SilentlyContinue; " ^
    "$rM=if($root){$root.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')}else{'                   '}; $rC=if($root){$root.CreationTime.ToString('yyyy-MM-dd HH:mm:ss')}else{'                   '}; " ^
    "$records.Add([PSCustomObject]@{T='.'; S='<DIR>'; M=$rM; C=$rC; H='-'}); " ^
    "function Scan-Dir($dir, $pfx){ " ^
    "    $items=@(Get-ChildItem -LiteralPath $dir -Force -ErrorAction SilentlyContinue | Sort-Object {-not $_.PSIsContainer}, Name); $c=$items.Count; " ^
    "    for($i=0; $i -lt $c; $i++){ " ^
    "        $it=$items[$i]; if($it.FullName -eq $log){continue}; $last=($i -eq ($c - 1)); " ^
    "        $br=if($last){[char]0x2514+[char]0x2500+[char]0x2500+' '}else{[char]0x251C+[char]0x2500+[char]0x2500+' '}; $nxt=if($last){$pfx+'    '}else{$pfx+[char]0x2502+'   '}; " ^
    "        $cDate=$it.CreationTime.ToString('yyyy-MM-dd HH:mm:ss'); $mDate=$it.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'); " ^
    "        if($it.PSIsContainer){ $global:d++; $records.Add([PSCustomObject]@{T=($pfx+$br+$it.Name+'/'); S='<DIR>'; M=$mDate; C=$cDate; H='-'}); Scan-Dir $it.FullName $nxt; } " ^
    "        else{ $global:f++; $global:sz += $it.Length; $h=try{(Get-FileHash -LiteralPath $it.FullName -Algorithm SHA256 -ErrorAction Stop).Hash}catch{'<ACCESS DENIED>'}; $records.Add([PSCustomObject]@{T=($pfx+$br+$it.Name); S=(F-Sz $it.Length); M=$mDate; C=$cDate; H=$h}); } " ^
    "    } " ^
    "}; " ^
    "Scan-Dir $t ''; $sw.Stop(); " ^
    "$maxT=36; foreach($r in $records){if($r.T.Length -gt $maxT){$maxT=$r.T.Length}}; $colW=$maxT+2; " ^
    "$bLen=[Math]::Max(120, ($colW+124)); $banner=[string]('=' * $bLen); " ^
    "function C-Txt($txt, $w){ $pL=[Math]::Max(0, [int](($w-$txt.Length)/2)); $pR=[Math]::Max(0, $w-$txt.Length-$pL); return ((' ' * $pL) + $txt + (' ' * $pR)) }; " ^
    "$fmt='  {0,-' + $colW + '}  {1,10}   {2,19}  {3,19}   {4,-64}'; " ^
    "$sep='  ' + [string]('-'*$colW) + '  ' + [string]('-'*10) + '   ' + [string]('-'*19) + '  ' + [string]('-'*19) + '   ' + [string]('-'*64); " ^
    "$w=New-Object System.IO.StreamWriter($log, $false, (New-Object System.Text.UTF8Encoding($true))); " ^
    "$w.WriteLine($banner); $w.WriteLine((C-Txt 'DIRECTORY TREE & FILE AUDIT REPORT' $bLen)); $w.WriteLine($banner); " ^
    "$w.WriteLine(('  Target Path  :  {0}' -f $t)); $w.WriteLine(('  Generated On :  {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))); $w.WriteLine($banner); $w.WriteLine(''); " ^
    "$w.WriteLine(($fmt -f 'PATH / TREE STRUCTURE', '   SIZE   ', '   DATE MODIFIED   ', '   DATE CREATED    ', (C-Txt 'SHA-256 HASH' 64))); $w.WriteLine($sep); " ^
    "foreach($r in $records){ $w.WriteLine(($fmt -f $r.T, $r.S, $r.M, $r.C, $r.H)) }; $w.WriteLine($sep); $w.WriteLine(''); " ^
    "$totSz=F-Sz $global:sz; $w.WriteLine($banner); $w.WriteLine((C-Txt 'STATISTICAL SUMMARY' $bLen)); $w.WriteLine($banner); " ^
    "$w.WriteLine(('  Total Folders   :  {0:N0}' -f $global:d)); $w.WriteLine(('  Total Files     :  {0:N0}' -f $global:f)); " ^
    "$w.WriteLine(('  Total File Size :  {0} ({1:N0} Bytes)' -f $totSz, $global:sz)); $w.WriteLine(('  Execution Time  :  {0:N2} Seconds' -f $sw.Elapsed.TotalSeconds)); " ^
    "$w.WriteLine($banner); $w.WriteLine((C-Txt 'END OF REPORT' $bLen)); $w.WriteLine($banner); $w.Close(); " ^
    "Write-Host ''; Write-Host '   ──────────────────────────────────────────────────────────────────────────' -ForegroundColor DarkGray; " ^
    "Write-Host '    ✔ SCAN COMPLETED SUCCESSFULLY' -ForegroundColor Green; Write-Host '   ──────────────────────────────────────────────────────────────────────────' -ForegroundColor DarkGray; Write-Host ''; " ^
    "Write-Host ('    Folders Scanned :  {0:N0}' -f $global:d) -ForegroundColor Cyan; " ^
    "Write-Host ('    Files Processed :  {0:N0}' -f $global:f) -ForegroundColor Cyan; " ^
    "Write-Host ('    Total Data Size :  {0} ({1:N0} Bytes)' -f $totSz, $global:sz) -ForegroundColor Yellow; " ^
    "Write-Host ('    Execution Time  :  {0:N2} Seconds' -f $sw.Elapsed.TotalSeconds) -ForegroundColor White; Write-Host ''; " ^
    "Write-Host '   ══════════════════════════════════════════════════════════════════════════' -ForegroundColor DarkGray; " ^
    "Write-Host '    ✔ Exported To   : File List Log.txt' -ForegroundColor Green; " ^
    "Write-Host '   ══════════════════════════════════════════════════════════════════════════' -ForegroundColor DarkGray;"

echo.
echo    Closing automatically in 5 seconds (or press any key)...
timeout /t 5 > nul
