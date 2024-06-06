FROM golang:1.22.4-alpine3.20 AS build
WORKDIR /build
COPY go.mod go.sum pricing.go ./
RUN go mod download
COPY internal/ internal/
COPY cmd/ cmd/
RUN go build ./cmd/pricing


FROM alpine:3.20.0
RUN adduser -D app \
    && mkdir -p /config/scripts
COPY --from=build /build/pricing /usr/local/bin/
COPY --chown=app:app pricing.example.yml /config/pricing.yml
VOLUME [ "/config" ]
WORKDIR /config
USER app
ENTRYPOINT [ "/usr/local/bin/pricing" ]
CMD [ "/config/pricing.yml" ]
