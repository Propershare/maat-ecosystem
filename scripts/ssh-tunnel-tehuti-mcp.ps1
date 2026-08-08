# SSH local forwards: 127.0.0.1:8011-8021 on this PC -> 127.0.0.1:8011-8021 on Tehuti server
# Run in PowerShell:  .\ssh-tunnel-tehuti-mcp.ps1
# Requires OpenSSH client (ssh.exe). MCP URLs on PC: http://127.0.0.1:8014 etc.

$TehutiHost = if ($env:TEHUTI_SSH_HOST) { $env:TEHUTI_SSH_HOST } else { "192.168.4.21" }
$TehutiUser = if ($env:TEHUTI_SSH_USER) { $env:TEHUTI_SSH_USER } else { "suspect" }

$forwardArgs = @()
for ($p = 8011; $p -le 8021; $p++) {
    $forwardArgs += "-L"
    $forwardArgs += "${p}:127.0.0.1:${p}"
}

$sshArgs = @(
    "-N",
    "-o", "ExitOnForwardFailure=yes",
    "-o", "ServerAliveInterval=60",
    "-o", "ServerAliveCountMax=3"
) + $forwardArgs + @("${TehutiUser}@${TehutiHost}")

Write-Host "[ssh-tunnel] ${TehutiUser}@${TehutiHost}  ->  local ports 8011-8021"
Write-Host "[ssh-tunnel] Example: http://127.0.0.1:8014 (Tehuti Core)"
Write-Host "[ssh-tunnel] Ctrl+C to stop."
& ssh @sshArgs
