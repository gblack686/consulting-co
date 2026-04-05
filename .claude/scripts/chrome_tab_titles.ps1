# Get window titles for Chrome main processes to identify tabs
$procs = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne "" }
foreach ($p in $procs) {
    $mb = [math]::Round($p.WorkingSet64/1MB)
    Write-Output ("{0,-8} {1,6} MB  {2}" -f $p.Id, $mb, $p.MainWindowTitle)
}
