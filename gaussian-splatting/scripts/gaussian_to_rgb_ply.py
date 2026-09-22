"""Create a basic Blender RGB point-cloud PLY from a 3DGS PLY."""
from __future__ import annotations

import argparse
import numpy as np
from plyfile import PlyData, PlyElement


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    source = PlyData.read(args.input)
    vertex = source["vertex"].data
    names = set(vertex.dtype.names or ())
    needed = {"x", "y", "z", "f_dc_0", "f_dc_1", "f_dc_2"}
    missing = sorted(needed - names)
    if missing:
        raise ValueError(f"Not a supported 3DGS PLY; missing {missing}")
    dc = np.column_stack([vertex[f"f_dc_{i}"] for i in range(3)]).astype(np.float32)
    rgb = np.clip(0.5 + 0.28209479177387814 * dc, 0.0, 1.0)
    out = np.empty(len(vertex), dtype=[("x", "f4"), ("y", "f4"), ("z", "f4"),
                                        ("red", "u1"), ("green", "u1"), ("blue", "u1")])
    for name in ("x", "y", "z"):
        out[name] = vertex[name]
    for index, name in enumerate(("red", "green", "blue")):
        out[name] = np.rint(rgb[:, index] * 255).astype(np.uint8)
    if not np.isfinite(np.column_stack([out["x"], out["y"], out["z"]])).all():
        raise ValueError("PLY contains NaN or Inf coordinates")
    PlyData([PlyElement.describe(out, "vertex")], text=False).write(args.output)


if __name__ == "__main__":
    main()
