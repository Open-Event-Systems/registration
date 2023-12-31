FROM node:20.1.0-alpine3.17 AS node
WORKDIR /build
COPY package.json package-lock.json ./
COPY interview/lib/package.json interview/lib/
COPY interview/components/package.json interview/components/
COPY badge/lib/package.json badge/lib/
COPY registration/package.json registration/
RUN npm ci

COPY tsconfig.json ./
COPY configs/ configs/
COPY interview/lib/ interview/lib/
COPY interview/components/ interview/components/
COPY badge/lib/ badge/lib/

RUN npm run build

COPY registration/ registration/
COPY registration/config.example.ts config.ts
COPY registration/theme.example.ts theme.ts
RUN npm run -w registration build


FROM nginx:1.24.0-alpine3.17-slim AS nginx
COPY --chown=root:nginx registration/extra/nginx.conf /etc/nginx/nginx.conf
RUN chmod u=rw,g=r,o= /etc/nginx/nginx.conf \
    && mkdir /var/run/nginx \
    && chown nginx:nginx /var/run/nginx /var/cache/nginx
COPY --from=node /build/registration/dist/ /usr/share/nginx/html/
RUN chmod -R u=rwX,g=rX,o=rX /usr/share/nginx/html
USER nginx
EXPOSE 9000
