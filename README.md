# FaceAttendance
**Table of Contents**

Introduction

Features

Requirements

Installation

Usage

Troubleshooting

Contributing

License

Introduction

FaceAttendance is a Python script that uses face recognition technology to automate attendance marking. It captures images, recognizes faces, and marks attendance in an Excel file with ease. This script is designed to simplify the attendance tracking process, making it ideal for schools, offices, and other organizations.

**Features**

Face Recognition: Uses the face_recognition library to recognize faces in captured images.

Automated Attendance: Marks attendance for recognized students in an Excel file.

Error Handling: Logs errors to a file for easy troubleshooting.

Easy to Use: Simple and intuitive interface for capturing images and marking attendance.

**Requirements**

Python 3.x: The script is written in Python 3.x and requires a compatible version to run.

OpenCV: The OpenCV library is required for image capture and processing.

face_recognition: The face_recognition library is required for face recognition.

pandas: The pandas library is required for Excel file manipulation.

openpyxl: The openpyxl library is required for Excel file manipulation.

**Installation**

Clone the repository using git clone https://github.com/Samarpan-77/FaceAttendance.git.
Install the required libraries using pip install -r requirements.txt.
Create a directory for known faces and add images of students.
Update the KNOWN_FACES_DIR variable in the script to point to the known faces directory.

**Usage**

Run the script using python FaceAttendance.py.


Capture an image of a student using the default camera.

The script will recognize the student's face and mark their attendance in the Excel file.

**Troubleshooting**

Error Logging: Check the error log file for any issues.

Face Recognition: Ensure that the known faces directory is correctly configured and that the images are clear and well-lit.

Excel File: Ensure that the Excel file is correctly configured and that the script has write permissions.

**Contributing**

Contributions are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request.

**License**

FaceAttendance is licensed under the MIT License. See the LICENSE file for more information.

**Acknowledgments**

The face_recognition library is used for face recognition.

The OpenCV library is used for image capture and processing.

The pandas and openpyxl libraries are used for Excel file manipulation.
