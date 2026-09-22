---
name: gaussian-splatting
description: Reconstruct a Gaussian Splatting asset from a single image, multiple photos, or video; export validated Gaussian and Blender-compatible PLY files; and verify the result with rendered views. Use for 3DGS, Gaussian PLY, NullSplat, camera alignment, training, cleanup, or Blender Gaussian workflows. Do not use for ordinary video conversion or polygon-mesh modeling.
---

# Gaussian Splatting Reconstruction

Create and validate the actual Gaussian asset. Do not stop at commands, environment setup, a generic RGB point cloud, or an unfinished training run.

Read [references/workflow.md](references/workflow.md) before execution. It contains detailed procedures for input inspection, environment setup, camera registration, training, cleanup, PLY encoding, Blender compatibility, and quality assurance.

## Select the reconstruction lane

- **Single image:** use a verified single-image Gaussian prediction model. Label the result `single_image_estimated`; do not describe hidden surfaces as measured or promise a complete 360-degree scan.
- **Multiple photos or video:** use genuinely distinct viewpoints, estimate cameras, and train a static-scene 3DGS pipeline. Reuse a working NullSplat environment when available; otherwise choose a maintained COLMAP/gsplat-based implementation with a complete loader, initialization, training, saving, and rendering path.

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
