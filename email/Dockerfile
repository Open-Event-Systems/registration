FROM golang:1.23.4-alpine3.21 AS build
WORKDIR /build
COPY go.mod go.sum email.go ./
RUN go mod download
COPY config/ config/
COPY template/ template/
COPY email/ email/
COPY senders/ senders/
COPY cmd/ cmd/
RUN go build ./cmd/send
RUN go build ./cmd/worker


FROM scratch
COPY --from=build /etc/ssl/ /etc/ssl/
COPY --from=build --chown=1000:1000 /build/send /send
COPY --from=build --chown=1000:1000 /build/worker /worker
COPY --chown=1000:1000 email.example.yml /config/email.yml
COPY --chown=1000:1000 templates/ /config/templates/
ENV PATH="/"
USER 1000:1000
VOLUME [ "/config" ]
WORKDIR /config
ENTRYPOINT [ "/worker" ]
CMD [ "/config/email.yml" ]
