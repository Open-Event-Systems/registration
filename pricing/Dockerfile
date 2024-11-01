FROM golang:1.22.4-alpine3.20 AS build
WORKDIR /build
COPY go.mod go.sum pricing.go ./
RUN go mod download
COPY internal/ internal/
COPY cmd/ cmd/
RUN go build ./cmd/pricing


FROM alpine:3.20.0
RUN apk add curl python3
RUN adduser -D app \
    && mkdir -p /config/scripts
COPY scripts/healthcheck.sh /
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
