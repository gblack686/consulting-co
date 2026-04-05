Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | ForEach-Object {
    if ($_.CommandLine -like '*chrome-devtools-mcp*') {
        Write-Output "PID: $($_.ProcessId) CMD: $($_.CommandLine.Substring(0, [Math]::Min(300, $_.CommandLine.Length)))"
    }
}
