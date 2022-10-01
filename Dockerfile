FROM python:3.10-slim

WORKDIR /usr/src/app

ENV PYTHONPATH=/usr/src/app/src/:$PYTHONPATH

COPY ./requirements.txt ./
COPY ./src ./src

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/botislav/__main__.py"]