from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import json

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Static files directory
static_dir = Path("static")
uploads_dir = static_dir / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data storage file
data_file = static_dir / "data.json"
if not data_file.exists():
    with data_file.open("w") as f:
        json.dump({"courses": []}, f)

# Serve the User Dashboard on root (`/`)
@app.get("/", response_class=HTMLResponse)
async def serve_user_dashboard():
    with open("user_dashboard.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Serve the Admin Dashboard
@app.get("/admin_dashboard", response_class=HTMLResponse)
async def serve_admin_dashboard():
    with open("admin_dashboard.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Add a new course
@app.post("/add_course")
async def add_course(title: str = Form(...)):
    with data_file.open("r+") as f:
        data = json.load(f)
        new_course = {"title": title, "plans": []}
        data["courses"].append(new_course)
        f.seek(0)
        json.dump(data, f, indent=4)
    return JSONResponse(content={"message": "Course added successfully", "course": new_course})

# Add a plan to a course
@app.post("/add_plan")
async def add_plan(course_title: str = Form(...), plan_name: str = Form(...), file: UploadFile = File(...)):
    file_path = uploads_dir / file.filename
    with file_path.open("wb") as f:
        f.write(await file.read())

    with data_file.open("r+") as f:
        data = json.load(f)
        for course in data["courses"]:
            if course["title"] == course_title:
                new_plan = {"name": plan_name, "pdf_path": str(file_path)}
                course["plans"].append(new_plan)
                break
        else:
            return JSONResponse(content={"error": "Course not found"}, status_code=404)

        f.seek(0)
        json.dump(data, f, indent=4)

    return JSONResponse(content={"message": "Plan added successfully", "plan": new_plan})

# Get all courses and plans for the user dashboard
@app.get("/get_courses")
async def get_courses():
    with data_file.open("r") as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
