import cv2
import mediapipe as mp
import requests
import time

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)  # Increased sensitivity

# PTZ Camera IP and Command URL
CAMERA_IP = "192.168.116.111"
BASE_URL = f"http://{CAMERA_IP}/cgi-bin/ptzctrl.cgi?ptzcmd&"

# Define the center of the frame and movement parameters
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
CENTER_X = FRAME_WIDTH // 2
CENTER_Y = FRAME_HEIGHT // 2
PANTILT_THRESHOLD = 50  # Adjusted threshold for smoother movement
DEAD_ZONE = 50  # Dead zone around the center to reduce unnecessary movements
COMMAND_DELAY = 0.2  # Delay for quicker response
PAN_SPEED = 12  # Increased pan speed for quicker adjustment
TILT_SPEED = 12  # Increased tilt speed for quicker adjustment

# Function to send PTZ commands
def send_command(command):
    url = BASE_URL + command
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Command sent: {command}")
        else:
            print(f"Failed to send command: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

# Initialize webcam feed
cap = cv2.VideoCapture(0)

# Initialize variables for movement timing
last_command_time = time.time()
current_command = None
command = None  # Initialize command with a default value

# Initialize variables for smoothing
prev_face_center_x = CENTER_X
prev_face_center_y = CENTER_Y

# Exponential smoothing factors
ALPHA_X = 0.1
ALPHA_Y = 0.1

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    # Improve image contrast and brightness
    frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=30)  # Increase contrast and brightness

    # Convert frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform face detection
    results = face_detection.process(rgb_frame)

    # Initialize tracking variables
    face_detected = False

    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            # Draw face bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, 'Face', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Print coordinates for PTZ camera control
            print(f"Detected face at: x1={x}, y1={y}, x2={x + w}, y2={y + h}")

            face_detected = True

            # Smooth out camera movements
            smoothed_face_center_x = int(ALPHA_X * face_center_x + (1 - ALPHA_X) * prev_face_center_x)
            smoothed_face_center_y = int(ALPHA_Y * face_center_y + (1 - ALPHA_Y) * prev_face_center_y)

            delta_x = smoothed_face_center_x - CENTER_X
            delta_y = smoothed_face_center_y - CENTER_Y

            if abs(delta_x) > DEAD_ZONE or abs(delta_y) > DEAD_ZONE:
                # Determine if the face is out of the center
                if abs(delta_x) > PANTILT_THRESHOLD:
                    if delta_x < 0:
                        command = f'left&{PAN_SPEED}&10'
                    else:
                        command = f'right&{PAN_SPEED}&10'

                if abs(delta_y) > PANTILT_THRESHOLD:
                    if delta_y < 0:
                        command = f'up&10&{TILT_SPEED}'
                    else:
                        command = f'down&10&{TILT_SPEED}'

                if current_command != command:
                    current_time = time.time()
                    if current_time - last_command_time >= COMMAND_DELAY:
                        send_command(command)
                        current_command = command
                        last_command_time = current_time

                # Update previous face center
                prev_face_center_x = smoothed_face_center_x
                prev_face_center_y = smoothed_face_center_y
            else:
                # If the face is within the dead zone, stop all movement
                if current_command:
                    send_command('ptzstop')
                    current_command = None
    else:
        # If no face detected, stop all movement
        if current_command:
            send_command('ptzstop')
            current_command = None
        print("No face detected")

    # Display the resulting frame
    cv2.imshow('Face Tracking', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()