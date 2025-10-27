FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG PROJECT_DIR

WORKDIR /src

COPY requirements.txt /src/requirements.txt

RUN apt-get update && apt-get -y install libpq-dev gcc python3-dev musl-dev netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY . /src

CMD ["python", "main.py"]