FROM golang:1.22.5-alpine3.20 AS build
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY cmd/ cmd/
COPY internal/ internal/
RUN go build ./cmd/worker

FROM scratch
COPY --from=build /etc/ssl /etc/ssl
COPY --from=build --chown=1000:1000 /build/worker /worker
COPY --chown=1000:1000 config.example.yml /config/sheets.yml
ENV PATH="/"
USER 1000:1000
VOLUME [ "/config" ]
WORKDIR /config
ENTRYPOINT [ "/worker" ]
CMD [ "/config/sheets.yml" ]
