FROM python:3.12.4

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir torch torchvision torchaudio

RUN pip install -r requirements.txt

COPY . .

# CMD ["python", "main.py"] 