# 🖱️ VisionMouse

**Real-Time Gesture-Based Virtual Mouse using Computer Vision**

VisionMouse is a real-time human-computer interaction system that uses a webcam, **OpenCV**, **MediaPipe Hand Landmarker**, and **PyAutoGUI** to translate hand gestures into mouse actions.

The project tracks 21 hand landmarks in real time and uses fingertip positions, finger states, normalized distances, smoothing, and gesture state management to control the system cursor.

---

## ✨ Features

### Computer Vision

* Real-time webcam capture using OpenCV
* 21-point hand landmark detection
* Index, thumb, and middle finger tracking
* Finger extension detection
* Palm-size normalization for scale-independent gestures

### Cursor Control

* Index-finger-based cursor movement
* Camera-to-screen coordinate mapping
* Active camera region
* Cursor smoothing
* Dead-zone filtering to reduce jitter and drift

### Mouse Gestures

| Gesture                          | Action      |
| -------------------------------- | ----------- |
| ☝️ Index finger only             | Move cursor |
| 🤏 Quick thumb + index pinch     | Left click  |
| 🤏 Hold + move thumb/index pinch | Drag & drop |
| 🤏 Thumb + middle pinch          | Right click |

### Safety

* Mouse button release if the hand disappears
* Mouse button release during application shutdown
* Gesture state tracking to prevent repeated clicks
* Delayed drag activation to distinguish clicking from dragging

---

## 🧠 How It Works

VisionMouse follows this pipeline:

```text
                  Webcam
                     │
                     ▼
              OpenCV Capture
                     │
                     ▼
          MediaPipe Hand Landmarker
                     │
                     ▼
             21 Hand Landmarks
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
       Finger      Pinch      Finger
        State     Distance     Position
          │          │          │
          └──────────┼──────────┘
                     ▼
             Gesture Recognition
                     │
                     ▼
              Gesture State Machine
                     │
                     ▼
                 PyAutoGUI
                     │
                     ▼
                OS Mouse
```

---

# 🏗️ Project Architecture

```text
VisionMouse/
│
├── src/
│   ├── main.py
│   └── hand_tracker.py
│
├── models/
│   └── hand_landmarker.task
│
├── screenshots/
│
├── requirements.txt
│
└── README.md
```

### `src/main.py`

Contains the main application loop:

* Webcam capture
* Hand tracking
* Coordinate mapping
* Cursor movement
* Gesture recognition
* Click handling
* Drag handling
* Safety mechanisms
* OpenCV interface

### `src/hand_tracker.py`

Responsible for:

* Loading the MediaPipe Hand Landmarker
* Converting OpenCV frames to MediaPipe images
* Running hand detection
* Extracting 21 hand landmarks

### `models/hand_landmarker.task`

MediaPipe's hand landmark model used for real-time hand tracking.

---

# ⚙️ Technology Stack

| Technology  | Purpose                          |
| ----------- | -------------------------------- |
| Python 3.12 | Core programming language        |
| OpenCV      | Webcam capture and visualization |
| MediaPipe   | Hand landmark detection          |
| PyAutoGUI   | OS-level mouse control           |
| NumPy       | Numerical processing             |

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd VisionMouse
```

---

## 2. Create a virtual environment

Python **3.12** is recommended for this project.

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you haven't created `requirements.txt` yet:

```text
numpy==2.2.6
opencv-python==4.11.0.86
mediapipe==0.10.35
pyautogui==0.9.54
```

Install manually if required:

```bash
pip install numpy==2.2.6
pip install opencv-python==4.11.0.86
pip install mediapipe==0.10.35
pip install pyautogui==0.9.54
```

---

# 📦 MediaPipe Model

Download the **Hand Landmarker** model and place it in:

```text
models/hand_landmarker.task
```

The application expects the following structure:

```text
models/
└── hand_landmarker.task
```

Without this file, the hand tracker cannot initialize.

---

# ▶️ Running the Application

From the project root:

```bash
python src/main.py
```

The webcam window should appear.

Press:

```text
Q
```

to exit.

---

# 🖐️ Gesture Controls

## Move Cursor

Raise only your index finger:

```text
       ☝️
```

The index fingertip controls the cursor position.

The camera coordinates are transformed into screen coordinates:

```text
Camera Space
     │
     ▼
Active Region
     │
     ▼
Normalized Coordinates
     │
     ▼
Screen Coordinates
```

---

## Left Click

Perform a quick:

```text
Thumb + Index
     🤏
```

The system waits for the pinch to be released before registering the click.

This prevents continuous clicking while the fingers remain together.

---

## Drag & Drop

Perform:

```text
Thumb + Index
      ↓
    Pinch
      ↓
 Hold
      ↓
 Move
