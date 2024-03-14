FROM python:latest

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY test.py /app/test.py

CMD [ "python3", "test.py" ]