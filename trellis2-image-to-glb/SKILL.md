---
name: trellis2-image-to-glb
description: Create a textured GLB from object images with standalone TRELLIS.2, automatically selecting and validating local dependencies for the user's hardware, then verify multiple views. Use for TRELLIS.2 image-to-3D or production GLB requests. Use ComfyUI only when explicitly requested. Do not use for Gaussian Splatting or manual polygon modeling.
---

# TRELLIS.2 Image to GLB

Produce the actual GLB, not only setup instructions or workflow JSON. Preserve the user's source images and existing working environments. Do not claim success until the GLB has been reopened, visually inspected from multiple directions, and checked for embedded texture and material data.

Read [references/standalone.md](references/standalone.md) before execution. Read the older [ComfyUI workflow](references/workflow.md) only when the user explicitly requests ComfyUI; its ComfyUI-first routing does not apply to standalone jobs.

## Bundled standalone automation

On a compatible Windows NVIDIA machine, use `scripts/install_windows.ps1` to create the isolated Python 3.11/CUDA 12.8 runtime, install the exact standalone packages and compiled wheels, clone the official TRELLIS.2 source, and execute CUDA, attention, sparse convolution, rasterization, textured GLB, and pipeline-import tests. This wheel source is a binary source only; the script never installs or starts ComfyUI. Pass `-DownloadModels` for an actual generation job so `scripts/download_models.py` fetches only the selected TRELLIS.2 checkpoints, the public DINOv3 encoder, and BiRefNet files.

Run `scripts/run_image_to_glb.py` with the prepared runtime and source image. It preserves the input, uses the public encoder through a local standalone pipeline configuration, embeds the texture in the GLB, and leaves `visual_validation` pending. Render and inspect front, side, back, and three-quarter views before declaring completion.

## Intake and geometry confidence

Open every supplied image. Decide whether the input is:

- `sufficient` — the major silhouette, depth, openings, supports, and asymmetric parts are observable;
- `needs structure reference` — a hidden side or critical connection could change the geometry;
- `needs target selection` — multiple objects are present and the requested target is ambiguous.

Ask for a specific missing angle only when the absent evidence materially changes the model. Continue safe environment checks while waiting, but do not treat silence as permission to invent critical geometry. Never present a generated back or mirrored view as observed evidence.

## Environment routing

Inspect the OS, GPU/VRAM, driver, RAM, free storage, Python, PyTorch/CUDA and model cache before installing anything. The default is a standalone Python pipeline with no ComfyUI server, nodes, or queue dependency. Check ComfyUI only when the user explicitly requests that route.

Use this order:

1. Reuse a verified standalone TRELLIS.2 environment.
2. Repair only missing components when that will not destabilize existing workflows.
3. Otherwise create an isolated standalone environment, selecting Python, PyTorch/CUDA, attention and compiled extensions together from the actual hardware and available binaries. Do not replace drivers just to match a newer wheel.
4. Use the official direct pipeline; on Windows, compatible maintained extension wheels may be sourced independently of their ComfyUI wrapper. Verify they work without importing ComfyUI.

Complete all independent local setup before reporting a model-access blocker: install compatible dependencies, run CUDA forward/backward checks, exercise dense and sparse attention and mesh/rasterization extensions, and check the export path. Track environment readiness and model-access readiness separately. A gated encoder does not block dependency installation. Never report a completed runtime from import-only checks or a generated model from setup alone.

Do not proceed with a large installation when hardware is clearly incompatible. TRELLIS.2 support, wrappers, model access, wheels, and GPU requirements change; check the current official repositories before choosing versions. New cloud cost, external upload, account access, driver replacement, reboot, or disruption of a running queue requires user involvement.

## Generation invariants

- Preserve the original input and make normalized working copies.
- Validate alpha or background removal; do not compute a crop from an empty mask.
- Use only real supplied views in multiview slots and verify each slot's direction semantics.
- Connect both geometry and texture paths through decode, UV/texturing, and GLB export.
- Distinguish geometry resolution from texture resolution and record the seed and settings.
- Do not fill intended holes or delete small functional parts as noise.
- Track versions, model sources, commands, inputs, assumptions, and outputs in `run_manifest.json` without secrets.

## Verification and delivery

Reopen the final GLB and check finite geometry, plausible scale, UVs, PBR material references, embedded base-color texture, face orientation, separated or floating parts, silhouette, depth, and observed part count. Render front, three-quarter, side, and back previews. Mark unobserved surfaces as estimated.

Deliver:

- `<object>_textured.glb`;
- `<object>_preview.png` with several viewpoints;
- reproducible workflow or run script and settings;
- `run_manifest.json` with validation results and assumptions.

If generation is blocked, report the exact blocker and the smallest required user action. Installation alone is not completion.
