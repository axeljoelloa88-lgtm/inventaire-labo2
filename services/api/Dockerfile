FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
HEALTHCHECK --interval=15s --timeout=5s --retries=4 \
    CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
CMD ["python", "app.py"]
