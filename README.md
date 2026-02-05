# FaceAttendance

A lightweight Python app that recognizes faces from a webcam feed and writes attendance records to an Excel file. Designed for quick setup in classrooms, offices, and small teams.

## Highlights
- Fast face recognition using `face_recognition`
- Automatic attendance logging to Excel
- Simple webcam capture flow
- Error logging for troubleshooting

## Requirements
- Python 3.x
- OpenCV (`opencv-python`)
- `face_recognition`
- `pandas`
- `openpyxl`

## Setup
1. Clone the repo.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a folder with known faces (one image per person).
4. Update `KNOWN_FACES_DIR` in `FaceAttendance.py` to point to that folder.

## Run
```bash
python FaceAttendance.py
```

## How It Works
1. Captures a frame from your default camera.
2. Matches detected faces against the known faces folder.
3. Writes attendance to an Excel sheet.

## Troubleshooting
- If recognition fails, use clear, well-lit images in your known faces folder.
- If the Excel file won�t update, check write permissions.
- Review the error log for detailed failures.

## Contributing
PRs welcome. Fork the repo, create a branch, and submit a pull request.

## License
MIT � see `LICENSE`.

## Acknowledgments
- `face_recognition` for facial encoding and matching
- OpenCV for camera capture
- `pandas` and `openpyxl` for Excel output
