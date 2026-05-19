## Resumo Executivo
O deploy v2.48.0 introduziu pool de conexões max=20 por pod e timeout 2s,
causando esgotamento sob carga a partir das 14:00 UTC. Com circuit breaker
aberto (87%) e HPA saturado (12/12), rollback imediato é a ação correta.
 
## Linha do Tempo
| Horário UTC       | Evento                                        | Evidência              |
|-------------------|-----------------------------------------------|------------------------|
| 2026-04-23 18:42  | Deploy v2.48.0 — pool refatorado, timeout 2s  | Changelog              |
| 2026-04-24 13:30  | Tráfego normal; p99=420ms, erros 0.2%         | Métricas Beacon        |
| 14:00             | Degradação inicia: p99=780ms, erros 0.8%      | Métricas Beacon        |
| 14:10             | Aceleração crítica: p99=2400ms, erros 4.5%    | Métricas Beacon        |
| 14:19             | Pool esgotado (active=20, waiting=147)        | Log do pod             |
| 14:19             | Timeouts 2000ms; circuit breaker OPEN 87%     | Log do pod             |
| 14:20             | p99=8100ms, erros 11.7%, RDS 240/250 conex.   | Métricas + cluster     |
 
## Causa Raiz
O deploy v2.48.0 introduziu um pool de conexões max=20 por pod, que sob
crescimento de tráfego para ~1.780 req/s (14:00 UTC) resultou em esgotamento
total (waiting=147 às 14:19), evidenciado pelo log 'connection pool exhausted'.
O timeout reduzido de 5s para 2s acelerou a abertura do circuit breaker.
Isso descarta problema no RDS em si porque as 240/250 conexões estão ATIVAS
— o banco responde, mas o pool do cliente não tem slots disponíveis.
 
## Cadeia de Falha
1. Deploy v2.48.0 → pool max=20/pod (subdimensionado para 12 pods x 20 = 240 conex.)
2. Crescimento de tráfego → pool esgota → requisições enfileiradas (waiting=147)
3. Timeout 2s → queries lentas → context deadline exceeded
4. Circuit breaker OPEN (87%) → 87% das requisições ao Ledger falham
5. POST /batch falha em cascata → erros 5xx 11.7%
6. Reactor não publica → fila acumula 50k+ mensagens
7. HPA no máximo → scaling não resolve (problema é no pool, não em CPU/memória)
 
## Análise das Opções
| Opção                    | Prós                             | Contras                          | Tempo    |
|--------------------------|----------------------------------|----------------------------------|----------|
| A) Rollback v2.48.0      | Resolve causa raiz; baixo risco  | Perde features; fila reprocessar | 5-10 min |
| B) Scaling RDS + pool    | Não reverte features             | RDS resize ~15min downtime       | 20-40min |
 
## Recomendação Imediata
Execute o rollback para v2.47.0 via Argo CD agora.
argocd app set chronos-api --revision v2.47.0 && argocd app sync chronos-api
O scaling emergencial do RDS não resolve o pool=20 e adiciona risco de downtime
na instância de banco. O rollback restaura o estado estável em 5-10 min.
 
## Ações Preventivas
1. [George McFly] Documentar fórmula: max_replicas × pool_size ≤ RDS_max × 0.8
2. [George McFly] Adicionar teste de carga no CI/CD para mudanças no cliente Ledger
3. [Lorraine Baines] Criar alerta Beacon: 'Ledger pool utilization > 70%'
4. [Doc Brown] Exigir revisão de impacto em conexões em PRs que alterem libs de BD
5. [SRE] Configurar rate limiting em POST /v2/transactions/batch