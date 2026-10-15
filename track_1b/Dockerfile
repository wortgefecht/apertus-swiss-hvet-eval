FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY src ./track_1b/src
COPY data ./track_1b/data

ENTRYPOINT ["python", "track_1b/src/run.py"]
CMD ["--reproduce"]
