from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI()

# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database
database = {"courses": {}}


@app.post("/admin/courses/")
async def add_course(title: str = Form(...)):
    if title in database["courses"]:
        return JSONResponse(content={"message": "Course already exists"}, status_code=400)
    database["courses"][title] = {"plans": []}
    return {"message": f"Course '{title}' added successfully"}


@app.get("/admin/courses/")
async def get_courses():
    return [{"title": title} for title in database["courses"]]


@app.post("/admin/courses/{course_title}/plans/")
async def add_plan(course_title: str, name: str = Form(...), pdf: UploadFile = File(...)):
    if course_title not in database["courses"]:
        return JSONResponse(content={"message": "Course not found"}, status_code=404)

    # Save the uploaded PDF
    save_dir = f"./uploads/{course_title}"
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, pdf.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)

    # Add the plan to the course
    database["courses"][course_title]["plans"].append({"name": name, "pdf_path": file_path})
    return {"message": f"Plan '{name}' added successfully"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
