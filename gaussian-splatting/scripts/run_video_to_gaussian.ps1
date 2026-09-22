[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $RuntimeRoot,
    [Parameter(Mandatory = $true)] [string] $Video,
    [Parameter(Mandatory = $true)] [string] $JobRoot,
    [ValidateRange(40, 1200)] [int] $MaxFrames = 400,
    [ValidateRange(1000, 100000)] [int] $Steps = 30000
)

$ErrorActionPreference = 'Stop'
$RuntimeRoot = [IO.Path]::GetFullPath($RuntimeRoot)
$Video = [IO.Path]::GetFullPath($Video)
$JobRoot = [IO.Path]::GetFullPath($JobRoot)
if (-not (Test-Path -LiteralPath $Video -PathType Leaf)) { throw "Video not found: $Video" }
if (Test-Path -LiteralPath $JobRoot) { throw "JobRoot already exists; choose a new versioned folder: $JobRoot" }

$Python = Join-Path $RuntimeRoot 'env\Scripts\python.exe'
$Colmap = Join-Path $RuntimeRoot 'tools\colmap\COLMAP.bat'
$Trainer = Join-Path $RuntimeRoot 'gsplat\examples\simple_trainer.py'
foreach ($required in @($Python, $Colmap, $Trainer)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Runtime component missing: $required" }
}

$Frames = Join-Path $JobRoot 'frames'
$RawSparse = Join-Path $JobRoot 'colmap_raw\sparse'
$Dataset = Join-Path $JobRoot 'dataset'
$Result = Join-Path $JobRoot 'training'
New-Item -ItemType Directory -Force -Path $Frames, $RawSparse, $Dataset, (Join-Path $JobRoot 'logs') | Out-Null
Copy-Item -LiteralPath $Video -Destination (Join-Path $JobRoot ('source' + [IO.Path]::GetExtension($Video)))

$durationText = & ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 -- $Video
$duration = [double]::Parse(($durationText | Select-Object -First 1), [Globalization.CultureInfo]::InvariantCulture)
$fps = [Math]::Min(12.0, [Math]::Max(1.0, $MaxFrames / [Math]::Max($duration, 0.001)))
$fpsText = $fps.ToString('0.######', [Globalization.CultureInfo]::InvariantCulture)
& ffmpeg -hide_banner -loglevel warning -i $Video -vf "fps=$fpsText" -q:v 2 (Join-Path $Frames 'frame_%06d.jpg')
if ($LASTEXITCODE -ne 0) { throw 'Frame extraction failed.' }

$Database = Join-Path $JobRoot 'colmap_raw\database.db'
& $Colmap feature_extractor --database_path $Database --image_path $Frames --ImageReader.single_camera 1 --SiftExtraction.use_gpu 1
if ($LASTEXITCODE -ne 0) { throw 'COLMAP feature extraction failed.' }
& $Colmap sequential_matcher --database_path $Database --SiftMatching.use_gpu 1 --SequentialMatching.loop_detection 1
if ($LASTEXITCODE -ne 0) { throw 'COLMAP matching failed.' }
& $Colmap mapper --database_path $Database --image_path $Frames --output_path $RawSparse
if ($LASTEXITCODE -ne 0) { throw 'COLMAP mapping failed.' }
$Model = Get-ChildItem -LiteralPath $RawSparse -Directory | Sort-Object {
    -((Get-ChildItem -LiteralPath $_.FullName -File | Measure-Object Length -Sum).Sum)
} | Select-Object -First 1
if (-not $Model) { throw 'COLMAP did not create a registered camera model.' }
& $Colmap image_undistorter --image_path $Frames --input_path $Model.FullName --output_path $Dataset --output_type COLMAP
if ($LASTEXITCODE -ne 0) { throw 'COLMAP undistortion failed.' }

Push-Location (Split-Path -Parent $Trainer)
try {
    & $Python $Trainer default --data-dir $Dataset --result-dir $Result --max-steps $Steps --save-ply --disable-viewer --disable-video
    if ($LASTEXITCODE -ne 0) { throw 'gsplat training failed.' }
} finally {
    Pop-Location
}

$Ply = Get-ChildItem -LiteralPath (Join-Path $Result 'ply') -Filter '*.ply' -File | Sort-Object LastWriteTime | Select-Object -Last 1
if (-not $Ply) { throw 'Training completed without a Gaussian PLY.' }
$Delivery = Join-Path $JobRoot 'delivery'
New-Item -ItemType Directory -Force -Path $Delivery | Out-Null
$GaussianOut = Join-Path $Delivery 'scene_gaussian.ply'
Copy-Item -LiteralPath $Ply.FullName -Destination $GaussianOut
& $Python (Join-Path $PSScriptRoot 'gaussian_to_rgb_ply.py') $GaussianOut (Join-Path $Delivery 'scene_blender_rgb.ply')
if ($LASTEXITCODE -ne 0) { throw 'RGB PLY conversion failed.' }

@{
    status = 'trained_requires_visual_validation'
    source_video = $Video
    duration_seconds = $duration
    extracted_frames = (Get-ChildItem -LiteralPath $Frames -File).Count
    registered_model = $Model.FullName
    steps = $Steps
    gaussian_ply = $GaussianOut
    blender_rgb_ply = (Join-Path $Delivery 'scene_blender_rgb.ply')
    visual_validation = 'pending'
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $JobRoot 'run_manifest.json') -Encoding UTF8
Write-Host "Training complete; render validation remains: $GaussianOut"
