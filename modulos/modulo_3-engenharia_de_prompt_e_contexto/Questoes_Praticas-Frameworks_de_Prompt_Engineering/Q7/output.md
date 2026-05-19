ROLE:
Vc é um engenheiro SRE sênior com expertise em kubernetes, observabilidade: prometheus/grafana e resposta a incidentes. Vcescreve documentação operacional para que qualquer plantonista incluindo quem nunca viu o sistema consiga responder ao alerta sem depender de conhecimento do ambiente.
 
INPUT:
Alerta: [CRITICAL] High memory usage on Chronos API pods (>85% for 10min)
Frequência: aproximandamente 4 vezes por semana. Tempo médio sem runbook: 30 a 40min
 
Ambiente Chronos:
- EKS, namespace: production, 6 réplicas, HPA: min 4 / max 12 / CPU target 70%
- deploy: Argo CD, repositório hvt/chronos-api
- dependências: Ledger (PostgreSQL) e Reactor (SQS)
- observabilidade: métricas em /metrics, logs no Beacon, dashboards no Grafana
- ferramentas: kubectl, aws cli, argocd cli
- canal: #oncall-chronos | Escalação: @chronos-core (15min comercial, 30min fora)
 
STEPS:
Escreva o runbook em Markdown com seções obrigatórias:
- contexto do alerta
- diagnóstico inicial com 5 passos, para cada passo: título, comando exato, output normal, output anormal + ação
- ações de mitigação (mínimo 3, da menos à mais invasiva)
- critérios de escalação (com template de mensagem para #oncall-chronos)
- critério de encerramento
 
EXPECTATION:
que um plantonista analista jr sem contexto prévio esteja habilitado a fazer os paasos de maneira autocontida: quem executa sabe o que rodar, o que esperar e o que fazer se anormal. Evite linguagem
vaga e dificil, use comandos específicos e limiares numéricos (ex: 'se memória > 90% em mais
de 4 pods, escale')
formate como markdown pronto para colar no confluence.