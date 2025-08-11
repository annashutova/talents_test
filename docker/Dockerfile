FROM python:3.11 as base

ENV C_FORCE_ROOT=True
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/code
ENV TZ=Europe/Moscow

WORKDIR /code

RUN apt-get update && apt-get install -y tzdata

RUN /usr/local/bin/python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry==2.1.1

COPY pyproject.toml /code/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev \
    && echo yes | poetry cache clear . --all

RUN adduser --disabled-password appuser
USER appuser


## stand image
#FROM base AS prod
#
#COPY . .
#
#RUN mkdir -p /var/log && chmod -R 1777 /var/log
#
#USER 1001

# tests image
FROM base AS test

RUN poetry install --no-interaction --no-ansi --with dev

#USER 1001