FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Render injects $PORT at runtime; default to 8000 for local `docker run` testing
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
