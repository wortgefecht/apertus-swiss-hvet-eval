FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./track_1b/requirements.txt
RUN pip install --no-cache-dir -r track_1b/requirements.txt

COPY src ./track_1b/src
COPY data ./track_1b/data

ENTRYPOINT ["python", "track_1b/src/run.py"]
CMD ["--reproduce"]
