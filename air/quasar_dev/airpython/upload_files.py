from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil
import os
from datetime import datetime

app = FastAPI()

# ✅ Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allow requests from any domain
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # ✅ Allow all headers
)

# Define base upload directory
UPLOAD_BASE_DIR = "/home/datavan/quasar/images/"

@app.post("/upload_file")
async def upload_file(
    project: str = Form(...),  # ✅ Get project name from FormData
    file: UploadFile = File(...),
    json_file: Optional[UploadFile] = File(None)  # ✅ Renamed `json` to `json_file` to avoid conflict
):
    # ✅ Create a folder for the current month (e.g., "2025-03")
    current_month = datetime.now().strftime("%Y-%m")
    project_dir = os.path.join(UPLOAD_BASE_DIR, project, current_month)
    os.makedirs(project_dir, exist_ok=True)  # ✅ Ensure the directory exists

    # ✅ Save PNG Image
    image_path = os.path.join(project_dir, file.filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ✅ Save JSON Data (if provided)
    json_path = None
    if json_file:
        json_path = os.path.join(project_dir, json_file.filename)
        with open(json_path, "wb") as buffer:
            shutil.copyfileobj(json_file.file, buffer)

    return {
        "message": "✅ Files uploaded successfully",
        "image_path": image_path,
        "json_path": json_path if json_file else None,
        "project": project
    }
