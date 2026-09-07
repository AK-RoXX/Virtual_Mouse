import math
import time
import cv2
import pyautogui

from hand_tracker import HandTracker

def main():
    # Webcam
    
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    tracker = HandTracker()    

    # Screen
    screen_width, screen_height = pyautogui.size()
    
    # Cursor configuration
    smoothening = 8
    frame_margin = 100
    deadzone = 3

    previous_x = 0
    previous_y = 0

    
    # Gesture configuration
    click_threshold = 35

    left_pinching = False
    right_pinching = False
    dragging = False

    
    # Timing
    start_time = time.time()

    print("================================")
    print("       VisionMouse")
    print("================================")
    print(f"Screen: {screen_width} x {screen_height}")
    print()
    print("Controls:")
    print("  Index finger       -> Move cursor")
    print("  Thumb + Index      -> Left click / Drag")
    print("  Thumb + Middle     -> Right click")
    print("  Q                  -> Quit")
    print("================================")

    while True:

        # Read frame
        success, frame = cap.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Mirror webcam
        frame = cv2.flip(frame, 1)

        # MediaPipe timestamp
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

        camera_height, camera_width, _ = frame.shape

        # Active region
        cv2.rectangle(
            frame,
            (frame_margin, frame_margin),
            (
                camera_width - frame_margin,
                camera_height - frame_margin
            ),
            (255, 0, 255),
            2
        )

        # Hand detected

        if landmarks:

            # INDEX FINGER -> CURSOR MOVEMENT

            _, x, y = landmarks[8]

            # Keep fingertip inside active area
            x = max(
                frame_margin,
                min(camera_width - frame_margin, x)
            )

            y = max(
                frame_margin,
                min(camera_height - frame_margin, y)
            )

            # Camera coordinates -> screen coordinates
            target_x = int(
                (x - frame_margin)
                / (camera_width - 2 * frame_margin)
                * screen_width
            )

            target_y = int(
                (y - frame_margin)
                / (camera_height - 2 * frame_margin)
                * screen_height
            )

            # DEAD-ZONE + SMOOTHING

            if (
                abs(target_x - previous_x) > deadzone
                or
                abs(target_y - previous_y) > deadzone
            ):

                current_x = previous_x + (
                    target_x - previous_x
                ) / smoothening

                current_y = previous_y + (
                    target_y - previous_y
                ) / smoothening

                current_x = int(current_x)
                current_y = int(current_y)

                pyautogui.moveTo(
                    current_x,
                    current_y
                )

                previous_x = current_x
                previous_y = current_y

            # Fingertip indicator

            cv2.circle(
                frame,
                (x, y),
                10,
                (255, 0, 255),
                -1
            )

            # Gesture landmarks

            _, thumb_x, thumb_y = landmarks[4]
            _, index_x, index_y = landmarks[8]
            _, middle_x, middle_y = landmarks[12]

            # Calculate pinch distances

            left_distance = math.hypot(
                index_x - thumb_x,
                index_y - thumb_y
            )

            right_distance = math.hypot(
                middle_x - thumb_x,
                middle_y - thumb_y
            )

            # Draw gesture lines

            # Thumb -> Index
            cv2.line(
                frame,
                (thumb_x, thumb_y),
                (index_x, index_y),
                (255, 255, 0),
                2
            )

            # Thumb -> Middle
            cv2.line(
                frame,
                (thumb_x, thumb_y),
                (middle_x, middle_y),
                (255, 0, 255),
                2
            )

            # LEFT CLICK / DRAG
            # Thumb + Index

            if left_distance < click_threshold:

                if not left_pinching:

                    # Start holding left mouse button
                    pyautogui.mouseDown()

                    left_pinching = True
                    dragging = True

                # Display drag state
                cv2.putText(
                    frame,
                    "DRAGGING",
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

            else:

                # Release mouse button when pinch ends
                if left_pinching:

                    pyautogui.mouseUp()

                    left_pinching = False
                    dragging = False

            # RIGHT CLICK
            # Thumb + Middle

            if right_distance < click_threshold:

                if not right_pinching:

                    pyautogui.rightClick()

                    right_pinching = True

                cv2.putText(
                    frame,
                    "RIGHT CLICK",
                    (10, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

            else:

                right_pinching = False

            # Tracking status

            cv2.putText(
                frame,
                "Tracking",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
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

            # Release mouse if hand disappears during drag

            if dragging:

                pyautogui.mouseUp()

                dragging = False
                left_pinching = False

        # Display
        
        cv2.imshow(
            "VisionMouse",
            frame
        )

        # Quit

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Safety: make sure mouse isn't left held when program exits
    if dragging:
        pyautogui.mouseUp()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
