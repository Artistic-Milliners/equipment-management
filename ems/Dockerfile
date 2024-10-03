FROM python:3.12.6-slim-bookworm

WORKDIR /usr/src/ems

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/ems/entrypoint.sh
RUN chmod +x /usr/src/ems/entrypoint.sh

COPY . .

ENTRYPOINT [ "/usr/src/ems/entrypoint.sh" ]