import math
import time

import cv2
import pyautogui

from hand_tracker import HandTracker



# Utility functions


def distance(p1, p2):
    """Euclidean distance between two (x, y) points."""
    return math.hypot(
        p1[0] - p2[0],
        p1[1] - p2[1]
    )


def is_finger_extended(landmarks, tip_id, pip_id):
    """
    Basic finger extension test.

    A fingertip being farther from the wrist than
    its PIP joint indicates that the finger is extended.
    """

    wrist = (landmarks[0][1], landmarks[0][2])

    tip = (landmarks[tip_id][1], landmarks[tip_id][2])
    pip = (landmarks[pip_id][1], landmarks[pip_id][2])

    tip_distance = distance(wrist, tip)
    pip_distance = distance(wrist, pip)

    return tip_distance > pip_distance * 1.15


def get_palm_size(landmarks):
    """
    Estimate palm size using wrist -> middle MCP.

    This allows gesture thresholds to scale with hand distance
    from the camera.
    """

    wrist = (landmarks[0][1], landmarks[0][2])
    middle_mcp = (landmarks[9][1], landmarks[9][2])

    return max(
        distance(wrist, middle_mcp),
        1
    )



# Main


def main():

    
    # Webcam
    

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    
    # Tracker
    

    tracker = HandTracker()

    
    # Screen
    

    screen_width, screen_height = pyautogui.size()

    
    # Cursor configuration
    

    smoothening = 7

    frame_margin = 100

    deadzone = 4

    previous_x = screen_width // 2
    previous_y = screen_height // 2

    cursor_initialized = False

    
    # Gesture configuration
    

    # Pinch starts below this normalized distance
    pinch_start_ratio = 0.32

    # Pinch must open beyond this value
    # before another gesture can happen.
    pinch_release_ratio = 0.45

    # Minimum movement before a pinch becomes drag
    drag_distance = 20

    # Time before a pinch is considered a drag
    drag_hold_time = 0.35

    
    # Gesture state
    

    left_pinching = False
    right_pinching = False

    left_pinch_start_time = 0

    pinch_start_x = 0
    pinch_start_y = 0

    dragging = False

    
    # Timing
    

    start_time = time.time()

    
    # PyAutoGUI safety
    

    pyautogui.PAUSE = 0.01

    print("========================================")
    print("             VisionMouse")
    print("========================================")
    print(f"Screen: {screen_width} x {screen_height}")
    print()
    print("Gestures:")
    print("  Index only              -> Move")
    print("  Quick thumb + index     -> Left click")
    print("  Hold + move pinch       -> Drag")
    print("  Thumb + middle          -> Right click")
    print()
    print("Press Q to quit.")
    print("========================================")

    
    # Main loop
    

    while True:

        success, frame = cap.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Mirror webcam
        frame = cv2.flip(frame, 1)

        
        # Timestamp
        

        timestamp_ms = int(
            (time.time() - start_time) * 1000
        )

        
        # Hand tracking
        

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

        
        # HAND DETECTED
        

        if landmarks:

            
            # Get important landmarks
            

            wrist = (
                landmarks[0][1],
                landmarks[0][2]
            )

            thumb = (
                landmarks[4][1],
                landmarks[4][2]
            )

            index = (
                landmarks[8][1],
                landmarks[8][2]
            )

            middle = (
                landmarks[12][1],
                landmarks[12][2]
            )

            
            # Finger states
            

            index_extended = is_finger_extended(
                landmarks,
                8,
                6
            )

            middle_extended = is_finger_extended(
                landmarks,
                12,
                10
            )

            ring_extended = is_finger_extended(
                landmarks,
                16,
                14
            )

            pinky_extended = is_finger_extended(
                landmarks,
                20,
                18
            )

            
            # Palm size
            

            palm_size = get_palm_size(
                landmarks
            )

            
            # Pinch distances
            

            thumb_index_distance = distance(
                thumb,
                index
            )

            thumb_middle_distance = distance(
                thumb,
                middle
            )

            # Normalize distances
            index_pinch_ratio = (
                thumb_index_distance / palm_size
            )

            middle_pinch_ratio = (
                thumb_middle_distance / palm_size
            )

            
            # GESTURE 1
            # INDEX ONLY -> CURSOR
            

            index_only = (
                index_extended
                and not middle_extended
                and not ring_extended
                and not pinky_extended
            )

            
            # Cursor movement
            

            if index_only:

                x = index[0]
                y = index[1]

                # Clamp inside active region
                x = max(
                    frame_margin,
                    min(
                        camera_width - frame_margin,
                        x
                    )
                )

                y = max(
                    frame_margin,
                    min(
                        camera_height - frame_margin,
                        y
                    )
                )

                # Camera -> screen
                target_x = int(
                    (x - frame_margin)
                    /
                    (camera_width - 2 * frame_margin)
                    *
                    screen_width
                )

                target_y = int(
                    (y - frame_margin)
                    /
                    (camera_height - 2 * frame_margin)
                    *
                    screen_height
                )

                # Initialize cursor on first detection
                if not cursor_initialized:

                    previous_x = target_x
                    previous_y = target_y

                    cursor_initialized = True

                    pyautogui.moveTo(
                        previous_x,
                        previous_y
                    )

                
                # Dead-zone
                

                if (
                    abs(target_x - previous_x) > deadzone
                    or
                    abs(target_y - previous_y) > deadzone
                ):

                    current_x = (
                        previous_x
                        +
                        (target_x - previous_x)
                        / smoothening
                    )

                    current_y = (
                        previous_y
                        +
                        (target_y - previous_y)
                        / smoothening
                    )

                    current_x = int(current_x)
                    current_y = int(current_y)

                    pyautogui.moveTo(
                        current_x,
                        current_y
                    )

                    previous_x = current_x
                    previous_y = current_y

                
                # Display
                

                cv2.putText(
                    frame,
                    "MOVE",
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

            
            # GESTURE 2
            # THUMB + INDEX
            

            left_pinch = (
                index_extended
                and
                index_pinch_ratio < pinch_start_ratio
            )

            
            # Start pinch
            

            if left_pinch and not left_pinching:

                left_pinching = True

                left_pinch_start_time = time.time()

                pinch_start_x = index[0]
                pinch_start_y = index[1]

                dragging = False

            
            # Pinch is being held
            

            if left_pinching:

                elapsed = (
                    time.time()
                    -
                    left_pinch_start_time
                )

                movement = math.hypot(
                    index[0] - pinch_start_x,
                    index[1] - pinch_start_y
                )

                # Start dragging only after
                # holding AND moving
                if (
                    elapsed >= drag_hold_time
                    and movement >= drag_distance
                ):

                    if not dragging:

                        pyautogui.mouseDown()

                        dragging = True

                    cv2.putText(
                        frame,
                        "DRAGGING",
                        (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )

                else:

                    cv2.putText(
                        frame,
                        "PINCH",
                        (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )

            
            # Release pinch
            

            if (
                left_pinching
                and
                index_pinch_ratio > pinch_release_ratio
            ):

                # If dragging, release mouse
                if dragging:

                    pyautogui.mouseUp()

                    dragging = False

                # If it was a quick pinch,
                # interpret it as a click.
                else:

                    elapsed = (
                        time.time()
                        -
                        left_pinch_start_time
                    )

                    if elapsed < drag_hold_time:

                        pyautogui.click()

                left_pinching = False

            
            # GESTURE 3
            # THUMB + MIDDLE
            # RIGHT CLICK
            

            right_pinch = (
                middle_extended
                and
                not index_extended
                and
                middle_pinch_ratio < pinch_start_ratio
            )

            if right_pinch and not right_pinching:

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

            if (
                right_pinching
                and
                middle_pinch_ratio > pinch_release_ratio
            ):

                right_pinching = False

            
            # Draw pinch lines
            

            cv2.line(
                frame,
                thumb,
                index,
                (255, 255, 0),
                2
            )

            cv2.line(
                frame,
                thumb,
                middle,
                (255, 0, 255),
                2
            )

            
            # Debug information
            

            cv2.putText(
                frame,
                f"Index pinch: {index_pinch_ratio:.2f}",
                (10, camera_height - 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1
            )

            cv2.putText(
                frame,
                f"Middle pinch: {middle_pinch_ratio:.2f}",
                (10, camera_height - 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1
            )

        
        # NO HAND
        

        else:

            cv2.putText(
                frame,
                "NO HAND",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            # Safety release
            if dragging:

                pyautogui.mouseUp()

                dragging = False

            left_pinching = False
            right_pinching = False

        
        # Display window
        

        cv2.imshow(
            "VisionMouse",
            frame
        )

        
        # Quit
        

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            if dragging:
                pyautogui.mouseUp()

            break

    
    # Final safety cleanup
    

    if dragging:
        pyautogui.mouseUp()

    cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