```

The system enters drag mode only after both:

* A minimum hold duration
* A minimum movement distance

have been reached.

When the pinch is released:

```text
mouseUp()
```

is triggered.

---

## Right Click

Use:

```text
Thumb + Middle Finger
        ↓
      Pinch
```

This triggers a right-click.

---

# 🎯 Cursor Stabilization

Raw hand landmarks contain small frame-to-frame variations.

Without filtering:

```text
Detected position:

100 → 104 → 98 → 103 → 97 → 105
```

would cause visible cursor jitter.

VisionMouse applies:

### 1. Active Region

The outer portion of the webcam frame is ignored.

```text
┌───────────────────────────────┐
│                               │
│    ┌─────────────────────┐    │
│    │                     │    │
│    │    ACTIVE REGION    │    │
│    │                     │    │
│    └─────────────────────┘    │
│                               │
└───────────────────────────────┘
```

### 2. Dead Zone

Very small movements are ignored.

```python
deadzone = 4
```

### 3. Temporal Smoothing

Cursor movement is interpolated toward the target:

```python
current_x = previous_x + (
    target_x - previous_x
) / smoothening
```

This reduces sudden cursor jumps.

---

# 🧩 Gesture State Machine

Instead of triggering actions directly from a single frame, VisionMouse maintains gesture states.

For example, left-click/drag:

```text
          ┌─────────────┐
          │    IDLE     │
          └──────┬──────┘
                 │
              Pinch
                 │
                 ▼
          ┌─────────────┐
          │   PINCHING  │
          └──────┬──────┘
                 │
          ┌──────┴───────┐
          │              │
       Release        Hold + Move
          │              │
          ▼              ▼
     LEFT CLICK       DRAGGING
                         │
                      Release
                         │
                         ▼
                       DROP
```

This is more reliable than simply checking:

```python
if distance < threshold:
    click()
```

because a gesture has a **beginning, duration, movement, and release**.

---

# 🛡️ Safety Mechanisms

Controlling the real operating-system mouse introduces several edge cases.

VisionMouse therefore includes safeguards.

### Hand disappears during drag

If the camera loses the hand while dragging:

```python
pyautogui.mouseUp()
```

is automatically called.

### Application exits during drag

Before shutting down:

```python
if dragging:
    pyautogui.mouseUp()
```

is executed.

This prevents the OS mouse button from accidentally remaining pressed.

---

# 📊 Current Status

| Component                | Status |
| ------------------------ | ------ |
| Webcam capture           | ✅      |
| MediaPipe hand detection | ✅      |
| 21 hand landmarks        | ✅      |
| Index finger tracking    | ✅      |
| Cursor control           | ✅      |
| Coordinate mapping       | ✅      |
| Cursor smoothing         | ✅      |
| Drift reduction          | ✅      |
| Left click               | ✅      |
| Right click              | ✅      |
| Drag & drop              | ✅      |
| Safety release           | ✅      |
| Scroll                   | 🚧     |
| Gesture HUD              | 🚧     |
| FPS monitoring           | 🚧     |
| Configuration system     | 🚧     |

---

# 🔬 Computer Vision Concepts Demonstrated

This project demonstrates several practical computer vision concepts:

### Hand Landmark Detection

MediaPipe provides 21 normalized hand landmarks:

```text
0  - Wrist
4  - Thumb tip
8  - Index fingertip
12 - Middle fingertip
16 - Ring fingertip
20 - Pinky fingertip
```

### Coordinate Transformation

Converts:

```text
Webcam coordinates
        ↓
Active region
        ↓
Screen coordinates
```

### Geometric Gesture Recognition

Gestures are identified using Euclidean distance:

```text
d = √((x₂-x₁)² + (y₂-y₁)²)
```

For example:

```text
Thumb ↔ Index
```

determines whether a pinch gesture is occurring.

### Scale Normalization

Instead of using a fixed pixel threshold, pinch distance is normalized using palm size:

```text
normalized_distance =
        fingertip_distance
        ───────────────────
            palm_size
```

This makes the gesture less dependent on how close the user's hand is to the camera.

### Temporal Filtering

Cursor smoothing reduces the effect of noisy landmark predictions over consecutive frames.

### Finite-State Gesture Recognition

Gestures are represented as states such as:

```text
IDLE
PINCHING
DRAGGING
```

rather than treating each webcam frame independently.

---

# 🚧 Future Improvements

Planned improvements include:

* [ ] Two-finger scrolling
* [ ] Gesture-based activation/deactivation
* [ ] FPS monitoring
* [ ] Better click/drag classification
* [ ] Configurable gesture thresholds
* [ ] Adaptive smoothing
* [ ] Multi-hand support
* [ ] Gesture calibration
* [ ] On-screen gesture HUD
* [ ] Performance optimization
* [ ] Automated gesture evaluation
* [ ] Cross-platform testing

---
