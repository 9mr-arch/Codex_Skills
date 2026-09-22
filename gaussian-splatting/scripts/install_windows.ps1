[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $RuntimeRoot,
    [switch] $InstallSystemTools
)

$ErrorActionPreference = 'Stop'
$RuntimeRoot = [IO.Path]::GetFullPath($RuntimeRoot)
$SkillRoot = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $RuntimeRoot 'logs'
New-Item -ItemType Directory -Force -Path $RuntimeRoot, $LogDir | Out-Null

function Resolve-Command([string] $Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    return $null
}

function Refresh-ProcessPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machinePath;$userPath"
}

if (-not (Resolve-Command 'nvidia-smi.exe')) {
    throw 'A supported NVIDIA GPU and driver are required for this Windows gsplat runtime.'
}
if ($InstallSystemTools) {
    if (-not (Resolve-Command 'git.exe')) {
        winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements
    }
    if (-not (Resolve-Command 'ffmpeg.exe')) {
        winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
    }
    if (-not (Get-Command py.exe -ErrorAction SilentlyContinue)) {
        winget install --id Python.Python.3.10 -e --accept-package-agreements --accept-source-agreements
    }
    Refresh-ProcessPath
}

if (-not (Resolve-Command 'git.exe') -or -not (Resolve-Command 'ffmpeg.exe') -or -not (Resolve-Command 'ffprobe.exe')) {
    throw 'Git and FFmpeg/ffprobe are required. Re-run with -InstallSystemTools.'
}

$PythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if (-not $PythonLauncher) { throw 'Python launcher not found. Re-run with -InstallSystemTools.' }
& $PythonLauncher.Source -3.10 -c 'import sys; assert sys.version_info[:2] == (3, 10)'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 is required. Re-run with -InstallSystemTools.' }

$EnvDir = Join-Path $RuntimeRoot 'env'
if (-not (Test-Path (Join-Path $EnvDir 'Scripts\python.exe'))) {
    & $PythonLauncher.Source -3.10 -m venv $EnvDir
}
$Python = Join-Path $EnvDir 'Scripts\python.exe'
& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu124
& $Python -m pip install ninja jaxtyping rich
& $Python -m pip install 'gsplat==1.5.3+pt24cu124' --index-url https://docs.gsplat.studio/whl
& $Python -m pip install -r (Join-Path $SkillRoot 'dependencies\windows-cu124.txt')

$GsplatDir = Join-Path $RuntimeRoot 'gsplat'
if (-not (Test-Path (Join-Path $GsplatDir '.git'))) {
    git clone --branch v1.5.3 --depth 1 https://github.com/nerfstudio-project/gsplat.git $GsplatDir
}

$ToolsDir = Join-Path $RuntimeRoot 'tools'
$ColmapDir = Join-Path $ToolsDir 'colmap'
if (-not (Test-Path (Join-Path $ColmapDir 'COLMAP.bat'))) {
    New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null
    $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/colmap/colmap/releases/latest'
    $asset = $release.assets | Where-Object name -eq 'colmap-x64-windows-cuda.zip' | Select-Object -First 1
    if (-not $asset) { throw 'Official COLMAP Windows CUDA release asset was not found.' }
    $archive = Join-Path $ToolsDir $asset.name
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $archive
    $stage = Join-Path $ToolsDir '_colmap_extract'
    if (Test-Path $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    Expand-Archive -LiteralPath $archive -DestinationPath $stage -Force
    $launcher = Get-ChildItem -LiteralPath $stage -Filter COLMAP.bat -File -Recurse | Select-Object -First 1
    if (-not $launcher) { throw 'Downloaded COLMAP archive did not contain COLMAP.bat.' }
    Move-Item -LiteralPath $launcher.Directory.FullName -Destination $ColmapDir
    if (Test-Path $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}

$env:GAUSSIAN_RUNTIME_ROOT = $RuntimeRoot
$env:COLMAP_BAT = Join-Path $ColmapDir 'COLMAP.bat'
& $Python (Join-Path $PSScriptRoot 'verify_runtime.py') --runtime-root $RuntimeRoot
if ($LASTEXITCODE -ne 0) { throw 'Gaussian runtime validation failed. See runtime_validation.json.' }

@{
    runtime_root = $RuntimeRoot
    python = $Python
    colmap = $env:COLMAP_BAT
    gsplat_source = $GsplatDir
    status = 'ready'
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $RuntimeRoot 'environment.json') -Encoding UTF8
Write-Host "Gaussian runtime ready: $RuntimeRoot"
