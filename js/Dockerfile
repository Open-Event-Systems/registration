FROM node:20.1.0-alpine3.17 AS node
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY .babelrc.json webpack.config.cjs config.example.json ./
COPY resources/ resources/
COPY src/ src/
RUN npm run build


FROM nginx:1.24.0-alpine3.17-slim AS nginx
COPY --chown=root:nginx extra/nginx.conf /etc/nginx/nginx.conf
RUN chmod u=rw,g=r,o= /etc/nginx/nginx.conf \
    && mkdir /var/run/nginx \
    && chown nginx:nginx /var/run/nginx /var/cache/nginx
COPY --from=node /build/dist/ /usr/share/nginx/html/
USER nginx
EXPOSE 9000
