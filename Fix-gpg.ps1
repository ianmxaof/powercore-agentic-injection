# Fix-gpg.ps1

# Path to gpg.conf
$gpgConfPath = "$env:USERPROFILE\.gnupg\gpg.conf"

# Backup old config if exists
if (Test-Path $gpgConfPath) {
    Copy-Item $gpgConfPath "$gpgConfPath.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
}

# Write only the correct option, overwrite existing file
"no-use-keyboxd" | Out-File -Encoding ASCII -FilePath $gpgConfPath -Force

# Restart gpg-agent cleanly
gpgconf --kill gpg-agent
Start-Sleep -Seconds 1
gpgconf --launch gpg-agent

Write-Host "✅ gpg.conf fixed and gpg-agent restarted."
