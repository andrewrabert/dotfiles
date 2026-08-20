#Requires -RunAsAdministrator

param(
    [Parameter(Mandatory)]
    [string]$PublicKey,

    [string]$UserName = $env:USERNAME
)

$ErrorActionPreference = "Stop"
$PublicKey = $PublicKey.Trim()

if ($PublicKey -notmatch '^(ssh-|ecdsa-|sk-)') {
    throw "The supplied value does not look like an SSH public key."
}

# Resolve the account, SID, and profile directory.
$Account = [System.Security.Principal.NTAccount]::new($UserName)
$Sid = $Account.Translate(
    [System.Security.Principal.SecurityIdentifier]
)
$AccountName = $Sid.Translate(
    [System.Security.Principal.NTAccount]
).Value

$ProfileRegistryPath =
    "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\$($Sid.Value)"

$UserProfile = [Environment]::ExpandEnvironmentVariables(
    (Get-ItemProperty $ProfileRegistryPath).ProfileImagePath
)

# Install and enable OpenSSH Server.
$Capability = Get-WindowsCapability -Online `
    -Name "OpenSSH.Server~~~~0.0.1.0"

if ($Capability.State -ne "Installed") {
    Add-WindowsCapability -Online `
        -Name "OpenSSH.Server~~~~0.0.1.0"
}

Set-Service sshd -StartupType Automatic
Start-Service sshd

# Ensure the firewall rule exists.
if (-not (Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" `
            -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule `
        -Name "OpenSSH-Server-In-TCP" `
        -DisplayName "OpenSSH SSH Server (sshd)" `
        -Enabled True `
        -Direction Inbound `
        -Protocol TCP `
        -Action Allow `
        -LocalPort 22
}

# User authorized_keys.
$UserSshDirectory = Join-Path $UserProfile ".ssh"
$UserKeyFile = Join-Path $UserSshDirectory "authorized_keys"

New-Item $UserSshDirectory -ItemType Directory -Force | Out-Null
Set-Content $UserKeyFile -Value $PublicKey -Encoding ASCII

# Remove inherited permissions and permit only the user and SYSTEM.
icacls.exe $UserSshDirectory /inheritance:r | Out-Null
icacls.exe $UserSshDirectory /grant:r `
    "${AccountName}:(OI)(CI)F" `
    "*S-1-5-18:(OI)(CI)F" | Out-Null
icacls.exe $UserSshDirectory /setowner "$AccountName" | Out-Null

icacls.exe $UserKeyFile /inheritance:r | Out-Null
icacls.exe $UserKeyFile /grant:r `
    "${AccountName}:F" `
    "*S-1-5-18:F" | Out-Null
icacls.exe $UserKeyFile /setowner "$AccountName" | Out-Null

# Shared authorized_keys used by Windows administrator accounts.
$AdminKeyFile = Join-Path $env:ProgramData `
    "ssh\administrators_authorized_keys"

Set-Content $AdminKeyFile -Value $PublicKey -Encoding ASCII

# S-1-5-32-544 = Administrators; S-1-5-18 = SYSTEM.
icacls.exe $AdminKeyFile /inheritance:r | Out-Null
icacls.exe $AdminKeyFile /grant:r `
    "*S-1-5-32-544:F" `
    "*S-1-5-18:F" | Out-Null

Restart-Service sshd

Write-Host "SSH setup complete."
Write-Host "User key:  $UserKeyFile"
Write-Host "Admin key: $AdminKeyFile"
