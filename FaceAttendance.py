import cv2
import os
import base64
import numpy as np
import pandas as pd
import logging
import re
from datetime import datetime
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify

# ================== CONSTANTS ==================
KNOWN_FACES_DIR = r"Location to Students Images"
ATTENDANCE_FILE = r"Location to Your xlms file"
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

# ================== FLASK ==================
app = Flask(__name__)

# Cache known embeddings to avoid reloading on each request
_known_embeddings = None
_known_names = None

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
                if image is None:
                    print(f"Failed to read {filename}")
                    continue

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


def get_known_faces():
    global _known_embeddings, _known_names
    if _known_embeddings is None or _known_names is None:
        _known_embeddings, _known_names = load_known_faces(KNOWN_FACES_DIR)
    return _known_embeddings, _known_names

def invalidate_known_faces_cache():
    global _known_embeddings, _known_names
    _known_embeddings = None
    _known_names = None

# ================== IMAGE HELPERS ==================
def decode_data_url_to_bgr(data_url):
    try:
        header, encoded = data_url.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None

# ================== RECOGNIZE FACE ==================
def recognize_face(image_bgr, known_embeddings, known_names):
    try:
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        faces = face_app.get(rgb)
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

# ================== ADD STUDENT ==================
def normalize_student_name(name):
    name = (name or "").strip()
    name = re.sub(r"\s+", " ", name)
    if not name:
        return ""
    safe = re.sub(r"[^A-Za-z0-9 _-]", "", name)
    safe = safe.strip().replace(" ", "_")
    return safe

def save_student_image(image_bgr, student_name, directory=KNOWN_FACES_DIR):
    safe_name = normalize_student_name(student_name)
    if not safe_name:
        return {"status": "bad_name", "message": "Please enter a valid student name."}

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    faces = face_app.get(rgb)
    if not faces:
        return {"status": "no_face", "message": "No face detected. Please try again."}

    file_path = os.path.join(directory, f"{safe_name}.png")
    if os.path.exists(file_path):
        return {"status": "exists", "message": "Student already exists."}

    ok = cv2.imwrite(file_path, image_bgr)
    if not ok:
        return {"status": "save_failed", "message": "Could not save image."}

    invalidate_known_faces_cache()
    return {"status": "saved", "message": f"Saved {safe_name}."}

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
            return "already_marked"

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
        return "marked"

    except Exception as e:
        logging.error(f"Attendance error: {e}")
        return "error"

# ================== CAPTURE + ATTEND ==================
def recognize_and_mark(image_bgr):
    known_embeddings, known_names = get_known_faces()

    if len(known_embeddings) == 0:
        return {
            "status": "no_known_faces",
            "message": "No known faces loaded. Check your Students folder path."
        }

    recognized = recognize_face(image_bgr, known_embeddings, known_names)

    if not recognized:
        return {"status": "not_recognized", "message": "Student not recognized."}

    results = []
    for name in recognized:
        result = mark_attendance(name)
        results.append((name, result))

    return {"status": "done", "recognized": results}

# ================== FLASK ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/capture", methods=["POST"])
def capture():
    payload = request.get_json(silent=True) or {}
    data_url = payload.get("image")
    if not data_url:
        return jsonify({"status": "no_image", "message": "No image received."}), 400

    image = decode_data_url_to_bgr(data_url)
    if image is None:
        return jsonify({"status": "bad_image", "message": "Could not decode image."}), 400

    result = recognize_and_mark(image)
    return jsonify(result)

@app.route("/add_student", methods=["POST"])
def add_student():
    payload = request.get_json(silent=True) or {}
    data_url = payload.get("image")
    student_name = payload.get("name")
    if not data_url:
        return jsonify({"status": "no_image", "message": "No image received."}), 400
    if not student_name:
        return jsonify({"status": "bad_name", "message": "Student name is required."}), 400

    image = decode_data_url_to_bgr(data_url)
    if image is None:
        return jsonify({"status": "bad_image", "message": "Could not decode image."}), 400

    result = save_student_image(image, student_name)
    return jsonify(result)

# ================== MAIN ==================
def main():
    app.run(host="127.0.0.1", port=5000, debug=True)

if __name__ == "__main__":
    main()
