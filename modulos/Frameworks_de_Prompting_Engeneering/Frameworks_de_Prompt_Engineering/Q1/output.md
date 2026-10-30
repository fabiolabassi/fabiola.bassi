# Output — Questão 01

## Resposta gerada

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

# Copia o ambiente virtual do builder, sem depender de diretórios do root
COPY --from=builder /opt/venv /opt/venv

# Cria usuário não root para rodar a aplicação
RUN useradd -m -u 1000 appuser

# Copia o código da aplicação
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser lib ./lib

USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]
```