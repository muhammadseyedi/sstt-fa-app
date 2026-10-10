# تبدیل گفتار فارسی به متن (Speech-to-Text)

یک وب‌اپلیکیشن سبک با **FastAPI** و **faster-whisper** برای تبدیل فایل‌های صوتی به متن فارسی. کاربر می‌تواند در مرورگر صدا ضبط کند یا فایل صوتی موجود را آپلود کند.

## قابلیت‌ها

- ضبط صدا در مرورگر و بارگذاری فایل صوتی.
- تبدیل ورودی صوتی به WAV تک‌کاناله با نرخ نمونه‌برداری 16 kHz با استفاده از FFmpeg.
- تبدیل گفتار به متن توسط faster-whisper.
- امکان دریافت متن همراه با زمان شروع و پایان segmentها.
- تنظیم مدل، device و نوع محاسبه از طریق متغیرهای محیطی.

> **وضعیت پروژه:** این مخزن کد برنامه را ارائه می‌کند، اما در حال حاضر بنچمارک دقت فارسی (مانند WER/CER)، نمونه‌ی صوتی مرجع و دمو میزبانی‌شده ارائه نشده‌اند. بنابراین کیفیت مدل روی داده‌های مشخص فارسی در این مخزن به‌صورت کمی ارزیابی نشده است.

## پیش‌نیازها

- Python 3.11 یا جدیدتر.
- FFmpeg قابل اجرا از طریق `PATH` یا مسیر مشخص‌شده با `FFMPEG_BIN`.
- اتصال اینترنت برای دانلود اولیه‌ی مدل.
- فضای ذخیره‌سازی کافی برای مدل انتخابی.

## ساختار پروژه

```text
sstt-fa-app/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── static/
│   └── index.html
├── .gitignore
└── README.md
```

## نصب و اجرا

### Windows PowerShell

از ریشه‌ی مخزن اجرا کنید:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel

# نصب پیش‌نیازهای Python
python -m pip install -r .\backend\requirements.txt

# اجرای سرور
Set-Location .\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Linux / macOS

از ریشه‌ی مخزن اجرا کنید:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r backend/requirements.txt

cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

سپس در مرورگر آدرس [http://127.0.0.1:8000/](http://127.0.0.1:8000/) را باز کنید.

## نصب FFmpeg

FFmpeg باید در همان محیطی که سرور را اجرا می‌کنید قابل دسترسی باشد.

در Windows می‌توانید پس از نصب، بررسی کنید:

```powershell
where.exe ffmpeg
ffmpeg -version
```

در Linux/macOS:

```bash
which ffmpeg
ffmpeg -version
```

اگر FFmpeg در `PATH` نیست، مسیر فایل اجرایی را با متغیر `FFMPEG_BIN` مشخص کنید. در PowerShell:

```powershell
$env:FFMPEG_BIN="C:\path\to\ffmpeg.exe"
```

این متغیر فقط برای همان نشست PowerShell فعال می‌ماند، مگر آن‌که به‌شکل دائمی در سیستم تنظیم شود.

## تنظیمات مدل

تنظیمات زیر پیش از شروع سرور خوانده می‌شوند:

| متغیر | مقدار پیش‌فرض | توضیح |
|---|---|---|
| `WHISPER_MODEL` | `small` | مدل faster-whisper |
| `WHISPER_DEVICE` | `cpu` | دستگاه اجرا، معمولاً `cpu` یا `cuda` |
| `WHISPER_COMPUTE` | `int8` | نوع محاسبه؛ `int8` معمولاً برای CPU مناسب است |
| `FFMPEG_BIN` | `ffmpeg` | مسیر FFmpeg یا نام قابل اجرا از `PATH` |

برای نمونه در PowerShell:

```powershell
$env:WHISPER_MODEL="medium"
$env:WHISPER_DEVICE="cpu"
$env:WHISPER_COMPUTE="int8"
```

مدل‌های بزرگ‌تر می‌توانند حافظه و زمان بیشتری مصرف کنند؛ انتخاب مناسب به سخت‌افزار و نیاز دقت/سرعت بستگی دارد. سازگاری CUDA به نصب نسخه‌های سازگار از درایور و وابستگی‌های لازم نیز وابسته است.

## API

### `POST /api/transcribe`

فایل را با `multipart/form-data` و نام فیلد `file` ارسال کنید.

پارامترهای query:

- `language`: کد زبان؛ پیش‌فرض `fa`.
- `timestamps`: اگر `true` باشد، segmentهای زمان‌بندی‌شده نیز برگردانده می‌شوند؛ پیش‌فرض `false`.

نمونه:

```bash
curl -X POST \
  -F "file=@sample.wav" \
  "http://127.0.0.1:8000/api/transcribe?language=fa&timestamps=true"
```

پاسخ شامل زبان تشخیص‌داده‌شده، مدت زمان صوت و متن است. در صورت فعال‌بودن `timestamps`، آرایه‌ی `segments` نیز شامل زمان شروع، پایان و متن هر قطعه خواهد بود.

فایل خالی با خطای `400` و فایل بزرگ‌تر از 25 MiB با خطای `413` رد می‌شود. خطاهای تبدیل یا تشخیص گفتار نیز در پاسخ API گزارش می‌شوند.

## محدودیت‌ها و کارهای بعدی

- کیفیت تشخیص گفتار هنوز با WER/CER روی مجموعه‌ای از فایل‌های فارسی سنجیده نشده است.
- زمان پاسخ و مصرف حافظه برای اندازه‌های مختلف مدل ثبت نشده‌اند.
- پیش از استقرار عمومی، احراز هویت، محدودسازی نرخ درخواست، محدودیت مدت صوت، مدیریت صف و نظارت بر خطاها را اضافه کنید.
- سرویس فعلی برای اجرا به‌شکل محلی مستند شده است؛ دسترسی شبکه‌ای گسترده را فقط در صورت نیاز و پس از اعمال ملاحظات امنیتی فعال کنید.
