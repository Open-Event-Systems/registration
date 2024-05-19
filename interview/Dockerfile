FROM python:3.12.3-alpine3.19 AS base


FROM base AS build-base
WORKDIR /build
RUN apk add git \
    && pip install --no-cache-dir poetry poetry-plugin-export


FROM build-base AS build
RUN python -m venv /app \
    && /app/bin/pip install --no-cache-dir setuptools
COPY pyproject.toml poetry.lock ./

# https://github.com/python-poetry/poetry-plugin-export/issues/69#issuecomment-1220142028
RUN poetry export -o requirements.txt \
    && grep 'git\+' requirements.txt > requirements-vcs.txt \
    && grep -v 'git\+' requirements.txt > requirements-hashed.txt \
    && /app/bin/pip install --no-cache-dir --no-deps -r requirements-vcs.txt \
    && /app/bin/pip install --no-cache-dir -r requirements-hashed.txt

COPY oes/ oes/
RUN poetry build -f wheel \
    && /app/bin/pip install --no-deps --no-cache-dir dist/*.whl


FROM base AS app
RUN mkdir /app /config && adduser -S app
WORKDIR /config

# COPY --chown=app:app alembic.ini /app/
COPY --chown=app:app interviews.example.yml /config/interviews.yml
COPY --from=build /app/ /app/

ENV PATH="/app/bin:$PATH"
VOLUME [ "/config" ]
EXPOSE 8000
USER app
ENTRYPOINT [ "oes-interview-service" ]
CMD [ "-H", "0.0.0.0" ]
