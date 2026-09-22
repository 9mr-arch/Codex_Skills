"""Run the official TRELLIS.2 pipeline standalone and export a textured GLB."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--runtime-root", type=Path, required=True)
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--pipeline", choices=("512", "1024_cascade"), default="1024_cascade")
parser.add_argument("--texture-size", type=int, default=2048)
args = parser.parse_args()
root = args.runtime_root.resolve()
if args.output.exists():
    parser.error("Output exists; choose a new versioned filename.")
os.environ["ATTN_BACKEND"] = "sdpa"
os.environ["SPARSE_ATTN_BACKEND"] = "xformers"
os.environ["FLEX_GEMM_USE_AUTOTUNE_CACHE"] = "0"
os.environ["FLEX_GEMM_AUTOSAVE_AUTOTUNE_CACHE"] = "0"
sys.path.insert(0, str(root / "TRELLIS.2"))

from PIL import Image, ImageOps
import numpy as np
import torch
import trimesh
from o_voxel import postprocess
from trellis2.pipelines import Trellis2ImageTo3DPipeline

models = root / "models"
dino = models / "dinov3"
pipeline_json = models / "trellis2" / "pipeline.json"
if not pipeline_json.is_file() or not (dino / "model.safetensors").is_file():
    parser.error("Required model files are missing; run install_windows.ps1 with -DownloadModels.")
config = json.loads(pipeline_json.read_text(encoding="utf-8"))
unused = ["tex_slat_flow_model_512"] if args.pipeline == "1024_cascade" else ["shape_slat_flow_model_1024", "tex_slat_flow_model_1024"]
for key in unused:
    config["args"]["models"].pop(key, None)
for key, value in config["args"]["models"].items():
    source = models / ("trellis-image-large" if key == "sparse_structure_decoder" else "trellis2")
    config["args"]["models"][key] = str((source / ("ckpts/" + value.split("ckpts/", 1)[1])).resolve())
config["args"]["image_cond_model"]["args"]["model_name"] = str(dino.resolve())
config["args"]["rembg_model"]["args"]["model_name"] = "ZhengPeng7/BiRefNet"
config_dir = root / "standalone_pipeline"
config_dir.mkdir(exist_ok=True)
(config_dir / "pipeline.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

args.output.parent.mkdir(parents=True, exist_ok=True)
manifest_path = args.output.with_suffix(".run.json")
manifest = {
    "state": "generating", "input": str(args.input.resolve()),
    "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
    "seed": args.seed, "pipeline": args.pipeline, "texture_size": args.texture_size,
    "unobserved_surfaces": "estimated", "scale": "not measured",
    "backend": "standalone official TRELLIS.2", "visual_validation": "pending",
    "encoder_source": "visualbruno/dinov3-vitl16-pretrain-lvd1689m",
}
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
image = ImageOps.exif_transpose(Image.open(args.input)).convert("RGB")
pipeline = Trellis2ImageTo3DPipeline.from_pretrained(str(config_dir))
pipeline.low_vram = True
pipeline.cuda()
prepared = pipeline.preprocess_image(image)
prepared.save(args.output.with_suffix(".input.png"))
mesh = pipeline.run(prepared, seed=args.seed, preprocess_image=False, pipeline_type=args.pipeline)[0]
mesh.simplify(16_777_216)
glb = postprocess.to_glb(vertices=mesh.vertices, faces=mesh.faces, attr_volume=mesh.attrs,
    coords=mesh.coords, attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
    aabb=[[-0.5] * 3, [0.5] * 3], decimation_target=200_000,
    texture_size=args.texture_size, remesh=False, verbose=True)
glb.export(args.output, extension_webp=False)
scene = trimesh.load(args.output, force="scene")
assert scene.geometry
for geometry in scene.geometry.values():
    assert len(geometry.faces) and np.isfinite(geometry.vertices).all()
    assert geometry.visual.uv is not None and geometry.visual.material.baseColorTexture is not None
manifest.update(state="generated_requires_visual_validation", output=str(args.output.resolve()),
    output_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(), bytes=args.output.stat().st_size,
    geometry_roundtrip="passed")
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
