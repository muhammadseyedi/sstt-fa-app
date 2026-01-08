تبدیل ویس فارسی به متن (STT) — FastAPI + faster-whisper

این پروژه یک وب‌اپ ساده برای تبدیل صوت فارسی به متن است:

ضبط صدا داخل مرورگر یا آپلود فایل صوتی

تبدیل فرمت با ffmpeg به WAV استاندارد (16kHz mono)

تبدیل صوت به متن با faster-whisper (Whisper)

پیش‌نیازها

Python 3.11+

ffmpeg (ضروری)

اینترنت برای دانلود اولیه مدل (فقط بار اول)

ساختار پروژه
stt-fa-app/
  backend/
    main.py
    requirements.txt
  static/
    index.html
  .venv/            (بعد از ساخت venv)

نصب و راه‌اندازی
ویندوز (PowerShell)

از داخل فولدر backend اجرا کنید.

cd .\backend

python -m venv ..\.venv
& ..\.venv\Scripts\Activate.ps1

python -m pip install -U pip setuptools wheel

# پیشنهاد می‌کنم این رو جدا نصب کنید تا pip سراغ build از سورس نره
python -m pip install --only-binary=:all: "ctranslate2>=4.6.3"

python -m pip install -r requirements.txt

لینوکس / مک
cd ./backend

python3 -m venv ../.venv
source ../.venv/bin/activate

python -m pip install -U pip setuptools wheel

# پیشنهاد می‌کنم این رو جدا نصب کنید تا pip سراغ build از سورس نره
python -m pip install --only-binary=:all: "ctranslate2>=4.6.3"

python -m pip install -r requirements.txt

ffmpeg (خیلی مهم)

اگر ffmpeg در دسترس نباشد معمولاً این خطا را می‌بینید:

تبدیل ffmpeg شکست خورد: [WinError 2] The system cannot find the file specified

تست نصب بودن ffmpeg

ویندوز:

where ffmpeg
ffmpeg -version


لینوکس/مک:

which ffmpeg
ffmpeg -version

نصب سریع روی ویندوز با winget
winget install --id Gyan.FFmpeg


بعد از نصب:

همه ترمینال‌ها را ببندید

یک PowerShell جدید باز کنید

دوباره تست بزنید:

where ffmpeg
ffmpeg -version

اگر ffmpeg داخل ترمینال پروژه شناخته نشد (راه قطعی)

گاهی ffmpeg نصب هست ولی داخل یک ترمینال خاص شناخته نمی‌شود. در این حالت می‌شود مسیر ffmpeg.exe را مستقیم با متغیر محیطی به برنامه داد.

مسیر دقیق ffmpeg را پیدا کنید:

where ffmpeg


همان مسیر را ست کنید (مثال):

$env:FFMPEG_BIN="C:\path\to\ffmpeg.exe"
& "$env:FFMPEG_BIN" -version


روش خودکار (بدون کپی‌کاری):

$ff = (where.exe ffmpeg | Select-Object -First 1)
$env:FFMPEG_BIN = $ff
& "$env:FFMPEG_BIN" -version


نکته: $env:FFMPEG_BIN=... فقط برای همان پنجره PowerShell است.

اجرای برنامه

داخل backend و در حالی که venv فعال است:

python -m uvicorn main:app --host 0.0.0.0 --port 8000


بعد در مرورگر:

http://localhost:8000/

API
POST /api/transcribe

ورودی: فایل صوتی (multipart/form-data)
خروجی: JSON شامل متن

پارامترها:

language (پیش‌فرض fa)

timestamps (پیش‌فرض false) اگر true باشد، segmentها با زمان شروع/پایان هم برمی‌گردد.

مثال با curl:

curl -F "file=@sample.wav" "http://localhost:8000/api/transcribe?language=fa&timestamps=false"

افزایش دقت (پیشنهاد)

دقت خیلی به اندازه مدل بستگی دارد. برای کیفیت بهتر، مدل را بزرگ‌تر کنید.

قبل از اجرای سرور می‌توانید این env ها را ست کنید:

$env:WHISPER_MODEL="large-v3"   # یا medium / small
$env:WHISPER_DEVICE="cpu"       # اگر GPU دارید: cuda
$env:WHISPER_COMPUTE="int8"     # برای cpu معمولاً int8
python -m uvicorn main:app --host 0.0.0.0 --port 8000


پیشنهاد کلی:

بهترین کیفیت: large-v3 (کندتر/سنگین‌تر)

تعادل سرعت/کیفیت: medium

سریع‌تر ولی دقت کمتر: small

نکته‌های رایج
uvicorn شناخته نمی‌شود

روی ویندوز به جای uvicorn ... همیشه این را بزنید:

python -m uvicorn main:app --host 0.0.0.0 --port 8000

هشدار symlink از huggingface_hub

این خطا نیست؛ فقط یعنی کش مدل‌ها روی ویندوز ممکن است فضای بیشتری مصرف کند. اگر نمی‌خواهید نمایش داده شود:

$env:HF_HUB_DISABLE_SYMLINKS_WARNING="1"


اگر فضای درایو C کم است، کش را روی D ببرید:

$env:HF_HOME="D:\hf_cache"
$env:HUGGINGFACE_HUB_CACHE="D:\hf_cache\hub"

Troubleshooting سریع
خطای WinError 2 برای ffmpeg

داخل همان ترمینالی که سرور را اجرا می‌کنید:

where ffmpeg


اگر خروجی خالی بود:

یا PATH درست نیست

یا از روش FFMPEG_BIN (بخش ffmpeg) استفاده کنید