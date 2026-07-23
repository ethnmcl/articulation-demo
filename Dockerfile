FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY signal_diagnostic_model.pkl .
COPY form_scorer_model.pkl .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
