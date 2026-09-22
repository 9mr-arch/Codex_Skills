#!/usr/bin/env python3
"""Extract metadata, representative frames, and a contact sheet from a reference video."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--max-frames", type=int, default=18)
    parser.add_argument("--scene-threshold", type=float, default=0.42)
    return parser.parse_args()


def probe_audio(video: Path) -> dict:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"verified": False, "reason": "ffprobe unavailable"}
    command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "a",
        "-show_entries",
        "stream=codec_name,channels,sample_rate",
        "-of",
        "json",
        str(video),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        streams = json.loads(result.stdout or "{}").get("streams", [])
        return {"verified": True, "present": bool(streams), "streams": streams}
    except Exception as exc:  # pragma: no cover - depends on local binaries/codecs
        return {"verified": False, "reason": str(exc)}


def read_frame(cap: cv2.VideoCapture, index: int) -> np.ndarray | None:
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    return frame if ok else None


def signature(frame: np.ndarray) -> np.ndarray:
    thumb = cv2.resize(frame, (96, 54), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(thumb, cv2.COLOR_BGR2LAB).astype(np.float32)


def scene_candidates(
    cap: cv2.VideoCapture, frame_count: int, fps: float, threshold: float
) -> list[tuple[int, float]]:
    step = max(1, int(round(fps / 2)))
    previous = None
    candidates: list[tuple[int, float]] = []
    for index in range(0, frame_count, step):
        frame = read_frame(cap, index)
        if frame is None:
            continue
        current = signature(frame)
        if previous is not None:
            score = float(np.mean(np.abs(current - previous)) / 255.0)
            if score >= threshold:
                candidates.append((index, score))
        previous = current
    return candidates


def choose_indices(
    frame_count: int,
    samples: int,
    cuts: list[tuple[int, float]],
    max_frames: int,
) -> list[int]:
    uniform = np.linspace(
        0, max(0, frame_count - 1), max(2, samples), dtype=int
    ).tolist()
    cut_context: list[int] = []
    for index, _ in cuts:
        cut_context.extend(
            [max(0, index - 1), index, min(frame_count - 1, index + 1)]
        )
    merged = sorted(set(uniform + cut_context + [0, max(0, frame_count - 1)]))
    if len(merged) <= max_frames:
        return merged

    protected = {0, max(0, frame_count - 1)} | {index for index, _ in cuts}
    selected = [index for index in merged if index in protected]
    remaining = [index for index in merged if index not in protected]
    slots = max(0, max_frames - len(selected))
    if slots and remaining:
        picks = np.linspace(
            0, len(remaining) - 1, min(slots, len(remaining)), dtype=int
        )
        selected.extend(remaining[index] for index in picks)
    return sorted(set(selected))[:max_frames]


def make_contact_sheet(items: list[tuple[np.ndarray, str]], output: Path) -> None:
    tile_width, tile_height, label_height = 480, 270, 32
    columns = 3 if len(items) > 4 else 2
    rows = math.ceil(len(items) / columns)
    sheet = np.full(
        (rows * (tile_height + label_height), columns * tile_width, 3),
        245,
        dtype=np.uint8,
    )
    for position, (frame, label) in enumerate(items):
        row, column = divmod(position, columns)
        height, width = frame.shape[:2]
        scale = min(tile_width / width, tile_height / height)
        resized = cv2.resize(
            frame,
            (max(1, int(width * scale)), max(1, int(height * scale))),
            interpolation=cv2.INTER_AREA,
        )
        y0 = row * (tile_height + label_height) + (tile_height - resized.shape[0]) // 2
        x0 = column * tile_width + (tile_width - resized.shape[1]) // 2
        sheet[y0 : y0 + resized.shape[0], x0 : x0 + resized.shape[1]] = resized
        text_y = row * (tile_height + label_height) + tile_height + 22
        cv2.putText(
            sheet,
            label,
            (column * tile_width + 10, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (25, 25, 25),
            1,
            cv2.LINE_AA,
        )
    write_jpeg(output, sheet, quality=93)


def write_jpeg(path: Path, image: np.ndarray, quality: int = 93) -> None:
    """Write a JPEG through bytes so Unicode Windows paths work reliably."""
    ok, encoded = cv2.imencode(
        ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    )
    if not ok:
        raise RuntimeError(f"Unable to encode image: {path}")
    encoded.tofile(path)


def main() -> int:
    args = parse_args()
    video = args.video.expanduser().resolve()
    if not video.is_file():
        raise SystemExit(f"Video not found: {video}")
    if args.samples < 2 or args.max_frames < 2:
        raise SystemExit("--samples and --max-frames must be at least 2")

    output = (
        args.output_dir or video.with_name(f"{video.stem}_analysis")
    ).expanduser().resolve()
    frames_dir = output / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"Unable to open video: {video}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
        raise SystemExit("Video metadata is incomplete or unsupported")

    duration = frame_count / fps
    cuts = scene_candidates(cap, frame_count, fps, args.scene_threshold)
    indices = choose_indices(frame_count, args.samples, cuts, args.max_frames)

    extracted = []
    contact_items = []
    cut_indices = {index for index, _ in cuts}
    for number, index in enumerate(indices, start=1):
        frame = read_frame(cap, index)
        if frame is None:
            continue
        timestamp = index / fps
        filename = f"frame_{number:02d}_{timestamp:07.3f}s.jpg"
        path = frames_dir / filename
        write_jpeg(path, frame, quality=93)
        label = f"#{number:02d}  {timestamp:.3f}s"
        if index in cut_indices:
            label += "  CUT?"
        contact_items.append((frame, label))
        extracted.append(
            {
                "number": number,
                "frame_index": index,
                "timestamp_seconds": round(timestamp, 4),
                "file": str(path),
            }
        )

    cap.release()
    contact_sheet = output / "contact-sheet.jpg"
    make_contact_sheet(contact_items, contact_sheet)

    report = {
        "source": str(video),
        "duration_seconds": round(duration, 4),
        "fps": round(fps, 4),
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 4),
        "audio": probe_audio(video),
        "scene_change_candidates": [
            {
                "frame_index": index,
                "timestamp_seconds": round(index / fps, 4),
                "score": round(score, 4),
            }
            for index, score in cuts
        ],
        "frames": extracted,
        "contact_sheet": str(contact_sheet),
        "note": "Scene changes are heuristic candidates and require visual confirmation.",
    }
    report_path = output / "analysis.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "analysis": str(report_path),
                "contact_sheet": str(contact_sheet),
                "extracted_frames": len(extracted),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
