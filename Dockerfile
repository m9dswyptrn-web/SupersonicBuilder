# ---- Base (slim) ----
FROM python:3.14-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# System deps (for pyttsx3 backends + basic TTS capability)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libespeak-ng1 libasound2 libasound2-data libasound2-plugins \
    build-essential curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# ---- Deps ----
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn

# ---- App ----
COPY . .

# Expose panel port; Render/Heroku pass $PORT
EXPOSE 5055

# Default: gunicorn serve panel
CMD ["sh", "-c", "gunicorn supersonic_settings_server:app --bind 0.0.0.0:${PORT:-5055} --workers 2 --threads 4 --timeout 120"]
