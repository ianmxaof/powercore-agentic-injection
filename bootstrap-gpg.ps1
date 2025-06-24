# PowerCore GPG + Git Commit Signing Bootstrapper (PowerShell)
# Patched to force correct homedir to avoid missing keys issue

$gpgHome = "C:\Users\Ian\.gnupg"

# 1. Find your secret keys explicitly in correct homedir
$keyListOutput = & gpg --list-secret-keys --keyid-format=long --homedir $gpgHome
$keyInfo = $keyListOutput | Select-String -Pattern 'sec\s+.*\/([A-F0-9]{16})' -AllMatches

if (-not $keyInfo) {
    Write-Error "No GPG secret keys found in $gpgHome! Generate one first."
    exit 1
}
$keyId = $keyInfo.Matches[0].Groups[1].Value
Write-Host "Found GPG signing key ID: $keyId"

# 2. Configure Git to use this key and sign commits globally
git config --global user.signingkey $keyId
git config --global commit.gpgsign true

# 3. Fix gpg.program path for Git if needed
$gpgPath = (Get-Command gpg).Source
git config --global gpg.program $gpgPath
Write-Host "Set git gpg.program to: $gpgPath"

# 4. Export public key to file for GitHub upload (using forced homedir)
$outputFile = "$env:USERPROFILE\Desktop\gpg-public-key.asc"
& gpg --armor --export $keyId --homedir $gpgHome | Out-File -Encoding ascii $outputFile
Write-Host "Exported public key to $outputFile"
Write-Host "Copy this file's contents to GitHub > Settings > SSH and GPG keys > New GPG key"

Write-Host "`n✅ Bootstrap complete. Test with a signed commit now."
