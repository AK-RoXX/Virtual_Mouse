from pathlib import Path

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker:
    def __init__(
        self,
        max_hands=1,
        detection_confidence=0.7,
        tracking_confidence=0.7,
    ):
        project_root = Path(__file__).resolve().parents[1]
        model_path = project_root / "models" / "hand_landmarker.task"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {model_path}\n"
                "Download hand_landmarker.task and place it in models/"
            )

        base_options = python.BaseOptions(model_asset_path=str(model_path))

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

    def find_hands(self, frame, timestamp_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        results = self.detector.detect_for_video(mp_image, timestamp_ms)

        return frame, results

    def get_landmarks(self, frame, results):
        landmarks = []

        if not results.hand_landmarks:
            return landmarks

        hand = results.hand_landmarks[0]

        height, width, _ = frame.shape

        for landmark_id, landmark in enumerate(hand):

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            landmarks.append((landmark_id, x, y))

            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        return landmarks
