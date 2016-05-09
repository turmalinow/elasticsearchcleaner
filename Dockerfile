FROM python:3.5.1-alpine

COPY . /usr/src/myapp

WORKDIR /usr/src/myapp

RUN pip install -r requirements.txt

CMD python main.py
