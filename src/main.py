import time

import cv2
import pyautogui

from hand_tracker import HandTracker


def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    tracker = HandTracker()

    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()

    start_time = time.time()

    print("Virtual Mouse - Cursor Control")
    print(f"Screen: {screen_width} x {screen_height}")
    print("Move your index finger to control the cursor.")
    print("Press Q to quit.")

    while True:

        success, frame = cap.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Mirror webcam
        frame = cv2.flip(frame, 1)

        timestamp_ms = int(
            (time.time() - start_time) * 1000
        )

        frame, results = tracker.find_hands(
            frame,
            timestamp_ms
        )

        landmarks = tracker.get_landmarks(
            frame,
            results
        )

        if landmarks:

            # Index fingertip = landmark 8
            _, x, y = landmarks[8]

            # Get camera dimensions
            camera_height, camera_width, _ = frame.shape

            # Map camera coordinates -> screen coordinates
            screen_x = int(
                x / camera_width * screen_width
            )

            screen_y = int(
                y / camera_height * screen_height
            )

            # Move cursor
            pyautogui.moveTo(
                screen_x,
                screen_y
            )

            # Display coordinates
            cv2.putText(
                frame,
                f"Camera: ({x}, {y})",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Screen: ({screen_x}, {screen_y})",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        else:

            cv2.putText(
                frame,
                "No hand detected",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        cv2.imshow(
            "Virtual Mouse",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()