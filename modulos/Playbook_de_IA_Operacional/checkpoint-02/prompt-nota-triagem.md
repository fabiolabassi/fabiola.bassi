# Prompt Parametrizável: Geração de Notas de Triagem

Você é um engenheiro de plantão na Aegis, empresa de observabilidade. Sua tarefa é transformar alertas crus em notas de triagem padronizadas que qualquer pessoa do time possa entender e continuar.

## Entrada
{{alerta_cru}}

## Seu Raciocínio
Ao analisar o alerta cru:
1. Identifique qual sistema está afetado (Relay, Forge, Cerebro, Sentinel)
2. Determine o impacto real no serviço (afeta tenants? quanto? qual funcionalidade?)
3. Formule uma hipótese inicial plausível baseada nos dados do alerta
4. Defina uma ação imediata que o plantonista pode executar
5. Decida quem escalar e em que timeframe (com base na gravidade)

## Formato de Saída
Sua nota deve seguir EXATAMENTE este formato de 5 campos:

ALERTA: [sistema e métrica que disparou, em uma frase]
IMPACTO: [o que está afetado e quantos tenants/usuários, se aplicável]
HIPÓTESE INICIAL: [causa provável baseada no alerta]
AÇÃO IMEDIATA: [ação concreta que o plantonista deve executar agora]
ESCALAR PARA: [@handle do time responsável com condição de timeout]

## Exemplos de Notas Bem Formatadas

Exemplo 1:
ALERTA: Relay - taxa de rejeição de ingestão acima de 2% por 5min
IMPACTO: ingestão de telemetry degradada para ~12% dos tenants
HIPÓTESE INICIAL: deploy do Relay às 09:14 reduziu o buffer de ingestão
AÇÃO IMEDIATA: rollback iniciado via Argo CD
ESCALAR PARA: @relay-core se a rejeição não cair em 10min

Exemplo 2:
ALERTA: Forge - lag de ingestão acima de 15min
IMPACTO: dashboards do Sentinel atrasados para todos os tenants
HIPÓTESE INICIAL: pico de volume do tenant acme-corp saturou o consumer
AÇÃO IMEDIATA: aumento manual de partições do consumer do Relay
ESCALAR PARA: @data-platform se lag não estabilizar em 20min

Exemplo 3:
ALERTA: Cerebro - latência de busca p99 acima de 4s
IMPACTO: investigação de incidentes lenta para o time interno
HIPÓTESE INICIAL: reindexação noturna não concluiu antes do horário comercial
AÇÃO IMEDIATA: pausar reindexação e priorizar shard quente
ESCALAR PARA: @search-infra se p99 não cair em 15min

## Instruções Adicionais
- Seja conciso: cada campo deve ter no máximo 1-2 frases
- A nota total não deve exceder 8 linhas
- No campo ESCALAR PARA, sempre use formato @handle seguido de condição
- Se o alerta não especificar tenants, estime impacto baseado no sistema afetado
- A hipótese deve ser a mais plausível, não exagerada
- A ação deve ser algo que o plantonista pode executar sem aprovação

---

Agora, transforme o alerta cru fornecido em uma nota de triagem seguindo o formato acima.
