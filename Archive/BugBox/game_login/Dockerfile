FROM python:3.12-slim

# System deps:
# - libzbar0 for pyzbar (QR decode)
# - libgl1 + libglib2.0-0 commonly needed for opencv-python on slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "game_login.py", "--server.address=0.0.0.0", "--server.port=8501"]
