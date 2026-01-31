FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install System Dependencies (The "Nuclear" CV Suite)
# We add 'libxcb1' and 'libgl1' to fix the "Shared Object" crashes.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install CPU-Only PyTorch (Keeps image small)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 3. Install Requirements
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Code
COPY . /app/

# 5. Entrypoint Setup
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//g' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]