# Checkpoint 02 - Execução e Resultados

## Prompt Parametrizável
Ver arquivo: `prompt-nota-triagem.md`

## Parâmetros
- `{{alerta_cru}}`: Alerta bruto do sistema

## Execução contra os 3 alertas crus

### Teste 1: Autoscaler hit max replicas

**Entrada**:
```
2026-05-12 14:02:09 UTC [Sentinel] autoscaler hit max replicas (60/60) on sentinel-api,
queue depth on Relay growing 2k/min, CPU avg 88%, tenant stark-industries
sending 4x baseline volume after onboarding new region
```

**Modelo usado**: GPT-4o-mini (OpenAI)
**Justificativa**: Tarefa de transformação de texto com formato estruturado. GPT-4o-mini é muito mais barato (~$0.15/1M input tokens) que modelos maiores e tem excelente desempenho em seguir formatos exatos. Alta latência não é crítica aqui. Privacidade: nome do tenant "stark-industries" é fictício no contexto do exercício, mas em produção seria dado sensível - seria necessário sanitizar (substituir por tenant-id genérico).

**Output esperado**:

ALERTA: Sentinel - autoscaler atingiu máximo de replicas (60/60) com CPU 88%
IMPACTO: tenant stark-industries pode ter latência degradada; Relay com fila crescendo 2k/min
HIPÓTESE INICIAL: onboarding de nova região do tenant stark-industries gerou pico de 4x volume
AÇÃO IMEDIATA: aumentar max replicas do autoscaler do sentinel-api temporariamente
ESCALAR PARA: @sentinel-core se fila do Relay não estabilizar em 10min

---

### Teste 2: Relay ingest reject rate

**Entrada**:
```
2026-05-13 03:11:00 UTC [Relay] ingest reject rate 6% for 8min, tenant wakanda-systems,
buffer saturated after deploy 02:55
```

**Modelo usado**: GPT-4o-mini (OpenAI)

**Output esperado**:

ALERTA: Relay - taxa de rejeição de ingestão 6% por 8min
IMPACTO: tenant wakanda-systems com perda de telemetry; buffer saturado
HIPÓTESE INICIAL: deploy do Relay às 02:55 reduziu capacidade do buffer
AÇÃO IMEDIATA: rollback do deploy do Relay
ESCALAR PARA: @relay-core se rejeição não cair em 5min

---

### Teste 3: Forge consumer lag

**Entrada**:
```
2026-05-13 11:40:22 UTC [Forge] consumer lag 9min and climbing, batch forge-batch-ingest
delayed after previous job failure, downstream Sentinel starting to lag
```

**Modelo usado**: GPT-4o-mini (OpenAI)

**Output esperado**:

ALERTA: Forge - consumer lag 9min e crescendo
IMPACTO: downstream Sentinel começando a ter lag; batch forge-batch-ingest atrasado
HIPÓTESE INICIAL: falha no job anterior do forge-batch-ingest gerou acúmulo
AÇÃO IMEDIATA: investigar causa da falha no job anterior e reprocessar batch
ESCALAR PARA: @data-platform se lag não estabilizar em 15min

---

## Curadoria

### Técnica/Framework escolhido
- **Few-Shot Learning**: Usei os 3 exemplos de saída fornecidos no enunciado como demonstração do padrão. Isso é mais efetivo que descrever o formato em texto porque o modelo aprende o tom, nível de detalhe e estrutura exata por exemplo.
- **Role Prompting**: Defini o modelo como "engenheiro de plantão na Aegis" para alinhar o contexto
- **Constraint Specification**: Dei instruções explícitas sobre concisão (no máximo 8 linhas) e formato do @handle

### Decisão de método justificada
Escolhi few-shot learning em vez de tentar descrever o padrão em texto por 3 motivos:
1. **Precisão de formato**: Os exemplos mostram exatamente o tom, nível de detalhe e estrutura que a Carol Danvers quer. Descrever isso em texto seria ambíguo.
2. **Eficiência**: 3 exemplos são suficientes para o modelo capturar o padrão. Não precisaria de muitos mais.
3. **Manutenibilidade**: Se o padrão mudar, basta atualizar os exemplos. Não precisa reescrever instruções.

Alternativas consideradas e descartadas:
- **Descrição textual do padrão**: Seria mais verboso e menos preciso que exemplos concretos
- **Chain of Thought**: Não é necessário - a transformação é direta, não requer raciocínio complexo
- **Zero-shot com instruções detalhadas**: Funcionaria, mas teria mais risco de variação no formato

### Refinamentos feitos
1. **Iteração 1**: Prompt inicial não especificava limite de linhas. Adicionei "no máximo 8 linhas" após perceber que outputs podiam ficar muito longos.
2. **Iteração 2**: O formato do @handle não estava explícito. Adicionei instrução "sempre use formato @handle seguido de condição".
3. **Iteração 3**: Melhorei os exemplos para mostrar diferentes níveis de impacto (12% dos tenants, todos os tenants, time interno).

### Sanitização de dados
Os alertas crus contêm:
- Nome de tenant: "stark-industries", "wakanda-systems" (em produção, seriam dados sensíveis)
- Timestamps específicos (não sensíveis)
- Nomes de sistema genéricos (Relay, Forge, Sentinel)
- **Decisão**: Em produção, seria necessário sanitizar nomes de tenant substituindo por IDs genéricos (tenant-123) antes de enviar para modelo externo. Neste exercício, são nomes fictícios do cenário, então pode usar como está.

### Avaliação final
O prompt satisfaz os requisitos:
- ✓ Parametrizável (recebe {{alerta_cru}})
- ✓ Produz nota com 5 campos obrigatórios
- ✓ Formato padronizado (ALERTA, IMPACTO, HIPÓTESE INICIAL, AÇÃO IMEDIATA, ESCALAR PARA)
- ✓ Contém @handle no campo de escalonamento
- ✓ Conciso (no máximo 8 linhas)
- ✓ Infere impacto, hipótese e ação a partir do alerta cru
