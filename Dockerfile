# syntax=docker/dockerfile:1

FROM python:3.11-alpine

WORKDIR /docker-basket

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN python3 -m flask db upgrade


EXPOSE 7000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]