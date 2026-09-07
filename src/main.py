import time

import cv2

from hand_tracker import HandTracker


def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    tracker = HandTracker()

    start_time = time.time()

    print("Virtual Mouse - Hand Tracking")
    print("Press Q to quit.")

    while True:

        success, frame = cap.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Mirror the webcam
        frame = cv2.flip(frame, 1)

        # MediaPipe requires increasing timestamps
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

        # Display index fingertip
        if landmarks:

            index_finger = landmarks[8]

            _, x, y = index_finger

            cv2.putText(
                frame,
                f"Index: ({x}, {y})",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        cv2.imshow(
            "Virtual Mouse - Hand Tracking",
            frame
        )

        # Q = quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()