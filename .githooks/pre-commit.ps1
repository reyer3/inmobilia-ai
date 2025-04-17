# PowerShell version of pre-commit hook for Windows users

Write-Host "Running pre-commit hook to format code..."

# Get a list of staged Python files
$STAGED_FILES = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.py$' }

if ($STAGED_FILES) {
    Write-Host "Formatting Python files with Black and isort..."
    
    # Format with Black
    $STAGED_FILES | ForEach-Object { python -m black $_ }
    
    # Format with isort
    $STAGED_FILES | ForEach-Object { python -m isort $_ }
    
    # Add back the formatted files to staging
    $STAGED_FILES | ForEach-Object { git add $_ }
    
    Write-Host "✅ Code formatting completed successfully!"
} else {
    Write-Host "No Python files to format."
}

# Run lint checks
Write-Host "Running lint checks..."
python -m flake8 src tests
if ($LASTEXITCODE -ne 0) { exit 1 }

python -m mypy --ignore-missing-imports src
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "✅ Pre-commit checks completed successfully!"
exit 0
