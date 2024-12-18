FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app/

ENTRYPOINT [ "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "9000"]
