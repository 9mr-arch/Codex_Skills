[CmdletBinding()]
param(
    [string[]]$Names,
    [string]$DestinationRoot = (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.agents\skills'),
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$destinationRoot = [System.IO.Path]::GetFullPath($DestinationRoot)

$available = Get-ChildItem -LiteralPath $packageRoot -Directory |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }

if (-not $available) {
    throw "No skill folders were found under $packageRoot"
}

if ($Names) {
    $requested = @($Names | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    $unknown = @($requested | Where-Object { $_ -notin $available.Name })
    if ($unknown.Count -gt 0) {
        throw "Unknown skill name(s): $($unknown -join ', '). Available: $($available.Name -join ', ')"
    }
    $selected = @($available | Where-Object { $_.Name -in $requested })
} else {
    $selected = @($available)
}

foreach ($skill in $selected) {
    $targetPath = Join-Path $destinationRoot $skill.Name
    if ((Test-Path -LiteralPath $targetPath) -and -not $Force) {
        throw "Skill already exists: $targetPath. Re-run with -Force to update it."
    }
}
New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null

foreach ($skill in $selected) {
    $destination = Join-Path $destinationRoot $skill.Name
    if ((Test-Path -LiteralPath $destination) -and -not $Force) {
        throw "Skill already exists: $destination. Re-run with -Force to update it."
    }
    Copy-Item -LiteralPath $skill.FullName -Destination $destinationRoot -Recurse -Force:$Force
    Write-Host "Installed $($skill.Name) -> $destination"
}

Write-Host "Installed $($selected.Count) skill(s). Restart or refresh Codex if the skills are not listed yet."
