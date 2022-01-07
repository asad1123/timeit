FROM python:3.8-alpine as base

# BUILD STAGE
FROM base as builder

RUN mkdir -p /install
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN apk update \
    && pip install --prefix=/install -r /requirements.txt

# DEPLOY STAGE
FROM base

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app
COPY gunicorn.py .

EXPOSE 8000
CMD [ "gunicorn", "-c", "gunicorn.py", "app:app"]
