FROM python:3.7-alpine

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

WORKDIR /crawler

COPY *.py /crawler/

ENTRYPOINT ["python", "crawler.py"]