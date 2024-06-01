FROM alpine:3.20.0 AS base


FROM base AS build
WORKDIR /build
RUN apk add go
COPY go.mod go.sum print.go /build/
COPY cmd /build/cmd
COPY pkg /build/pkg
RUN go build ./cmd/print-to-pdf
RUN go build ./cmd/print-api


FROM base AS target
RUN apk add chromium chromium-swiftshader
RUN adduser -D app
RUN mkdir /config /data && chown app:app /data
COPY --chown=app:app print.example.yml /config/print.yml
COPY --chown=app:app template.example.html /config/template.html
COPY --from=build /build/print-to-pdf /build/print-api /usr/local/bin/
USER app
VOLUME [ "/config" ]
VOLUME [ "/data" ]
EXPOSE 8000
WORKDIR /home/app
CMD [ "print-api", "/config/print.yml" ]
