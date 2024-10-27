from ultralytics import YOLO
import cv2

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Nano model for faster inference

# Initialize webcam feed
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    # Perform detection
    results = model(frame)

    # Process results
    person_detected = False
    for result in results[0].boxes:  # Accessing the boxes directly
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        conf = result.conf[0].item()
        cls = int(result.cls[0].item())

        if cls == 0:  # Class ID 0 is for 'person'
            person_detected = True
            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'person {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Print coordinates for PTZ camera control
            print(f"Detected person at: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

    # Display the resulting frame
    cv2.imshow('Person Tracking', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()