# Backend .env Auto-Generation Script
# This script copies backend/.env.example to backend/.env if missing,
# then patches values for development environment

# Define paths
$BackendDir = Join-Path $PSScriptRoot "backend"
$EnvExamplePath = Join-Path $BackendDir ".env.example"
$EnvPath = Join-Path $BackendDir ".env"

# Ensure backend directory exists
if (-Not (Test-Path $BackendDir)) {
    Write-Error "Backend directory not found: $BackendDir"
    exit 1
}

# Check if .env.example exists
if (-Not (Test-Path $EnvExamplePath)) {
    Write-Error ".env.example not found: $EnvExamplePath"
    exit 1
}

# Copy .env.example to .env if .env doesn't exist
if (-Not (Test-Path $EnvPath)) {
    Copy-Item -Path $EnvExamplePath -Destination $EnvPath
    Write-Host "✓ Created .env file from .env.example" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Yellow
}

# Function to replace or add a line in the .env file
function Set-EnvValue {
    param (
        [string]$FilePath,
        [string]$Key,
        [string]$Value
    )
    
    # Read all lines and create a list
    $lines = Get-Content $FilePath
    $isUpdated = $false

    # Create regex pattern to match the key
    $pattern = "^$([Regex]::Escape($Key))="

    # Iterate over each line
    $lines = $lines | ForEach-Object {
        if ($_ -match $pattern) {
            # Replace existing value
            "${Key}=${Value}"
            $isUpdated = $true
        } else {
            # Return untouched
            $_
        }
    }

    # If not updated, add new pair
    if (-not $isUpdated) {
        $lines += "${Key}=${Value}"
        Write-Host "✓ Added $Key=$Value" -ForegroundColor Green
    } else {
        Write-Host "✓ Updated $Key=$Value" -ForegroundColor Cyan
    }

    # Write updated content back to file
    Set-Content -Path $FilePath -Value $lines
}

Write-Host "Patching .env file for development environment..." -ForegroundColor Blue

# Development environment patches
try {
    # Ensure DEBUG is true for development
    Set-EnvValue -FilePath $EnvPath -Key "DEBUG" -Value "true"
    
    # Set CORS origins for local development
    Set-EnvValue -FilePath $EnvPath -Key "CORS_ORIGINS" -Value "http://localhost:3000"
    
    # Set host to localhost for development
    Set-EnvValue -FilePath $EnvPath -Key "HOST" -Value "localhost"
    
    # Ensure log level is appropriate for development
    Set-EnvValue -FilePath $EnvPath -Key "LOG_LEVEL" -Value "DEBUG"
    
    Write-Host "`n✅ Backend .env file successfully configured for development!" -ForegroundColor Green
    Write-Host "Location: $EnvPath" -ForegroundColor Gray
    
} catch {
    Write-Error "Failed to patch .env file: $_"
    exit 1
}

Write-Host "`nDevelopment environment ready! The .env file has been configured with:" -ForegroundColor Yellow
Write-Host "  • DEBUG=true" -ForegroundColor Gray
Write-Host "  • CORS_ORIGINS=http://localhost:3000" -ForegroundColor Gray
Write-Host "  • HOST=localhost" -ForegroundColor Gray
Write-Host "  • LOG_LEVEL=DEBUG" -ForegroundColor Gray
