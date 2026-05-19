FROM node:20-alpine

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

COPY frontend/package.json ./
RUN npm install

COPY frontend ./

EXPOSE 3000
CMD ["npm", "run", "dev"]
