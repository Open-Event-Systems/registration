FROM golang:1.24.2-alpine3.21 AS build
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY internal/ internal/
COPY cmd/ cmd/
RUN go build ./cmd/pricing


FROM alpine:3.21.3
RUN apk add curl python3
RUN adduser -D app \
    && mkdir -p /config/scripts
COPY healthcheck.sh /
RUN chmod u=rwx,g=rx,o=rx /healthcheck.sh
COPY --from=build /build/pricing /usr/local/bin/
COPY --chown=app:app pricing.example.yml /config/pricing.yml
VOLUME [ "/config" ]
WORKDIR /config
USER app
ENV HEALTHCHECK_EVENT_ID=example-event
ENTRYPOINT [ "/usr/local/bin/pricing" ]
HEALTHCHECK --start-interval=5s --start-period=30s --retries=1 CMD [ "/healthcheck.sh" ]
CMD [ "/config/pricing.yml" ]
