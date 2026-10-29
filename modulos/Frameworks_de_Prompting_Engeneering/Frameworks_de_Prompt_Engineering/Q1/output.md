# Output — Questão 01

## Resposta gerada

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copia apenas os pacotes instalados do builder
COPY --from=builder /root/.local /root/.local

# Copia o código da aplicação
COPY app.py .
COPY lib ./lib

# Adiciona /root/.local/bin ao PATH para que os pacotes instalados sejam encontrados
ENV PATH=/root/.local/bin:$PATH

# Cria usuário não root para rodar a aplicação
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]
```