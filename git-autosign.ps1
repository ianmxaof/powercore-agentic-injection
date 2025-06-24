param(
    [string]$Message = "Auto commit via script"
)

# Stage all changes
git add -A

# Commit with GPG signing enabled explicitly (just in case)
git commit -S -m "$Message"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Git commit failed. Check changes or GPG config."
    exit 1
}

# Push to the current branch upstream
git push

if ($LASTEXITCODE -ne 0) {
    Write-Error "Git push failed. Check remote and network."
    exit 1
}

Write-Host "Commit and push completed successfully!"
