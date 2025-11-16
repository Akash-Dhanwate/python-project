Hospital Management System (Python + Tkinter + SQLite)

A modern, offline hospital record management application built with Python.
The system allows operators to store, retrieve, preview, and manage patient and prescription data using a clean GUI, local database, QR code generation, visual effects, and audit logging.

🚀 Overview

This project is a desktop-based Hospital Management System created using:

Python

Tkinter (GUI)

SQLite (local database)

Pillow (image handling)

qrcode (QR generation)

The app runs fully offline and automatically stores all data inside a single file:
hospital.db

It includes extra polished features like animated particle backgrounds, time-based themes, ripple save effects, sound notifications, operator login, and action auditing.

✨ Features
1. Patient & Prescription Entry

Input fields for tablets, dose, dates, side effects, patient details, etc.

Clean layout using Tkinter’s ttk styling.

2. Local Database (SQLite)

Auto-creates tables on first launch.

Saves all records in hospital.db.

No external server required.

3. Record Table View

Bottom table shows all saved entries.

Clicking a row loads it back into the form.

4. Prescription Preview

Neatly formatted preview panel.

Displays all patient and medication information.

5. QR Code Generation

Automatically generates a QR image: qr_<reference>.png

Encodes reference, tablet name, and patient name as JSON.

“Show QR” button opens popup preview.

6. Operator Login System

User must enter Name + Role before using the system.

Stored for audit logs.

7. Audit Logging

Every important action is recorded:

Save

Preview

Delete

Show QR

Clear

Stored in audit_log table with timestamp + operator identity.

8. UI Enhancements

Particle animation background.

Time-based themes: morning, afternoon, night.

Theme switch button.

Ripple effect when saving data.

Sound feedback for Save, Delete, Error, QR.

Keyboard shortcuts:

Ctrl + Q: Quick QR popup

Ctrl + Shift + F: Toggle table visibility

📦 Requirements

Install dependencies:

pip install qrcode pillow


The app uses winsound for audio on Windows (no installation required).
If on another OS, you can optionally install a sound library like playsound.

▶️ How to Run

Ensure Python 3.8+ is installed.

Put all files in one folder.

Open terminal in that folder.

Run:

python Hospitalmanagenmentsystem.py

Operator login window will appear.

Fill the form → Save / Preview → View records in table.

📁 Project Structure
|-- hospital_app.py
|-- hospital.db           (auto-created)
|-- error.log             (auto-created on errors)
|-- qr_<ref>.png          (generated QR files)
|-- README.md
|-- *.wav                 (sound files if added)

⚙️ Database Schema
1. hospital table
Column	Description
nameoftablets	Tablet name
Refrence	Unique reference number
dose	Patient dosage
nooftablets	Quantity
issuedate	Date issued
expdate	Expiry date
dailydose	Daily dose
sideeffect	Known side effects
nameofpatient	Name of patient
dob	Date of birth
patientaddress	Full address
2. audit_log table

Tracks operator actions:

Operator name

Operator roll

Action name

Reference number

Timestamp

🧪 Error Logging

Any unexpected error (like database write failure) is written to error.log with the full traceback and timestamp.
The user only sees a clean error message.
