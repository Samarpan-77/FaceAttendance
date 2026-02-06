# FaceAttendance

A lightweight Python app that recognizes faces from a webcam feed and writes attendance records to an Excel file. Designed for quick setup in classrooms, offices, and small teams.

## Highlights

- Fast face recognition using `insightface`
- Automatic attendance logging to Excel
- Simple webcam capture flow
- Error logging for troubleshooting
- Flask-based UI for one-click capture

## Requirements

- Python 3.x
- OpenCV (`opencv-python`)
- `insightface`
- `pandas`
- `openpyxl`
- `flask`
- `scikit-learn`

## Setup

1. Clone the repo.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a folder with known faces (one image per person).
4. Update `KNOWN_FACES_DIR` in `FaceAttendance.py` to point to that folder.
5. Ensure `ATTENDANCE_FILE` in `FaceAttendance.py` points to a writable Excel file path.

## Run

```bash
python FaceAttendance.py
```

Then open the UI in your browser:

- `http://127.0.0.1:5000`

## How It Works

1. Click "Start Camera" in the web UI.
2. Click "Capture" to recognize faces and mark attendance.
3. Matches detected faces against the known faces folder.
4. Writes attendance to an Excel sheet.

## Add Student (New)

You can add students directly from the UI:

1. Click "Start Camera".
2. Enter a student name.
3. Click "Add Student".

The app saves a face image as `Name_With_Underscores.png` inside `KNOWN_FACES_DIR` and reloads the known faces cache.

## Troubleshooting

- If recognition fails, use clear, well-lit images in your known faces folder.
- If adding a student fails, make sure a face is clearly visible and the name is valid.
- If the Excel file won’t update, check write permissions.
- Review the error log for detailed failures.

## Contributing

PRs welcome. Fork the repo, create a branch, and submit a pull request.

## License

MIT — see `LICENSE`.

## Acknowledgments

- `insightface` for face embeddings and detection
- OpenCV for camera capture
- `pandas` and `openpyxl` for Excel output
