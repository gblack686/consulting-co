$procs = Get-CimInstance Win32_Process -Filter "Name='chrome.exe'"

$yourBrowser = @()
$mcpDevtools = @()
$extensions = @()
$infrastructure = @()

foreach ($p in $procs) {
    $cmd = $p.CommandLine
    $mb = [math]::Round([int64]($p.WorkingSetSize)/1MB)
    $obj = [PSCustomObject]@{
        PID = $p.ProcessId
        MemMB = $mb
        Type = ""
        Category = ""
    }

    if ($cmd -match 'chrome-devtools-mcp|\.cache\\chrome-de') {
        $obj.Category = "MCP-DEVTOOLS"
    } elseif ($cmd -match '--extension-process') {
        $obj.Category = "EXTENSION"
    } elseif ($cmd -match '--type=gpu') {
        if ($cmd -match '\.cache\\chrome-de|disable-gpu-sandbox') {
            $obj.Category = "MCP-DEVTOOLS"
        } else {
            $obj.Category = "YOUR-CHROME"
        }
    } elseif ($cmd -match '--type=renderer') {
        $obj.Category = "YOUR-TAB"
    } elseif ($cmd -match '--type=utility') {
        $obj.Category = "CHROME-INFRA"
    } elseif ($cmd -match '--type=crashpad') {
        if ($cmd -match '\.cache\\chrome-de') {
            $obj.Category = "MCP-DEVTOOLS"
        } else {
            $obj.Category = "CHROME-INFRA"
        }
    } elseif ($cmd -match '--allow-pre-commit-input --disable-background') {
        $obj.Category = "MCP-DEVTOOLS"
    } else {
        $obj.Category = "YOUR-CHROME"
    }

    # Type
    if ($cmd -match '--type=renderer.*--extension') { $obj.Type = "extension" }
    elseif ($cmd -match '--type=renderer') { $obj.Type = "tab" }
    elseif ($cmd -match '--type=gpu') { $obj.Type = "gpu" }
    elseif ($cmd -match '--type=utility') { $obj.Type = "utility" }
    elseif ($cmd -match '--type=crashpad') { $obj.Type = "crashpad" }
    elseif ($cmd -notmatch '--type=') { $obj.Type = "main" }
    else { $obj.Type = "other" }

    switch ($obj.Category) {
        "MCP-DEVTOOLS" { $mcpDevtools += $obj }
        "EXTENSION" { $extensions += $obj }
        "YOUR-TAB" { $yourBrowser += $obj }
        "YOUR-CHROME" { $yourBrowser += $obj }
        "CHROME-INFRA" { $infrastructure += $obj }
    }
}

Write-Output "========================================="
Write-Output "  YOUR CHROME BROWSER (tabs + main)"
Write-Output "========================================="
$yourBrowser | Sort-Object MemMB -Descending | Format-Table PID, @{N='MB';E={$_.MemMB}; Align='Right'}, Type -AutoSize
$yourTotal = ($yourBrowser | Measure-Object -Property MemMB -Sum).Sum
Write-Output ("  Subtotal: {0} processes, {1} MB ({2:F1} GB)" -f $yourBrowser.Count, $yourTotal, ($yourTotal/1024))

Write-Output ""
Write-Output "========================================="
Write-Output "  CHROME EXTENSIONS"
Write-Output "========================================="
$extensions | Sort-Object MemMB -Descending | Format-Table PID, @{N='MB';E={$_.MemMB}; Align='Right'}, Type -AutoSize
$extTotal = ($extensions | Measure-Object -Property MemMB -Sum).Sum
Write-Output ("  Subtotal: {0} processes, {1} MB" -f $extensions.Count, $extTotal)

Write-Output ""
Write-Output "========================================="
Write-Output "  MCP CHROME DEVTOOLS (Claude Code)"
Write-Output "========================================="
$mcpDevtools | Sort-Object MemMB -Descending | Format-Table PID, @{N='MB';E={$_.MemMB}; Align='Right'}, Type -AutoSize
$mcpTotal = ($mcpDevtools | Measure-Object -Property MemMB -Sum).Sum
Write-Output ("  Subtotal: {0} processes, {1} MB" -f $mcpDevtools.Count, $mcpTotal)

Write-Output ""
Write-Output "========================================="
Write-Output "  CHROME INFRASTRUCTURE (utilities etc)"
Write-Output "========================================="
$infrastructure | Sort-Object MemMB -Descending | Format-Table PID, @{N='MB';E={$_.MemMB}; Align='Right'}, Type -AutoSize
$infraTotal = ($infrastructure | Measure-Object -Property MemMB -Sum).Sum
Write-Output ("  Subtotal: {0} processes, {1} MB" -f $infrastructure.Count, $infraTotal)

Write-Output ""
Write-Output "========================================="
Write-Output "  GRAND TOTAL"
Write-Output "========================================="
$grandTotal = $yourTotal + $extTotal + $mcpTotal + $infraTotal
Write-Output ("  Your tabs:     {0,5} MB  ({1} processes)" -f $yourTotal, $yourBrowser.Count)
Write-Output ("  Extensions:    {0,5} MB  ({1} processes)" -f $extTotal, $extensions.Count)
Write-Output ("  MCP DevTools:  {0,5} MB  ({1} processes)" -f $mcpTotal, $mcpDevtools.Count)
Write-Output ("  Infrastructure:{0,5} MB  ({1} processes)" -f $infraTotal, $infrastructure.Count)
Write-Output ("  TOTAL:         {0,5} MB  ({1} processes) = {2:F1} GB" -f $grandTotal, $procs.Count, ($grandTotal/1024))
