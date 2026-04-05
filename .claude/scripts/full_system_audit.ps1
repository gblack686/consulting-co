function Get-GroupStats {
    param([string]$Name, [string]$Filter)
    $procs = Get-CimInstance Win32_Process -Filter $Filter -ErrorAction SilentlyContinue
    if (-not $procs) { return @{ Name=$Name; Count=0; TotalMB=0; TotalGB=0; Details=@() } }
    $totalMB = 0
    $details = @()
    foreach ($p in $procs) {
        $mb = [math]::Round([int64]($p.WorkingSetSize)/1MB)
        $totalMB += $mb
        $cmdline = if ($p.CommandLine) { $p.CommandLine } else { '(no cmdline)' }
        $cmd = if ($cmdline.Length -gt 100) { $cmdline.Substring(0, 100) } else { $cmdline }
        $details += [PSCustomObject]@{ PID=$p.ProcessId; MB=$mb; Cmd=$cmd }
    }
    return @{ Name=$Name; Count=$procs.Count; TotalMB=$totalMB; TotalGB=[math]::Round($totalMB/1024,1); Details=($details | Sort-Object MB -Descending) }
}

$os = Get-CimInstance Win32_OperatingSystem
$totalRAM = [math]::Round([int64]($os.TotalVisibleMemorySize)/1MB, 1)
$freeRAM = [math]::Round([int64]($os.FreePhysicalMemory)/1MB, 1)
$usedRAM = [math]::Round($totalRAM - $freeRAM, 1)
$usedPct = [math]::Round(($usedRAM/$totalRAM)*100)

Write-Output '============================================'
Write-Output '  SYSTEM MEMORY OVERVIEW'
Write-Output '============================================'
Write-Output "  Total RAM:     $totalRAM GB"
Write-Output "  Used:          $usedRAM GB ($usedPct%)"
Write-Output "  Free:          $freeRAM GB"
Write-Output ''

$chrome = Get-GroupStats -Name 'Google Chrome' -Filter "Name='chrome.exe'"
$cursor = Get-GroupStats -Name 'Cursor' -Filter "Name='Cursor.exe' OR Name='cursor.exe'"
$node = Get-GroupStats -Name 'Node.js' -Filter "Name='node.exe'"
$edge = Get-GroupStats -Name 'Microsoft Edge' -Filter "Name='msedge.exe'"
$wsl = Get-GroupStats -Name 'VmmemWSL' -Filter "Name='vmmem'"
$docker = Get-GroupStats -Name 'Docker' -Filter "Name LIKE '%docker%'"
$discord = Get-GroupStats -Name 'Discord' -Filter "Name='Discord.exe'"
$wispr = Get-GroupStats -Name 'Wispr Flow' -Filter "Name LIKE '%wispr%' OR Name LIKE '%Wispr%'"
$onedrive = Get-GroupStats -Name 'OneDrive' -Filter "Name='OneDrive.exe'"
$defender = Get-GroupStats -Name 'Windows Defender' -Filter "Name='MsMpEng.exe'"

$groups = @($chrome, $cursor, $node, $edge, $wsl, $docker, $discord, $wispr, $onedrive, $defender) | Sort-Object { $_.TotalMB } -Descending

Write-Output '============================================'
Write-Output '  MEMORY BY APPLICATION'
Write-Output '============================================'
Write-Output ''

$header = 'Application'.PadRight(22) + 'Procs'.PadLeft(6) + 'MB'.PadLeft(8) + 'GB'.PadLeft(6)
Write-Output $header
Write-Output ('---'.PadRight(22) + '---'.PadLeft(6) + '---'.PadLeft(8) + '---'.PadLeft(6))

$accountedMB = 0
foreach ($g in $groups) {
    if ($g.Count -gt 0) {
        $line = ($g.Name).PadRight(22) + ($g.Count.ToString()).PadLeft(6) + ($g.TotalMB.ToString()).PadLeft(8) + ($g.TotalGB.ToString()).PadLeft(6)
        Write-Output $line
        $accountedMB += $g.TotalMB
    }
}

$otherMB = [math]::Round(($usedRAM * 1024) - $accountedMB)
$otherGB = [math]::Round($otherMB/1024, 1)
$otherLine = 'Other/OS'.PadRight(22) + '---'.PadLeft(6) + $otherMB.ToString().PadLeft(8) + $otherGB.ToString().PadLeft(6)
Write-Output $otherLine
Write-Output ''

Write-Output ''
Write-Output '============================================'
Write-Output "  CURSOR DETAILS ($($cursor.Count) procs)"
Write-Output '============================================'
$cursor.Details | Select-Object -First 15 | Format-Table PID, MB, Cmd -AutoSize

Write-Output ''
Write-Output '============================================'
Write-Output "  NODE.JS DETAILS ($($node.Count) procs)"
Write-Output '============================================'
$node.Details | Select-Object -First 15 | Format-Table PID, MB, Cmd -AutoSize

Write-Output ''
Write-Output '============================================'
Write-Output '  RAM HARDWARE'
Write-Output '============================================'
$slots = Get-CimInstance Win32_PhysicalMemory
foreach ($s in $slots) {
    $gb = [math]::Round([int64]($s.Capacity)/1GB)
    Write-Output "  Slot $($s.DeviceLocator): $gb GB @ $($s.Speed) MHz ($($s.Manufacturer))"
}
$totalSlotGB = [math]::Round(($slots | ForEach-Object { [int64]($_.Capacity)/1GB } | Measure-Object -Sum).Sum)
$maxCap = (Get-CimInstance Win32_PhysicalMemoryArray).MaxCapacity
$maxGB = if ($maxCap) { [math]::Round($maxCap/1MB, 0) } else { 'Unknown' }
Write-Output ''
Write-Output "  Installed: $totalSlotGB GB across $($slots.Count) slot(s)"
Write-Output "  Max supported: $maxGB GB"
