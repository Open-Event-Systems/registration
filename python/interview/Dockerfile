FROM python:3.10.13-alpine3.18 AS base

FROM base AS build
RUN apk add git build-base
WORKDIR /build
RUN pip install --no-cache-dir poetry wheel
RUN python -m venv /app
COPY pyproject.toml poetry.lock ./
# hack: exclude oes-* dependencies due to git repos not having hashes
RUN poetry export | grep -v ^oes- > requirements.txt
RUN pip wheel --no-cache-dir -w deps -r requirements.txt
RUN /app/bin/pip install --no-cache-dir deps/*
COPY README.md ./
COPY oes/ oes/
RUN /app/bin/pip install --no-cache-dir .

FROM base AS interview-server
RUN adduser -h /app -H -D python \
    && mkdir /config
COPY --chown=root:python config.example.yml /config/config.yml
COPY --chown=root:python interviews.example.yml /config/interviews.yml
RUN chmod u=rw,g=r,o= /config/config.yml /config/interviews.yml
COPY --from=build /app/ /app/
WORKDIR /config
USER python
ENTRYPOINT [ "/app/bin/oes-interview" ]
CMD [ "--bind", "0.0.0.0", "--port", "8001" ]
