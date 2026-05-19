TASK:
Produza um relatório executivo de oportunidades de redução de custos AWS para a CEO
Goldie Wilson, com base no breakdown de custos mensais abaixo. O relatório precisa
trazer as oportunidades priorizadas por impacto financeiro, com percentual sobre a
conta total, esforço de implementação (Baixo/Médio/Alto) e riscos/pré-requisitos.
 
ACTION:
Analise o CSV, calcule a conta total, identifique os maiores desperdícios e construa
o relatório nesta estrutura:
- Sumário executivo (2-3 parágrafos): conta atual, meta de 15%, gap em dólares
- Tabela de oportunidades (ordenada por economia estimada descendente):
| Oportunidade | Serviço(s) | Economia Est. (USD/mês) | % da Conta | Esforço | Riscos |
- Roadmap de 3 ondas (Onda 1: ≤30 dias; Onda 2: 31-90 dias; Onda 3: >90 dias)
- Conclusão: se a meta de 15% é atingível
 
CSV:
servico,categoria,custo_mensal_usd,uso_medio_pct,observacao
EC2 reservada,compute,4200,72,contrato de 1 ano
EC2 on-demand,compute,8200,45,workloads variaveis
EKS,compute,6700,58,3 clusters
RDS PostgreSQL,databases,8200,62,multi-AZ
ElastiCache Redis,databases,2100,40,cluster de producao
S3 Standard,storage,3100,,5 buckets principais
EBS gp3,storage,1600,68,volumes de producao
CloudWatch Logs,observability,2800,,retencao de 90 dias
CloudWatch Metrics,observability,900,,
Data Transfer Out,network,1900,,trafego entre regioes
NAT Gateway,network,1200,,3 gateways ativos
Lambda,compute,900,30,~12M invocacoes/mes
 
GOAL:
O relatório deve habilitar Goldie a decidir quais iniciativas autorizar no próximo
trimestre para atingir 15% de redução (~USD 6.000/mês sobre conta de ~USD 41.800/mês),
sem degradação de SLA. Priorize alto impacto e baixo risco. Deixe claro explicito os tradeoffs