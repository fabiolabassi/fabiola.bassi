SELECT
    TO_CHAR(t.created_at AT TIME ZONE 'UTC', 'YYYY-MM') AS mes,
    t.category                                           AS categoria,
    COUNT(*)                                             AS qtd_transacoes,
    ROUND(SUM(t.amount_cents) / 100.0, 2)               AS volume_total_brl
FROM transactions t
WHERE t.status      = 'completed'
  AND t.created_at >= '2025-10-24 00:00:00+00'::TIMESTAMPTZ
  AND t.created_at <  '2026-04-25 00:00:00+00'::TIMESTAMPTZ
GROUP BY
    TO_CHAR(t.created_at AT TIME ZONE 'UTC', 'YYYY-MM'),
    t.category
ORDER BY
    mes       ASC,
    categoria ASC;