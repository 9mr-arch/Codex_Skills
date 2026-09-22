[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $RuntimeRoot,
    [switch] $InstallSystemTools,
    [switch] $DownloadModels
)

$ErrorActionPreference = 'Stop'
$RuntimeRoot = [IO.Path]::GetFullPath($RuntimeRoot)
$SkillRoot = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force -Path $RuntimeRoot, (Join-Path $RuntimeRoot 'logs') | Out-Null

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
    throw 'Standalone TRELLIS.2 on Windows requires a supported NVIDIA GPU and driver.'
}
$gpuCsv = & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits | Select-Object -First 1
$gpuParts = $gpuCsv -split ',' | ForEach-Object Trim
if ([int]$gpuParts[1] -lt 22000) {
    throw "TRELLIS.2 needs about 24GB VRAM for this tested route; detected $($gpuParts[1]) MiB."
}

if ($InstallSystemTools) {
    if (-not (Resolve-Command 'git.exe')) {
        winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements
    }
    if (-not (Get-Command py.exe -ErrorAction SilentlyContinue)) {
        winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements
    }
    Refresh-ProcessPath
}
if (-not (Resolve-Command 'git.exe')) { throw 'Git is required. Re-run with -InstallSystemTools.' }
$PythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if (-not $PythonLauncher) { throw 'Python launcher not found. Re-run with -InstallSystemTools.' }
& $PythonLauncher.Source -3.11 -c 'import sys; assert sys.version_info[:2] == (3, 11)'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 is required. Re-run with -InstallSystemTools.' }

$EnvDir = Join-Path $RuntimeRoot 'env'
if (-not (Test-Path (Join-Path $EnvDir 'Scripts\python.exe'))) {
    & $PythonLauncher.Source -3.11 -m venv $EnvDir
}
$Python = Join-Path $EnvDir 'Scripts\python.exe'
& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128
& $Python -m pip install xformers==0.0.32.post2 --index-url https://download.pytorch.org/whl/cu128
& $Python -m pip install 'triton-windows>=3.4,<3.5'
& $Python -m pip install -r (Join-Path $SkillRoot 'dependencies\windows-cu128.txt')

$SourceDir = Join-Path $RuntimeRoot 'TRELLIS.2'
if (-not (Test-Path (Join-Path $SourceDir '.git'))) {
    git clone --recursive https://github.com/microsoft/TRELLIS.2.git $SourceDir
}
$WheelSource = Join-Path $RuntimeRoot 'ComfyUI-Trellis2-wheel-source'
if (-not (Test-Path (Join-Path $WheelSource '.git'))) {
    git clone --depth 1 https://github.com/visualbruno/ComfyUI-Trellis2.git $WheelSource
}
$WheelDir = Join-Path $WheelSource 'wheels\Windows\Torch280'
if (-not (Test-Path -LiteralPath $WheelDir -PathType Container)) {
    throw "The tested Torch 2.8 Windows wheel set is missing: $WheelDir"
}
$patterns = @('cumesh-*-cp311-cp311-win_amd64.whl', 'o_voxel-*-cp311-cp311-win_amd64.whl',
              'flex_gemm-*-cp311-cp311-win_amd64.whl', 'nvdiffrast-*-cp311-cp311-win_amd64.whl',
              'nvdiffrec_render-*-cp311-cp311-win_amd64.whl', 'custom_rasterizer-*-cp311-cp311-win_amd64.whl')
foreach ($pattern in $patterns) {
    $wheel = Get-ChildItem -LiteralPath $WheelDir -Filter $pattern -File | Sort-Object Name | Select-Object -Last 1
    if (-not $wheel) { throw "Required Windows wheel not found: $pattern" }
    & $Python -m pip install $wheel.FullName
}

if ($DownloadModels) {
    & $Python (Join-Path $PSScriptRoot 'download_models.py') --runtime-root $RuntimeRoot --pipeline 1024_cascade
    if ($LASTEXITCODE -ne 0) { throw 'Selective model download failed.' }
}

$env:TRELLIS2_SOURCE = $SourceDir
& $Python (Join-Path $PSScriptRoot 'verify_runtime.py') --runtime-root $RuntimeRoot
if ($LASTEXITCODE -ne 0) { throw 'TRELLIS.2 runtime validation failed. See runtime_validation.json.' }
@{
    runtime_root = $RuntimeRoot
    python = $Python
    source = $SourceDir
    source_commit = (git -C $SourceDir rev-parse HEAD)
    wheel_source_commit = (git -C $WheelSource rev-parse HEAD)
    gpu = $gpuParts[0]
    vram_mib = [int]$gpuParts[1]
    driver = $gpuParts[2]
    runtime_status = 'ready'
    model_status = $(if ($DownloadModels) { 'downloaded' } else { 'not_requested' })
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $RuntimeRoot 'environment.json') -Encoding UTF8
Write-Host "Standalone TRELLIS.2 runtime ready: $RuntimeRoot"
