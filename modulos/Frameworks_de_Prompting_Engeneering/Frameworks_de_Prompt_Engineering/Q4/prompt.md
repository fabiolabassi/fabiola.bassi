TASK:
Escreva uma query SQL para PostgreSQL que produza o relatório mensal de transações dos
últimos 6 meses corridos a partir de 2026-04-24, agrupado por mês e por categoria,
trazendo quantidade de transações e volume total em reais.
 
ACTION:
Use as tabelas abaixo. Regras de negócio:
- Filtrar apenas status = 'completed'
- Recorte: created_at entre 2025-10-24 e 2026-04-24
- Converter amount_cents para reais: amount_cents / 100.0, 2 casas decimais
- Agrupar por: mês no formato YYYY-MM (TO_CHAR) e categoria
- Colunas de saída: mes, categoria, qtd_transacoes, volume_total_brl
- Ordenação: mês crescente, categoria crescente
 
ddl:
CREATE TABLE transactions (
  id              BIGSERIAL PRIMARY KEY,
  customer_id     BIGINT NOT NULL REFERENCES customers(id),
  category        VARCHAR(32) NOT NULL,
  amount_cents    BIGINT NOT NULL,
  status          VARCHAR(16) NOT NULL,
  payment_method  VARCHAR(16),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_category ON transactions(category);
 
GOAL:
Query executável diretamente no Ledger, usando os índices existentes, sem CTEs
desnecessárias. Retornar exatamente as colunas esperadas por Jennifer para montar
os gráficos. Forneça apenas o SQL, sem explicações ou markdown.