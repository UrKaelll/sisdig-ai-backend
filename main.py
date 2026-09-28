import json
import os
import shutil
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ==========================================
# PATENKAN PATH AGAR IMPORT DAN FOLDER KONSISTEN
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

sys.path.extend([str(BASE_DIR), str(ROOT_DIR)])

try:
    from ppt_reader import read_ppt
    from content_analyzer import analyze_content
    from ai_generator import generate_ai_media
    from media_generator import generate_media
except ImportError:
    from ppt_reader import read_ppt
    from content_analyzer import analyze_content
    from ai_generator import generate_ai_media
    from media_generator import generate_media

app = FastAPI(title="SISDIG AI")

# ==========================================
# PERBAIKAN CORS LENGKAP & AMAN UNTUK BROWSER
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# FOLDER PENYIMPANAN WAJIB DI /tmp/ (VERCEL READ-ONLY)
# ==========================================
UPLOAD_DIR = Path("/tmp/uploads")
GENERATED_DIR = Path("/tmp/generated")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

class RenameRequest(BaseModel):
    title: str


@app.get("/")
def home():
    return {"status": "online", "message": "SISDIG AI Backend berhasil berjalan!"}


@app.post("/upload")
async def upload_ppt(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".ppt", ".pptx")):
        return {"error": "File harus berupa PPT atau PPTX"}

    file_path = UPLOAD_DIR / Path(file.filename).name
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "PPT berhasil diupload", "filename": file_path.name}


@app.get("/analyze/{filename}")
def analyze_ppt(filename: str):
    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():
        return {"error": "File PPT tidak ditemukan"}

    slides_data = read_ppt(file_path)
    analyzed_content = analyze_content(slides_data)

    return {
        "filename": safe_filename,
        "total_slides": len(slides_data),
        "analysis": analyzed_content,
        "slides": slides_data
    }


@app.get("/generate/{filename}")
def generate_media_json(filename: str):
    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():
        return {"error": "File PPT tidak ditemukan"}

    slides_data = read_ppt(file_path)

    try:
        ai_media = generate_ai_media(slides_data)
        output_path = generate_media(ai_media, safe_filename)

        return {
            "message": "Media berhasil dibuat",
            "filename": safe_filename,
            "output": str(output_path),
            "media": ai_media
        }
    except Exception as error:
        return {"error": "Gagal membuat media", "detail": str(error)}


@app.post("/process")
async def process_ppt(
    file: UploadFile = File(...),
    week: int = Form(1)
):
    if not file.filename.lower().endswith((".ppt", ".pptx")):
        return {"error": "File harus berupa PPT atau PPTX"}

    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        slides_data = read_ppt(file_path)
        ai_media = generate_ai_media(slides_data)
        
        if isinstance(ai_media, str):
            ai_media = json.loads(ai_media)
        elif hasattr(ai_media, "dict"):
            ai_media = ai_media.dict()

        ai_media["week"] = week
        
        json_filename = f"{Path(safe_filename).stem}.json"
        json_path = GENERATED_DIR / json_filename
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ai_media, f, ensure_ascii=False, indent=2)

        return {
            "message": "PPT berhasil diproses",
            "filename": safe_filename,
            "total_slides": len(slides_data),
            "media_file": json_filename,
            "media": ai_media
        }
    except Exception as error:
        return {"error": "Gagal memproses PPT", "detail": str(error)}


@app.get("/media/{filename}")
def get_media(filename: str):
    safe_filename = Path(filename).name
    file_path = GENERATED_DIR / safe_filename

    if not file_path.exists():
        return {"error": "Media JSON tidak ditemukan"}

    return FileResponse(path=file_path, media_type="application/json")


# ==========================================
# FITUR MANAJEMEN MATERI
# ==========================================

@app.get("/materials")
def list_materials():
    materials = []
    if GENERATED_DIR.exists():
        for file_path in GENERATED_DIR.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    materials.append({
                        "filename": file_path.name,
                        "title": content.get("title", file_path.stem),
                        "course": content.get("course", "Sistem Digital"),
                        "week": content.get("week", 0)
                    })
            except Exception:
                continue
    return materials


@app.put("/materials/{filename}/rename")
def rename_material(filename: str, req: RenameRequest):
    safe_filename = Path(filename).name
    file_path = GENERATED_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File media tidak ditemukan")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        content["title"] = req.title

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

        return {"message": "Judul berhasil diubah", "title": req.title}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Gagal mengubah nama: {str(error)}")


@app.delete("/materials/{filename}")
def delete_material(filename: str):
    safe_filename = Path(filename).name
    file_path = GENERATED_DIR / safe_filename

    if file_path.exists():
        os.remove(file_path)
        return {"message": "Materi berhasil dihapus"}

    raise HTTPException(status_code=404, detail="File media tidak ditemukan")
