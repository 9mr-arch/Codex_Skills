# Standalone TRELLIS.2: image to verified textured GLB

## Discover and select the runtime

Inspect OS, NVIDIA GPU/VRAM, driver, RAM, free storage, existing Python environments and model cache. Reuse a verified standalone environment; otherwise install an isolated environment in the task's work directory. Do not install or start ComfyUI for this route.

Read the current official `microsoft/TRELLIS.2` README, setup script, pipeline configuration and example. Match Python ABI, PyTorch version, CUDA runtime, driver and compiled extensions before large downloads. Official Linux support is distinct from community Windows support. Windows wheels from a maintained wrapper can be used as standalone binary packages only after checking their metadata, imports and actual execution. Do not pretend an untested wheel combination is supported.

Required paths commonly include CuMesh, O-Voxel, FlexGEMM, nvdiffrast and an attention backend; derive the exact list from the selected source revision. Check dense and sparse attention separately. Setting dense attention to SDPA does not guarantee sparse attention uses it. Avoid installing unrelated UI, training or experimental dependencies.

Install automatically within the user's authorized local setup scope. Use official sources or identified maintained binary releases. Preserve existing environments. Record commits, wheel sources, hashes, package versions and install logs. Do not replace a GPU driver or reboot to fit a newer binary without user involvement.

## Two independent readiness states

Track `runtime_status` and `model_access_status` separately. Check gated models early, but finish independent installation and smoke tests even if authentication is missing. Reuse an existing authenticated session. Never copy secrets into logs or manifests, bypass a model access gate, or confuse anonymous HTTP 401 with hardware incompatibility.

For this user's standalone setup, use the public encoder repository `visualbruno/dinov3-vitl16-pretrain-lvd1689m`, also referenced by ComfyUI-Trellis2, and load its downloaded directory through a local pipeline config. Verify current availability, configuration, revision and source; record them in the manifest. Do not force a request to the gated `facebook/` endpoint when using this configured public source. Preserve the model's license. Public background model `ZhengPeng7/BiRefNet` is supported by the official BiRefNet adapter and avoids adding an unnecessary RMBG-2.0 account dependency. Verify the actual model load and preprocessing rather than assuming checkpoint compatibility.

Runtime checks must execute CUDA forward/backward, dense and sparse attention, a small sparse convolution, CUDA rasterization, mesh processing and a textured GLB round trip. Run tests with the same interpreter and environment used for generation. Save exact errors and fix the actual missing component. If a test remains broken, mark the relevant path as failed rather than declaring the environment ready.

Only ask the user to perform the remaining personal login/model-access consent after independent work is complete. Provide a concrete local login route, identify the specific model and preserve the prepared environment for continuation. Do not ask the user to install Python, ComfyUI or dependencies manually.

## Prepare and generate

Preserve the input and record its hash. Inspect the real image and determine if major geometry is sufficiently visible. Ask for reference only when critical structure cannot be determined; do not request extra views by habit. Never put mirrored or invented images into measured-view inputs.

Normalize orientation, remove background on a working copy using a real segmentation model, validate that alpha is nonempty and the object is intact, crop with margin and inspect the prepared input. Check the chosen pipeline's preprocessing code before supplying RGB or RGBA. Never compute bounds from an empty mask.

Write a standalone CLI/run script using the actual official pipeline signatures. Configure attention before imports. Use stage-wise model offloading/low-VRAM mode when supported. Record seed, shape resolution, texture resolution and settings. Start from settings appropriate to measured available VRAM, not a blanket highest resolution. Decode both shape and texture, then UV unwrap and bake materials to embedded images before GLB export. Do not fill intended openings or delete small parts by default.

## Validate and deliver

Reopen the GLB independently and check finite vertices, indices, UVs, PBR material assignments, embedded base-color image and any generated metallic/roughness channels. Render front, side, back and three-quarter views in a compatible renderer. Compare observed silhouette, parts and texture to the source. Label unseen surfaces and scale as estimated. Correct visible failures before declaring completion.

Deliver the textured GLB, multi-view preview, reproducible standalone script/settings and `run_manifest.json`. Record runtime tests separately from actual model inference and asset verification. Installation or a successful smoke-test GLB is not a generated product asset.

Sources to inspect at execution time:
- https://github.com/microsoft/TRELLIS.2
- https://huggingface.co/microsoft/TRELLIS.2-4B
- https://github.com/visualbruno/ComfyUI-Trellis2/tree/main/wheels
