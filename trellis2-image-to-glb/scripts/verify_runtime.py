"""Exercise the Windows standalone runtime without downloading large weights."""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.runtime_root.resolve()
    source = Path(os.environ.get("TRELLIS2_SOURCE", root / "TRELLIS.2"))
    os.environ["ATTN_BACKEND"] = "sdpa"
    os.environ["SPARSE_ATTN_BACKEND"] = "xformers"
    os.environ["FLEX_GEMM_USE_AUTOTUNE_CACHE"] = "0"
    os.environ["FLEX_GEMM_AUTOSAVE_AUTOTUNE_CACHE"] = "0"
    sys.path.insert(0, str(source))
    import torch

    result = {"python": sys.version, "torch": torch.__version__, "checks": {}}

    def check(name, fn):
        try:
            detail = fn()
            torch.cuda.synchronize()
            result["checks"][name] = {"status": "passed", "detail": detail}
        except Exception:
            result["checks"][name] = {"status": "failed", "error": traceback.format_exc()}
        (root / "runtime_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    def cuda():
        assert torch.cuda.is_available()
        x = torch.rand(32, 32, device="cuda", requires_grad=True)
        (x @ x).sum().backward()
        assert torch.isfinite(x.grad).all()
        return torch.cuda.get_device_name()

    def attention():
        from trellis2.modules.attention import scaled_dot_product_attention
        from trellis2.modules.sparse import VarLenTensor
        from trellis2.modules.sparse.attention import sparse_scaled_dot_product_attention
        qkv = torch.randn(1, 16, 3, 2, 32, device="cuda", dtype=torch.float16)
        dense = scaled_dot_product_attention(qkv)
        sparse = sparse_scaled_dot_product_attention(VarLenTensor(qkv[0]))
        assert torch.isfinite(dense).all() and torch.isfinite(sparse.feats).all()
        return "dense SDPA and sparse xformers"

    def convolution():
        from trellis2.modules.sparse import SparseConv3d, SparseTensor
        xyz = torch.cartesian_prod(*[torch.arange(3, device="cuda")] * 3).int()
        coords = torch.cat([torch.zeros((len(xyz), 1), device="cuda", dtype=torch.int32), xyz], 1)
        value = SparseTensor(torch.randn(len(xyz), 32, device="cuda"), coords)
        with torch.no_grad():
            out = SparseConv3d(32, 32, 3).cuda()(value)
        assert out.feats.shape == (27, 32) and torch.isfinite(out.feats).all()
        return list(out.feats.shape)

    def raster_and_mesh():
        import numpy as np
        import trimesh
        import nvdiffrast.torch as dr
        import cumesh
        from o_voxel import postprocess

        ctx = dr.RasterizeCudaContext()
        vertices4 = torch.tensor([[[-0.8, -0.8, 0, 1], [0.8, -0.8, 0, 1], [0, 0.8, 0, 1]]], device="cuda", dtype=torch.float32, requires_grad=True)
        faces3 = torch.tensor([[0, 1, 2]], device="cuda", dtype=torch.int32)
        rast, _ = dr.rasterize(ctx, vertices4, faces3, resolution=[32, 32])
        rast[..., :2].sum().backward()
        assert torch.isfinite(vertices4.grad).all()
        cube = trimesh.creation.box(extents=[0.7, 0.7, 0.7])
        vertices = torch.tensor(cube.vertices, device="cuda", dtype=torch.float32)
        faces = torch.tensor(cube.faces, device="cuda", dtype=torch.int32)
        mesh = cumesh.CuMesh()
        mesh.init(vertices, faces)
        assert len(mesh.read()[0])
        n = 16
        coords = torch.cartesian_prod(*[torch.arange(n, device="cuda")] * 3).int()
        attrs = torch.tensor([0.7, 0.3, 0.1, 0.2, 0.5, 1.0], device="cuda").repeat(len(coords), 1)
        glb = postprocess.to_glb(vertices=vertices, faces=faces, attr_volume=attrs, coords=coords,
            attr_layout={"base_color": slice(0, 3), "metallic": slice(3, 4), "roughness": slice(4, 5), "alpha": slice(5, 6)},
            aabb=[[-0.5] * 3, [0.5] * 3], grid_size=n, decimation_target=1000, texture_size=128, remesh=False)
        path = root / "runtime_smoke_cube.glb"
        glb.export(path)
        scene = trimesh.load(path, force="scene")
        for geometry in scene.geometry.values():
            assert np.isfinite(geometry.vertices).all()
            assert geometry.visual.uv is not None and geometry.visual.material.baseColorTexture is not None
        return {"glb": str(path), "bytes": path.stat().st_size}

    def pipeline_import():
        from trellis2.pipelines import Trellis2ImageTo3DPipeline
        assert callable(Trellis2ImageTo3DPipeline.from_pretrained)
        assert not any(name == "comfy" or name.startswith("comfy.") for name in sys.modules)
        return "official pipeline imports without ComfyUI"

    check("cuda_forward_backward", cuda)
    check("dense_sparse_attention", attention)
    check("sparse_convolution", convolution)
    check("rasterization_textured_glb", raster_and_mesh)
    check("standalone_pipeline_import", pipeline_import)
    return 0 if all(v["status"] == "passed" for v in result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
