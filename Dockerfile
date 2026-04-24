FROM python:3.11-alpine AS builder
WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-alpine
WORKDIR /app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /install /usr/local
COPY backend/user-service/ .

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8001

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8001"]