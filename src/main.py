import time
import math
import cv2
import pyautogui

from hand_tracker import HandTracker


def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    tracker = HandTracker()

    screen_width, screen_height = pyautogui.size()

    # -----------------------------
    # Cursor configuration
    # -----------------------------

    smoothening = 8

    # click state
    previous_y = 0
    pinching = False
    click_threshold = 35

    frame_margin = 100

    # Ignore tiny movements
    deadzone = 3

    previous_x = 0
    previous_y = 0

    start_time = time.time()

    print("VisionMouse")
    print("Move index finger to control cursor.")
    print("Press Q to quit.")

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        timestamp_ms = int((time.time() - start_time) * 1000)

        frame, results = tracker.find_hands(frame, timestamp_ms)

        landmarks = tracker.get_landmarks(frame, results)

        camera_height, camera_width, _ = frame.shape

        # Active region
        cv2.rectangle(
            frame,
            (frame_margin, frame_margin),
            (camera_width - frame_margin, camera_height - frame_margin),
            (255, 0, 255),
            2,
        )

        if landmarks:

            # Index fingertip
            _, x, y = landmarks[8]

            # Clamp inside active region
            x = max(frame_margin, min(camera_width - frame_margin, x))

            y = max(frame_margin, min(camera_height - frame_margin, y))

            # Camera → screen
            target_x = int(
                (x - frame_margin) / (camera_width - 2 * frame_margin) * screen_width
            )

            target_y = int(
                (y - frame_margin) / (camera_height - 2 * frame_margin) * screen_height
            )

            # --------------------------------
            # Dead-zone to prevent drift
            # --------------------------------

            if (
                abs(target_x - previous_x) > deadzone
                or abs(target_y - previous_y) > deadzone
            ):

                current_x = previous_x + (target_x - previous_x) / smoothening

                current_y = previous_y + (target_y - previous_y) / smoothening

                current_x = int(current_x)
                current_y = int(current_y)

                pyautogui.moveTo(current_x, current_y)

                previous_x = current_x
                previous_y = current_y

            # Fingertip indicator
            cv2.circle(frame, (x, y), 10, (255, 0, 255), -1)

            cv2.putText(
                frame,
                "Tracking",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            # --------------------------------
            # Left click detection
            # --------------------------------

            _, thumb_x, thumb_y = landmarks[4]
            _, index_x, index_y = landmarks[8]

            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

            if distance < click_threshold:

                if not pinching:

                    pyautogui.click()

                    pinching = True

                    cv2.putText(
                        frame,
                        "LEFT CLICK",
                        (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2,
                    )
                    cv2.line(
                        frame, (thumb_x, thumb_y), (index_x, index_y), (255, 255, 0), 2
                    )
                else:
                    pinching = False

        else:

            cv2.putText(
                frame,
                "No hand detected",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        cv2.imshow("VisionMouse", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
