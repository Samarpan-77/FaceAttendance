import cv2
import face_recognition
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook
import logging

# Constants
KNOWN_FACES_DIR = '##Change this with your known faces directory or location ## '
ATTENDANCE_FILE = '##Change this with your attendance.xlsx file directory or location ##'

# Set up logging
logging.basicConfig(filename='attendance.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def load_known_faces(directory):
    """
    Load known faces from the specified directory.

    """
    if not os.path.exists(directory):
        print("Known faces directory does not exist.")
        return [], []

    known_faces = []
    known_names = []

    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            try:
                image = face_recognition.load_image_file(f"{directory}/{filename}")
                encoding = face_recognition.face_encodings(image)[0]
                known_faces.append(encoding)
                known_names.append(filename.split('.')[0])
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return known_faces, known_names

def capture_image():
    """
    Capture an image from the default camera.

    """
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert the frame to RGB for face recognition
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)

        # Draw rectangles around the faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 2)

        cv2.imshow('Press Space to capture', frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    cam.release()
    cv2.destroyAllWindows()
    return frame if ret else None

def recognize_face(captured_image, known_faces, known_names):
    """
    Recognize faces in the captured image.

    """
    try:
        face_encodings = face_recognition.face_encodings(captured_image)
        if len(face_encodings) == 0:
            print("No  known faces detected in the image.")
            return []

        recognized_faces = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            if True in matches:
                first_match_index = matches.index(True)
                recognized_faces.append(known_names[first_match_index])

        return recognized_faces
    except Exception as e:
        print(f"Error recognizing face: {e}")
        return []

def mark_attendance(student_name, file=ATTENDANCE_FILE):
    try:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        current_month = now.strftime("%B")  

        try:
            df = pd.read_excel(file)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            df = pd.DataFrame(columns=["Name", "Date", "Time", "Days_Present", "Month"])
            df.to_excel(file, index=False)
        
        if student_name in df[df["Date"] == current_date]["Name"].values:
            print(f"Attendance already marked for {student_name} on {current_date}.")
        else:
            # Check if student has an existing record for the current month
            student_monthly_record = df[(df["Name"] == student_name) & (df["Month"] == current_month)]
            if not student_monthly_record.empty:
                # Get the current days present count
                days_present = student_monthly_record["Days_Present"].max() + 1
            else:
                days_present = 1
            
            # Add a new record for the current month
            new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time], "Days_Present": [days_present], "Month": [current_month]})
            df = pd.concat([df, new_record_df], ignore_index=True)
            # Write the DataFrame to the Excel file
            df.to_excel(file, index=False)
            print(f"Attendance marked for {student_name}.")
    except Exception as e:
        logging.error(f"Error marking attendance: {e}")


def main():
    known_faces, known_names = load_known_faces(KNOWN_FACES_DIR)
    image = capture_image()
    if image is None:
        return

    recognized_faces = recognize_face(image, known_faces, known_names)
    if not recognized_faces:
        print("Student not recognized!")
        return

    for student_name in recognized_faces:
        mark_attendance(student_name)

if __name__ == "__main__":
    main()
