import os
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")

import uuid
import tempfile
import subprocess
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from faster_whisper import WhisperModel


# ----------------------------
# تنظیمات مدل (با ENV هم قابل تغییر)
# ----------------------------
MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")     # tiny/base/small/medium/large
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")         # cpu یا cuda
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "int8") # برای cpu: int8 / برای cuda: float16

app = FastAPI(title="Persian Speech-to-Text")

# استاتیک (فرانت) را سرو می‌کنیم
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ----------------------------
# مدل را یک‌بار در شروع برنامه لود می‌کنیم
# ----------------------------
model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

#model = WhisperModel("large-v3", device="cpu", compute_type="int8")
#مدل سنگین و بهتر برای دقت بالاتر
def ffmpeg_to_wav_16k_mono(input_path: str, output_path: str) -> None:
    """
    هر چیزی (webm/ogg/mp3/m4a/wav/...) را تبدیل می‌کند به:
    WAV - PCM 16bit - 16kHz - Mono
    """
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", input_path,
        "-acodec", "pcm_s16le",
        "-ac", "1",
        "-ar", "16000",
        output_path,
    ]


    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        err = p.stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(err)


def do_transcribe(wav_path: str, language: str, with_timestamps: bool) -> Dict[str, Any]:
    """
    اجرای سنگین مدل (blocking) — این را داخل thread اجرا می‌کنیم.
    """
    segments, info = model.transcribe(
        wav_path,
        language=language,     # "fa"
        vad_filter=True,       # حذف سکوت‌ها
    )

    if with_timestamps:
        segs = []
        texts = []
        for s in segments:
            t = (s.text or "").strip()
            if t:
                texts.append(t)
            segs.append({"start": float(s.start), "end": float(s.end), "text": t})
        return {
            "language": info.language,
            "duration": float(info.duration or 0),
            "text": " ".join(texts).strip(),
            "segments": segs,
        }

    # بدون تایم‌استمپ
    texts = [(s.text or "").strip() for s in segments]
    text = " ".join([t for t in texts if t]).strip()
    return {
        "language": info.language,
        "duration": float(info.duration or 0),
        "text": text,
    }


@app.get("/")
def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.post("/api/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Query("fa", description="مثلاً fa"),
    timestamps: bool = Query(False, description="اگر true باشد، segmentها هم برمی‌گردد"),
):
    # محافظت ساده
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="فایل خالی است.")
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="فایل خیلی بزرگ است (حد 25MB).")

    with tempfile.TemporaryDirectory() as td:
        raw_path = os.path.join(td, f"raw_{uuid.uuid4().hex}")
        wav_path = os.path.join(td, "audio.wav")

        with open(raw_path, "wb") as f:
            f.write(data)

        try:
            await run_in_threadpool(ffmpeg_to_wav_16k_mono, raw_path, wav_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"تبدیل ffmpeg شکست خورد: {e}")

        try:
            result = await run_in_threadpool(do_transcribe, wav_path, language, timestamps)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ترنسکرایب شکست خورد: {e}")

        return result
