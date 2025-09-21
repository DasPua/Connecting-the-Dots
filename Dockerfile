FROM python:3.12.4

WORKDIR /app

COPY requirements.txt .


# Install PyTorch + Torchvision + Torchaudio (CPU & GPU support)
RUN pip install --no-cache-dir torch torchvision torchaudio

# Install other dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .    

# Expose port (important for container networking)
EXPOSE 5000

# Set default command to run the app
CMD ["python", "app.py"]
=======
RUN pip install --no-cache-dir torch torchvision torchaudio

RUN pip install -r requirements.txt

COPY . .

# CMD ["python", "main.py"] 
