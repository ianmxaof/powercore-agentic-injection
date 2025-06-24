param(
    [string]$Message
)

# Ensure GPG path is set (adjust if installed elsewhere)
$env:GPG_TTY = (Get-Process -Id $PID).MainWindowHandle
git config --global gpg.program "C:/Program Files (x86)/GnuPG/bin/gpg.exe"

# Commit with signed flag and message
git commit -S -m $Message
