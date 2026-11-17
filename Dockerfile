FROM python:3.12-alpine

LABEL org.opencontainers.image.title="SIF Edge" \
      org.opencontainers.image.description="SIF's implementation for Edge/Cloud Systems" \
      org.opencontainers.image.vendor="CAPS" \
      org.opencontainers.image.licenses="AGPLv3" \
      org.opencontainers.image.source="https://github.com/CAPS-IoT/sif-edge"

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app/

ENTRYPOINT [ "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "9000"]
