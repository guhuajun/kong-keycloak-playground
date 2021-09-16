FROM node:alpine as BASE

WORKDIR /app/
ADD src/package.json .
RUN npm install

FROM node:alpine
WORKDIR /app/
COPY --from=BASE /app/ .
ADD src/ .
EXPOSE 8080

CMD ["npm", "run", "serve"]