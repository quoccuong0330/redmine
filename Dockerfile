FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY redmine_client.py email_renderer.py email_sender.py daily-digest.py ./

CMD ["python", "daily-digest.py"]
