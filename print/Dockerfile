FROM alpine:3.21.0 AS base


FROM base AS build
WORKDIR /build
RUN apk add go
COPY go.mod go.sum /build/
COPY cmd /build/cmd
COPY internal /build/internal
RUN go build ./cmd/print-api
RUN go build ./cmd/print-worker


FROM base AS target
RUN apk add font-noto-all font-noto-cjk font-noto-cjk-extra
RUN apk add curl chromium chromium-swiftshader cups-client
RUN adduser -D app
RUN mkdir /home/app/.fonts \
    && curl -L -o /home/app/.fonts/BabelStoneHan.ttf https://www.babelstone.co.uk/Fonts/Download/BabelStoneHan.ttf \
    && chown -R app:app /home/app/.fonts \
    && su app -c "fc-cache -fv"
RUN mkdir /config /data && chown app:app /data
COPY --chown=app:app print.example.yml /config/print.yml
COPY --chown=app:app template.example.html /config/template.html
COPY --from=build /build/print-api /usr/local/bin/
COPY --from=build /build/print-worker /usr/local/bin/
USER app
VOLUME [ "/config" ]
VOLUME [ "/data" ]
EXPOSE 8000
WORKDIR /config
CMD [ "print-api", "/config/print.yml" ]
