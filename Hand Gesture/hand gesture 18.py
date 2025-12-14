#!/usr/bin/env python3

import cv2
from cvzone.HandTrackingModule import HandDetector
import time

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not accessible.")
    exit()

# Initialize the HandDetector
detector = HandDetector(maxHands=1, detectionCon=0.8)

# Mapping of finger configurations to hand gesture emojis and their names
emoji_mapping = {
    (0, 0, 0, 0, 0): ("✊", "Raised Fist"),
    (0, 1, 0, 0, 0): ("☝️", "Index Pointing Up"),
    (0, 1, 1, 0, 0): ("✌️", "Victory Hand"),
    (1, 1, 0, 0, 1): ("🤟", "Love-You Gesture"),
    (0, 1, 1, 1, 1): ("🖖", "Vulcan Salute"),
    (1, 1, 1, 1, 1): ("✋", "Raised Hand"),
    (0, 0, 1, 1, 1): ("👌", "OK Hand"),
    (1, 1, 0, 0, 0): ("🤘", "Rock On"),
    (1, 0, 0, 0, 0): ("👍", "Thumbs Up"),
    (1, 0, 0, 0, 1): ("🤙", "Call Me"),
    (0, 1, 0, 1, 0): ("🤞", "Crossed Fingers"),
    (1, 0, 1, 0, 0): ("👆", "Pointing Up"),
    (0, 0, 0, 0, 1): ("👋", "Waving Hand"),
}

while True:
    success, img = cap.read()
    if not success:
        break

    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)  # Get the state of each finger [thumb, index, middle, ring, pinky]
        finger_config = tuple(fingers)

        # Map finger configuration to emoji and name
        emoji, name = emoji_mapping.get(finger_config, ("❓", "Unknown Gesture"))

        # Display the gesture name on the screen
        cv2.putText(img, name, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    # Display the image
    cv2.imshow("Hand Gesture Detection", img)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
