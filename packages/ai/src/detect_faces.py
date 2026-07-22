#!/usr/bin/env python3
"""Detect faces in a video and output keyframe positions as JSON.

Uses OpenCV's YuNet DNN face detector for accurate face tracking.

Usage: python3 detect_faces.py <input_video> <output_json> [sample_fps]

Output format:
{
  "width": 1920,
  "height": 1080,
  "duration": 60.0,
  "keyframes": [
    {"t": 0.0, "x": 800, "y": 200, "w": 300, "h": 300},
    ...
  ]
}
"""

import json
import os
import sys
import cv2


MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "face_detection_yunet_2023mar.onnx"
)


def detect_faces(video_path, output_path, sample_fps=2):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: cannot open {video_path}", file=sys.stderr)
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    sample_interval = max(1, int(fps / sample_fps))

    detector = cv2.FaceDetectorYN_create(MODEL_PATH, "", (width, height))

    keyframes = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_interval == 0:
            t = frame_idx / fps
            _, faces = detector.detect(frame)

            if faces is not None and len(faces) > 0:
                # Pick largest face
                areas = [f[2] * f[3] for f in faces]
                best = int(max(range(len(areas)), key=lambda i: areas[i]))
                f = faces[best]
                x, y, w, h = int(f[0]), int(f[1]), int(f[2]), int(f[3])
                keyframes.append(
                    {
                        "t": round(t, 3),
                        "x": max(0, x),
                        "y": max(0, y),
                        "w": min(w, width - x),
                        "h": min(h, height - y),
                    }
                )
            else:
                # No face: center of frame
                keyframes.append(
                    {
                        "t": round(t, 3),
                        "x": width // 4,
                        "y": height // 4,
                        "w": width // 2,
                        "h": height // 2,
                    }
                )

        frame_idx += 1

    cap.release()

    result = {
        "width": width,
        "height": height,
        "duration": round(duration, 3),
        "keyframes": keyframes,
    }

    with open(output_path, "w") as f:
        json.dump(result, f)

    print(json.dumps({"ok": True, "keyframes": len(keyframes)}))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: detect_faces.py <input> <output.json> [sample_fps]", file=sys.stderr
        )
        sys.exit(1)

    sample = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    detect_faces(sys.argv[1], sys.argv[2], sample)
