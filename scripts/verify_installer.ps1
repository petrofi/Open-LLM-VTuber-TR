param(
    [Parameter(Mandatory=$true)][string]$Installer,
    [Parameter(Mandatory=$true)][string]$ChecksumFile,
    [switch]$LeaveRunning
)
$ErrorActionPreference='Stop'
$workspace=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$installerPath=(Resolve-Path -LiteralPath $Installer).Path
$installerName=[IO.Path]::GetFileName($installerPath)
if ($installerName -notmatch '^Open-LLM-VTuber-TR-v\d+\.\d+\.\d+-tr\.\d+-Setup\.exe$') { throw 'Unexpected installer name' }
$expected=(Get-Content -LiteralPath $ChecksumFile | Where-Object { ($_ -split '\s+')[1] -eq $installerName }) -split '\s+'
if ($expected.Count -lt 2 -or $expected[0] -notmatch '^[0-9a-fA-F]{64}$') { throw 'Checksum entry missing' }
$actual=(Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected[0].ToLowerInvariant()) { throw 'SHA-256 mismatch' }
$installDir=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs/Open-LLM-VTuber-TR'))
$dataDir=[IO.Path]::GetFullPath((Join-Path $env:APPDATA 'Open-LLM-VTuber-TR'))
$application=Join-Path $installDir 'Open-LLM-VTuber-TR.exe'
$desktopLink=Join-Path ([Environment]::GetFolderPath('Desktop')) 'Open-LLM-VTuber TR.lnk'
$startLink=Join-Path $env:APPDATA 'Microsoft/Windows/Start Menu/Programs/Open-LLM-VTuber TR.lnk'
$ownedProcesses=@(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($installDir+'\',[StringComparison]::OrdinalIgnoreCase) })
if ($ownedProcesses.Count) { throw 'Close the installed application before installer verification' }
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
$sentinel=Join-Path $dataDir 'installer-retention-test.txt'
if (-not (Test-Path -LiteralPath $sentinel)) { [IO.File]::WriteAllText($sentinel,[Guid]::NewGuid().ToString()) }
$snapshot=@{}
foreach ($relative in @('installer-retention-test.txt','settings.json','backend/conf.yaml','backend/models/whisper-small/model.bin')) {
    $item=Join-Path $dataDir $relative
    if(Test-Path -LiteralPath $item) { $snapshot[$relative]=(Get-FileHash -LiteralPath $item).Hash }
}
function Assert-Retained {
    foreach($relative in $snapshot.Keys) {
        $item=Join-Path $dataDir $relative
        if(-not (Test-Path -LiteralPath $item) -or (Get-FileHash -LiteralPath $item).Hash -ne $snapshot[$relative]) { throw "User data changed: $relative" }
    }
}
function Install-Release {
    $process=Start-Process -FilePath $installerPath -ArgumentList '/S' -PassThru -Wait -WindowStyle Hidden
    if($process.ExitCode -ne 0) { throw "Installer exit $($process.ExitCode)" }
    $deadline=(Get-Date).AddMinutes(5)
    while(-not (Test-Path -LiteralPath $application)) {
        if((Get-Date) -gt $deadline) { throw 'Installer did not create application' }
        Start-Sleep -Milliseconds 250
    }
    if(-not (Test-Path -LiteralPath $desktopLink) -or -not (Test-Path -LiteralPath $startLink)) { throw 'Shortcut missing' }
    $links=New-Object -ComObject WScript.Shell
    foreach($shortcut in @($desktopLink,$startLink)) {
        if($links.CreateShortcut($shortcut).TargetPath -ne $application) { throw 'Shortcut target mismatch' }
    }
    Assert-Retained
}
$report=[ordered]@{date=(Get-Date).ToUniversalTime().ToString('o');installer=$installerName;sha256=$actual;checksum='PASS'}
$uninstaller=Join-Path $installDir 'Uninstall Open-LLM-VTuber-TR.exe'
if(Test-Path -LiteralPath $uninstaller) {
    $process=Start-Process -FilePath $uninstaller -ArgumentList '/S' -Wait -PassThru -WindowStyle Hidden
    if($process.ExitCode -ne 0) { throw "Uninstaller exit $($process.ExitCode)" }
    $deadline=(Get-Date).AddMinutes(5)
    while((Test-Path -LiteralPath $application) -or (Test-Path -LiteralPath $desktopLink) -or (Test-Path -LiteralPath $startLink)) {
        if((Get-Date) -gt $deadline) { throw 'Application files remain after uninstall' }
        Start-Sleep -Milliseconds 250
    }
    if((Test-Path -LiteralPath $desktopLink) -or (Test-Path -LiteralPath $startLink)) { throw 'Shortcut remains after uninstall' }
    Assert-Retained
    $remaining=@(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($installDir+'\',[StringComparison]::OrdinalIgnoreCase) })
    if($remaining.Count) { throw 'Application process remains after uninstall' }
    $report.uninstall='PASS'
} else { throw 'Expected installed TR uninstaller is missing' }
Install-Release
$report.install='PASS'
Install-Release
$report.reinstall='PASS'
$report.userDataRetained='PASS'
$report.desktopShortcut='PASS'
$report.startMenuShortcut='PASS'
$entries=@(Get-ItemProperty 'HKCU:/Software/Microsoft/Windows/CurrentVersion/Uninstall/*' | Where-Object DisplayName -eq 'Open-LLM-VTuber TR')
if($entries.Count -ne 1) { throw 'Expected exactly one installed application entry' }
$report.version=$entries[0].DisplayVersion
$report.singleInstallation='PASS'
$report.signature=(Get-AuthenticodeSignature -LiteralPath $installerPath).Status.ToString()
New-Item -ItemType Directory -Force -Path (Join-Path $workspace '.build') | Out-Null
$report | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $workspace '.build/installer-verification.json') -Encoding utf8
$report | ConvertTo-Json
if($LeaveRunning) { Start-Process -FilePath $desktopLink }
