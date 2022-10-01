FROM python:3.10-slim

WORKDIR /bot

COPY ./requirements.txt .
COPY ./src .

RUN pip install --no-cache-dir -r requirements.txt

CMD python src/botislav/__main__.py