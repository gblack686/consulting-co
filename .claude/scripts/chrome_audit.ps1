$procs = Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | Sort-Object WorkingSetSize -Descending
$totalMB = 0
foreach ($p in $procs) {
    $mb = [math]::Round([int64]($p.WorkingSetSize)/1MB)
    $totalMB += $mb
    $cmd = if ($p.CommandLine.Length -gt 120) { $p.CommandLine.Substring(0, 120) } else { $p.CommandLine }
    # Classify the process
    $type = "unknown"
    if ($cmd -match "--type=renderer") { $type = "renderer/tab" }
    elseif ($cmd -match "--type=gpu") { $type = "gpu-process" }
    elseif ($cmd -match "--type=utility") { $type = "utility" }
    elseif ($cmd -match "--type=crashpad") { $type = "crashpad" }
    elseif ($cmd -match "--type=broker") { $type = "broker" }
    elseif ($cmd -match "chrome-devtools-mcp") { $type = "MCP-DEVTOOLS" }
    elseif ($cmd -notmatch "--type=") { $type = "MAIN-BROWSER" }
    Write-Output ("{0,-8} {1,6} MB  {2,-16}  {3}" -f $p.ProcessId, $mb, $type, $cmd)
}
Write-Output ""
Write-Output ("TOTAL: {0} processes using {1} MB ({2:F1} GB)" -f $procs.Count, $totalMB, ($totalMB/1024))
