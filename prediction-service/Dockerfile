FROM python:3.10-slim

WORKDIR /app

# Copy all files
COPY . .


RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["python", "prediction.py"]
