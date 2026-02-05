import cv2
import os
import numpy as np
import pandas as pd
import logging
from datetime import datetime
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

# ================== CONSTANTS ==================
KNOWN_FACES_DIR = r"##Change this with your known faces directory or location ##"
ATTENDANCE_FILE = r"##Change this with your attendance.xlsx location ##"
SIMILARITY_THRESHOLD = 0.5  # adjust if needed

# ================== LOGGING ==================
logging.basicConfig(
    filename="attendance.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ================== MODELS ==================
face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=-1)  # CPU

# ================== LOAD KNOWN FACES ==================
def load_known_faces(directory):
    if not os.path.exists(directory):
        print("Known faces directory does not exist.")
        return [], []

    embeddings = []
    names = []

    for filename in os.listdir(directory):
        if filename.lower().endswith((".jpg", ".png")):
            try:
                path = os.path.join(directory, filename)
                image = cv2.imread(path)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                faces = face_app.get(rgb)
                if not faces:
                    print(f"No face found in {filename}")
                    continue

                embeddings.append(faces[0].embedding)
                names.append(os.path.splitext(filename)[0])

            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return np.array(embeddings), np.array(names)

# ================== CAPTURE IMAGE ==================
def capture_image():
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_app.get(rgb)

        if results:
            for face in results:
                # Get bounding box from face object
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        cv2.imshow("Press SPACE to capture", frame)
        if cv2.waitKey(1) & 0xFF == ord(" "):
            cam.release()
            cv2.destroyAllWindows()
            return frame

    cam.release()
    cv2.destroyAllWindows()
    return None

# ================== RECOGNIZE FACE ==================
def recognize_face(image, known_embeddings, known_names):
    try:
        faces = face_app.get(image)
        if not faces:
            print("No face detected.")
            return []

        recognized = []

        for face in faces:
            emb = face.embedding.reshape(1, -1)
            similarities = cosine_similarity(emb, known_embeddings)
            best_idx = np.argmax(similarities)
            score = similarities[0][best_idx]

            if score >= SIMILARITY_THRESHOLD:
                recognized.append(known_names[best_idx])

        return recognized

    except Exception as e:
        print(f"Recognition error: {e}")
        return []

# ================== MARK ATTENDANCE ==================
def mark_attendance(student_name, file=ATTENDANCE_FILE):
    try:
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        month = now.strftime("%B")

        if os.path.exists(file):
            df = pd.read_excel(file)
        else:
            df = pd.DataFrame(columns=["Name", "Date", "Time", "Days_Present", "Month"])

        if ((df["Name"] == student_name) & (df["Date"] == date)).any():
            print(f"Attendance already marked for {student_name}")
            return

        monthly = df[(df["Name"] == student_name) & (df["Month"] == month)]
        days_present = monthly["Days_Present"].max() + 1 if not monthly.empty else 1

        new_row = {
            "Name": student_name,
            "Date": date,
            "Time": time,
            "Days_Present": days_present,
            "Month": month
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(file, index=False)

        print(f"Attendance marked for {student_name}")

    except Exception as e:
        logging.error(f"Attendance error: {e}")

# ================== MAIN ==================
def main():
    known_embeddings, known_names = load_known_faces(KNOWN_FACES_DIR)

    if len(known_embeddings) == 0:
        print("No known faces loaded.")
        return

    image = capture_image()
    if image is None:
        return

    recognized = recognize_face(image, known_embeddings, known_names)

    if not recognized:
        print("Student not recognized!")
        return

    for name in recognized:
        mark_attendance(name)

if __name__ == "__main__":
    main()
