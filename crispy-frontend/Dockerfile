FROM node:18.6 AS build
WORKDIR /crispy-frontend
COPY . .
RUN npm install && npm run build
FROM nginx:1.23
COPY --from=build /crispy-frontend/public /usr/share/nginx/html
EXPOSE 80
