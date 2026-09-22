---
name: trellis2-image-to-glb
description: Create a textured, material-bearing GLB from one or more object images with TRELLIS.2, using an existing or isolated ComfyUI/direct environment, and verify the exported asset from multiple views. Use when a user asks to convert object photos into a TRELLIS.2 3D model or production GLB. Do not use for Gaussian Splatting, manual polygon modeling, or requests that only need a render.
---

# TRELLIS.2 Image to GLB

Produce the actual GLB, not only setup instructions or workflow JSON. Preserve the user's source images and existing working environments. Do not claim success until the GLB has been reopened, visually inspected from multiple directions, and checked for embedded texture and material data.

Read [references/workflow.md](references/workflow.md) before taking implementation actions. It contains the environment discovery, installation, image preparation, ComfyUI/direct-pipeline, export, and verification procedure.

## Intake and geometry confidence

Open every supplied image. Decide whether the input is:

- `sufficient` — the major silhouette, depth, openings, supports, and asymmetric parts are observable;
- `needs structure reference` — a hidden side or critical connection could change the geometry;
- `needs target selection` — multiple objects are present and the requested target is ambiguous.

Ask for a specific missing angle only when the absent evidence materially changes the model. Continue safe environment checks while waiting, but do not treat silence as permission to invent critical geometry. Never present a generated back or mirrored view as observed evidence.

## Environment routing

Inspect the OS, GPU/VRAM, driver, RAM, free storage, Python, PyTorch/CUDA, ComfyUI installation, custom nodes, model cache, and any running queue before installing anything.

Use this order:

1. Reuse a verified TRELLIS.2 environment.
2. Repair only missing components when that will not destabilize existing workflows.
3. Create an isolated task environment when dependency changes could break the user's setup.
4. Use a verified direct official pipeline when it is more appropriate than ComfyUI.

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
