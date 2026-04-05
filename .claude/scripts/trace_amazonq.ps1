# Trace Amazon Q — find parent process chain and startup origin
Write-Output '============================================'
Write-Output '  AMAZON Q PROCESS TREE'
Write-Output '============================================'

$aqProcs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'AmazonQ' }
foreach ($p in $aqProcs) {
    $mb = [math]::Round([int64]($p.WorkingSetSize)/1MB)
    Write-Output ''
    Write-Output "PID: $($p.ProcessId)  Memory: $mb MB"
    Write-Output "Command: $($p.CommandLine)"
    Write-Output "Created: $($p.CreationDate)"

    # Walk parent chain
    $current = $p
    $depth = 0
    Write-Output 'Parent chain:'
    while ($current.ParentProcessId -and $depth -lt 10) {
        $parent = Get-CimInstance Win32_Process -Filter "ProcessId=$($current.ParentProcessId)" -ErrorAction SilentlyContinue
        if (-not $parent) {
            Write-Output "  -> PID $($current.ParentProcessId) (no longer running)"
            break
        }
        $pmb = [math]::Round([int64]($parent.WorkingSetSize)/1MB)
        $pcmd = if ($parent.CommandLine -and $parent.CommandLine.Length -gt 150) { $parent.CommandLine.Substring(0,150) } elseif ($parent.CommandLine) { $parent.CommandLine } else { '(no cmdline)' }
        Write-Output "  -> PID $($parent.ProcessId) ($pmb MB) $($parent.Name): $pcmd"
        $current = $parent
        $depth++
    }
}

Write-Output ''
Write-Output '============================================'
Write-Output '  AMAZON Q FILES ON DISK'
Write-Output '============================================'
$aqPath = "$env:LOCALAPPDATA\aws\toolkits\language-servers\AmazonQ"
if (Test-Path $aqPath) {
    Write-Output "Location: $aqPath"
    Get-ChildItem $aqPath -Directory | ForEach-Object { Write-Output "  Version: $($_.Name)" }
} else {
    Write-Output 'AmazonQ language server directory not found'
}

Write-Output ''
Write-Output '============================================'
Write-Output '  CURSOR EXTENSIONS REFERENCING AMAZON'
Write-Output '============================================'
$extDir = "$env:USERPROFILE\.cursor\extensions"
if (Test-Path $extDir) {
    $amazonExts = Get-ChildItem $extDir -Directory | Where-Object { $_.Name -match 'amazon|aws' }
    if ($amazonExts) {
        foreach ($e in $amazonExts) {
            Write-Output "  Extension: $($e.Name)"
            $pkg = Join-Path $e.FullName 'package.json'
            if (Test-Path $pkg) {
                $json = Get-Content $pkg -Raw | ConvertFrom-Json
                Write-Output "    Display: $($json.displayName)"
                Write-Output "    Version: $($json.version)"
                Write-Output "    Desc: $($json.description)"
            }
        }
    } else {
        Write-Output '  No Amazon/AWS extensions found in Cursor'
    }
} else {
    Write-Output '  Cursor extensions directory not found'
}

Write-Output ''
Write-Output '============================================'
Write-Output '  VS CODE EXTENSIONS REFERENCING AMAZON'
Write-Output '============================================'
$vscExtDir = "$env:USERPROFILE\.vscode\extensions"
if (Test-Path $vscExtDir) {
    $amazonExts = Get-ChildItem $vscExtDir -Directory | Where-Object { $_.Name -match 'amazon|aws' }
    if ($amazonExts) {
        foreach ($e in $amazonExts) {
            Write-Output "  Extension: $($e.Name)"
        }
    } else {
        Write-Output '  No Amazon/AWS extensions found in VS Code'
    }
}

Write-Output ''
Write-Output '============================================'
Write-Output '  STARTUP / SCHEDULED TASKS'
Write-Output '============================================'
$tasks = Get-ScheduledTask | Where-Object { $_.TaskName -match 'amazon|aws|AmazonQ' } -ErrorAction SilentlyContinue
if ($tasks) {
    foreach ($t in $tasks) {
        Write-Output "  Task: $($t.TaskName) State: $($t.State)"
    }
} else {
    Write-Output '  No Amazon/AWS scheduled tasks found'
}

# Check startup registry
$startupKeys = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run'
)
foreach ($key in $startupKeys) {
    $vals = Get-ItemProperty $key -ErrorAction SilentlyContinue
    if ($vals) {
        $vals.PSObject.Properties | Where-Object { $_.Value -match 'amazon|aws|AmazonQ' } | ForEach-Object {
            Write-Output "  Registry startup: $($_.Name) = $($_.Value)"
        }
    }
}
