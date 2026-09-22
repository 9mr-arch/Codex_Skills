"""Validate the actual CUDA rasterization and PLY paths used by video 3DGS."""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import traceback
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.runtime_root.resolve()
    results: dict[str, object] = {"python": sys.version, "checks": {}}

    def check(name, fn):
        try:
            results["checks"][name] = {"status": "passed", "detail": fn()}
        except Exception:
            results["checks"][name] = {"status": "failed", "error": traceback.format_exc()}
        (root / "runtime_validation.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    def cuda_and_raster():
        import torch
        from gsplat import rasterization

        assert torch.cuda.is_available()
        means = torch.tensor([[0.0, 0.0, 2.0]], device="cuda", requires_grad=True)
        quats = torch.tensor([[1.0, 0.0, 0.0, 0.0]], device="cuda", requires_grad=True)
        scales = torch.full((1, 3), 0.1, device="cuda", requires_grad=True)
        opacities = torch.full((1,), 0.8, device="cuda", requires_grad=True)
        colors = torch.tensor([[1.0, 0.2, 0.1]], device="cuda", requires_grad=True)
        view = torch.eye(4, device="cuda")[None]
        intrinsics = torch.tensor([[[100.0, 0.0, 32.0], [0.0, 100.0, 32.0], [0.0, 0.0, 1.0]]], device="cuda")
        image, alpha, _ = rasterization(means, quats, scales, opacities, colors, view, intrinsics, 64, 64)
        loss = image.sum() + alpha.sum()
        loss.backward()
        assert torch.isfinite(image).all() and means.grad is not None
        return {"gpu": torch.cuda.get_device_name(), "image_sum": float(image.sum())}

    def ply_roundtrip():
        import numpy as np
        from plyfile import PlyData, PlyElement

        dtype = [("x", "f4"), ("y", "f4"), ("z", "f4"), ("f_dc_0", "f4"),
                 ("f_dc_1", "f4"), ("f_dc_2", "f4"), ("opacity", "f4"),
                 ("scale_0", "f4"), ("scale_1", "f4"), ("scale_2", "f4"),
                 ("rot_0", "f4"), ("rot_1", "f4"), ("rot_2", "f4"), ("rot_3", "f4")]
        row = np.zeros(1, dtype=dtype)
        row["z"] = 2.0
        row["rot_0"] = 1.0
        path = root / "runtime_smoke_gaussian.ply"
        PlyData([PlyElement.describe(row, "vertex")], text=False).write(path)
        reopened = PlyData.read(path)["vertex"].data
        assert len(reopened) == 1 and math.isfinite(float(reopened["z"][0]))
        return {"path": str(path), "bytes": path.stat().st_size}

    def external_tools():
        colmap = os.environ.get("COLMAP_BAT")
        if not colmap or not Path(colmap).is_file():
            raise FileNotFoundError("COLMAP_BAT is missing")
        colmap_help = subprocess.run([colmap, "-h"], capture_output=True, text=True, timeout=30)
        if colmap_help.returncode != 0:
            raise RuntimeError(colmap_help.stderr or colmap_help.stdout)
        ffmpeg = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=30)
        if ffmpeg.returncode != 0:
            raise RuntimeError(ffmpeg.stderr)
        return {"colmap": colmap, "ffmpeg": ffmpeg.stdout.splitlines()[0]}

    check("cuda_forward_backward_rasterization", cuda_and_raster)
    check("gaussian_ply_roundtrip", ply_roundtrip)
    check("colmap_ffmpeg", external_tools)
    return 0 if all(v["status"] == "passed" for v in results["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
