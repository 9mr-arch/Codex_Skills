---
name: gaussian-splatting
description: Reconstruct Gaussian Splatting from video or multiple real viewpoints using COLMAP camera estimation and a complete 3DGS trainer; export validated Gaussian and Blender-compatible PLY files with rendered previews. Use for video-to-3DGS, Gaussian PLY, NullSplat, alignment, training or Blender Gaussian workflows. Do not use for ordinary video conversion or polygon modeling.
---

# Gaussian Splatting Reconstruction

Create and validate the actual Gaussian asset. Do not stop at commands, environment setup, a generic RGB point cloud, or an unfinished training run.

Read [references/workflow.md](references/workflow.md) before execution. It contains detailed procedures for input inspection, environment setup, camera registration, training, cleanup, PLY encoding, Blender compatibility, and quality assurance.

## Bundled standalone automation

On a compatible Windows NVIDIA machine, use `scripts/install_windows.ps1` to create the isolated Python 3.10/CUDA 12.4 runtime, install the tested prebuilt gsplat wheel, download the official COLMAP CUDA binary, install FFmpeg when requested, and execute the real CUDA/PLY/tool smoke tests. Then use `scripts/run_video_to_gaussian.ps1` for frame extraction, COLMAP registration and undistortion, gsplat training, Gaussian PLY export, and Blender RGB PLY conversion. Do not replace these scripts with hand-written partial setup unless the detected platform or current upstream compatibility requires another lane.

The installer intentionally keeps system tools, runtime packages, and job data separate. Pass `-InstallSystemTools` only when Git, FFmpeg, or Python 3.10 is absent. The runner refuses to overwrite an existing job directory. After it finishes, render and inspect representative registered views before changing the manifest from `trained_requires_visual_validation` to complete.

## Select the reconstruction lane

- **Video (default) or multiple photos:** extract sharp, overlapping real viewpoints across the full clip, estimate cameras with COLMAP, and train a static-scene 3DGS pipeline. Reuse a working compatible environment; otherwise install an isolated maintained COLMAP/gsplat pipeline with a complete loader, initialization, training, saving, and rendering path. COLMAP estimates cameras and sparse geometry; it does not itself train Gaussian splats.
- **Only one image supplied:** explain that the video reconstruction route needs actual multiview video/photos and request that input. Do not silently switch to SHARP or create artificial duplicates. Only investigate a single-image estimator when the user explicitly chooses that separate route; label it `single_image_estimated`.

Evaluate licenses per selected component, including trainer, weights and renderer. SHARP's research-only restriction does not apply to COLMAP or Gaussian Splatting as a whole. Prefer a license-compatible video pipeline and do not ask a research-only usage question merely because SHARP exists. A permissive COLMAP license alone does not establish the license of a separate trainer.

Do not duplicate one image into an SfM dataset. Detect insufficient parallax, object deformation, moving subjects, state changes, and fixed-camera turntables before deciding that standard static-scene SfM is valid.

## Environment and data discipline

Inspect current hardware, drivers, storage, Python environments, Blender, and existing reconstruction tools before installing. Prefer official repositories and compatible binaries. Keep incompatible model families in separate environments and validate CUDA forward and backward operations, PLY round trips, and Blender launch rather than relying on imports alone.

Preserve originals and create a versioned job folder with input metadata, hashes, selected frames, configuration, logs, checkpoints, and delivery outputs. Never delete recoverable user data or overwrite an accepted result.

For video and photo sets, sample the full requested range with sufficient overlap, parallax, sharpness, and coverage. Record the mapping between source frame, timestamp, and training image. Verify registered-camera distribution, missing intervals, reprojection quality, and whether critical rear or upper views belong to the same connected reconstruction.

## Training and cleanup

Set image resolution, frame count, Gaussian cap, densification schedule, and checkpoints from measured VRAM and a short pilot run. Preserve headroom for other applications. Respond to OOM by fixing the effective memory drivers rather than blindly repeating the same command.

Keep trained originals and perform background or object cleanup on copies. Validate cropping and cleanup with source-aligned renders; do not remove thin parts, floors, entrances, or detached-looking features solely from coordinate assumptions or largest-component heuristics.

## Output and verification

Export a true Gaussian PLY with the implementation's verified position, spherical-harmonic color, opacity, scale, and rotation encoding. Also create a color-compatible Blender RGB PLY when useful, but clearly distinguish it from the full Gaussian representation.

Reopen and validate each file for NaN/Inf values, point and property counts, quaternion behavior, opacity, color distribution, bounds, byte length, coordinate system, and scale. Test the recommended Gaussian PLY in a compatible renderer or Blender add-on; Blender's basic PLY importer is not proof of Gaussian support.

Deliver the recommended Gaussian PLY, Blender RGB PLY, optional web format, validated preview renders, optional `.blend`, and a manifest recording inputs, tools, commits, settings, coverage, cleanup, validation, hashes, coordinates, and limitations. State separately what was generated, Gaussian-render verified, and Blender verified.
