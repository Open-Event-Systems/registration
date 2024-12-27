FROM python:3.12.8-alpine3.21 AS base


FROM base AS build-base
WORKDIR /build
RUN apk add git \
    && pip install --no-cache-dir poetry poetry-plugin-export


FROM build-base AS build
RUN python -m venv /app \
    && /app/bin/pip install --no-cache-dir setuptools
COPY pyproject.toml poetry.lock poetry.toml ./

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
RUN mkdir /app /config && adduser -D app
WORKDIR /app

COPY scripts/healthcheck.py /
RUN chmod u=rw,g=r,o=r /healthcheck.py
# COPY --chown=app:app scripts/docker-entrypoint.sh /
# COPY --chown=app:app alembic/ /app/alembic/
# COPY --chown=app:app alembic.ini /app/
COPY --chown=app:app events.example.yml /config/events.yml
COPY --from=build /app/ /app/

ENV PATH="/app/bin:$PATH"
ENV CONFIG_FILE=/config/events.yml
VOLUME [ "/config" ]
EXPOSE 8000
USER app
# ENTRYPOINT [ "/docker-entrypoint.sh" ]
ENTRYPOINT [ "oes-web-service" ]
HEALTHCHECK --start-interval=10s --start-period=5m --retries=1 CMD [ "/app/bin/python", "/healthcheck.py" ]
CMD [ "-H", "0.0.0.0" ]
