CONTEXT:
vc é o engenheiro de plantão. Esta acontecendo um incidente crítico durante um pico de tráfego. O CTO Doc Brown precisa de um postmortem técnico em 20 minutos para decidir entre:

Opção:
(A) rollback do deploy v2.48.0 ou 
(B) scaling emergencial (limits rds + pool conexões).
 
[1] CHANGELOG v2.47.0 -> v2.48.0 (ontem as 18:42 UTC):
- adicionado endpoint post /v2/transactions/batch
- refatorado cliente do ledger (pool movido para nova biblioteca interna)
- bump psycopg 3.1.18 -> 3.2.0
- reduzido timeout do ledger de 5s para 2s
 
[2] MÉTRICAS BEACON (últimos 30 min):
13:30 UTC — p99=420ms, req=1200/s, erros=0.2%
13:45 UTC — p99=510ms, req=1450/s, erros=0.3%
14:00 UTC — p99=780ms, req=1780/s, erros=0.8%
14:10 UTC — p99=2400ms, req=2100/s, erros=4.5%
14:15 UTC — p99=5200ms, req=2400/s, erros=8.2%
14:20 UTC — p99=8100ms, req=2650/s, erros=11.7%
 
[3] log pod chronos-api-79c4d8b9-xk2jp (14:19-14:20 UTC):
[ERROR] connection pool exhausted (max=20, active=20, waiting=147)
[WARN]  query timeout after 2000ms
[ERROR] POST /v2/transactions/batch failed: context deadline exceeded
[WARN]  circuit-breaker ledger-client OPEN (threshold 50%, current 87%)
[ERROR] failed to publish message: chronos-api upstream error
 
[4] REACTOR, fila chronos-transactions:
50.127 mensagens acumuladas, crescendo ~800/min. consumer lag: 18 min.
 
[5] CLUSTER:
Chronos: 12/12 pods (HPA no máximo). CPU: 62%. memória: 71%.
conexões rds ativas: 240/250.
 
ACTION:
analise os 5 artefatos e produza o postmortem técnico:
- correlacione a degradação com as mudanças do deploy v2.48.0
- identifique a causa raiz provável com evidências dos artefatos
- mapeie a cadeia de falha
- avalie as duas opções de remediação e recomende uma, com justificativa
- liste de 3 a 5 ações preventivas
 
RESULT:
estruture o postmortem:
## resumo rxecutivo (3 linhas máximo)
## linha do tempo (tabela: horário | evento | evidência)
## causa raiz
## cadeia de falha
## análise das opções (tabela: Opção | Prós | Contras | Tempo estimado)
## recomendação imediata (1 parágrafo decisivo)
## ações preventivas (lista numerada com responsável)
 

EXAMPLE:
'O deploy v2.48.0 introduziu [mudança X], que sob carga [condição Y] resultou
em [efeito Z], evidenciado por [artefato N]. Isso descarta [alternativa]
porque [razão].'

seja conclusivo pois é necessário de uma recomendação e não de hipóteses