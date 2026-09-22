"""Download only the model files used by the selected TRELLIS.2 pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path
from huggingface_hub import snapshot_download

DINO_REPO = "visualbruno/dinov3-vitl16-pretrain-lvd1689m"
DINO_REVISION = "8463e34549282813c2cbf67241b27c6fe8fa6321"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--pipeline", choices=("512", "1024_cascade"), default="1024_cascade")
    args = parser.parse_args()
    models = args.runtime_root.resolve() / "models"
    models.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        DINO_REPO,
        revision=DINO_REVISION,
        allow_patterns=["model.safetensors", "config.json", "preprocessor_config.json"],
        local_dir=models / "dinov3",
        token=False,
    )
    common = [
        "pipeline.json",
        "ckpts/shape_dec_next_dc_f16c32_fp16.*",
        "ckpts/ss_flow_img_dit_1_3B_64_bf16.*",
        "ckpts/tex_dec_next_dc_f16c32_fp16.*",
    ]
    if args.pipeline == "1024_cascade":
        common += [
            "ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16.*",
            "ckpts/slat_flow_img2shape_dit_1_3B_512_bf16.*",
            "ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.*",
        ]
    else:
        common += [
            "ckpts/slat_flow_img2shape_dit_1_3B_512_bf16.*",
            "ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16.*",
        ]
    snapshot_download("microsoft/TRELLIS.2-4B", allow_patterns=common, local_dir=models / "trellis2")
    snapshot_download(
        "microsoft/TRELLIS-image-large",
        allow_patterns=["ckpts/ss_dec_conv3d_16l8_fp16.*"],
        local_dir=models / "trellis-image-large",
    )
    # BiRefNet remains in the shared Hugging Face cache; its adapter loads it by repo id.
    snapshot_download(
        "ZhengPeng7/BiRefNet",
        allow_patterns=["config.json", "model.safetensors", "*.py"],
    )


if __name__ == "__main__":
    main()
