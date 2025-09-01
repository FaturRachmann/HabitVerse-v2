from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from typing import Optional

router = APIRouter()

UPLOAD_DIR = os.path.join("app", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _safe_ext(filename: str) -> str:
    base, ext = os.path.splitext(filename)
    ext = ext.lower()
    # allow only common image extensions
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return ext
    return ""


@router.post("/uploads/image")
async def upload_image(file: UploadFile = File(...)):
    # basic validation
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar")

    ext = _safe_ext(file.filename or "")
    if not ext:
        # Fall back from content-type if filename doesn't have safe ext
        guessed = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }.get(content_type, "")
        if not guessed:
            raise HTTPException(status_code=400, detail="Ekstensi gambar tidak didukung")
        ext = guessed

    fname = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, fname)

    try:
        with open(path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    finally:
        await file.close()

    url = f"/static/uploads/{fname}"
    return JSONResponse({"url": url})
