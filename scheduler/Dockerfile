FROM python:3.8-alpine as base

# BUILD STAGE
FROM base as builder

RUN mkdir -p /install
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN apk update \
    && apk add python3-dev \
            gcc \
            libc-dev \
            tzdata \
    && pip install --prefix=/install -r /requirements.txt

# DEPLOY STAGE
FROM base

WORKDIR /app

COPY --from=builder /install /usr/local
COPY scheduler.py schemas.py settings.py /app/

CMD [ "python", "scheduler.py" ]
