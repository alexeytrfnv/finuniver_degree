FROM nexus.sogaz.ru/node:24

WORKDIR /app
RUN npm config set registry http://nexus.sogaz.ru/npm

COPY package*.json ./

RUN npm install 

COPY . .

RUN npm run build

FROM nexus.sogaz.ru/nginx:1.28.2-alpine

COPY --from=0 /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]