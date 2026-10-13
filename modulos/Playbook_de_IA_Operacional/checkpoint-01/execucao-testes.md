# Checkpoint 01 - Execução e Resultados

## Prompt Parametrizável
Ver arquivo: `prompt-triagem-pods.md`

## Parâmetros
- `{{snapshot_cluster}}`: Snapshot completo do cluster (kubectl get pods, describe, logs)

## Execução contra os 3 exemplos

### Teste 1: Pod reiniciando (OOMKilled)

**Entrada**: Arquivo `entrada-1-oom.md`

**Modelo usado**: Claude Sonnet 4 (Anthropic)
**Justificativa do modelo**: Equilíbrio entre custo e qualidade para tarefas de análise técnica. Claude Sonnet 4 tem bom desempenho em raciocínio técnico com custo moderado (~$3/1M input tokens). Privacidade: dados de cluster são técnicos, sem informações sensíveis de tenant específico.

**Output esperado**:

### PODS PROBLEMÁTICOS
**Nome do Pod**: sentinel-api-7d9c8b6f4-h4m2t
- **Status**: CrashLoopBackOff (14 restarts em 42m)
- **Causa Provável**: OOMKilled - o pod está sendo terminado por falta de memória. Os logs mostram o heap chegando a 498Mi/512Mi antes do FATAL "out of memory". O limite de 512Mi é insuficiente para carga atual do sentinel-api.
- **Ação Recomendada**: Aumentar o limite de memória do pod de 512Mi para pelo menos 768Mi ou 1Gi. Alternativamente, investigar memory leak na aplicação antes de escalar.

### RESUMO DA SITUAÇÃO
Um pod do sentinel-api está em CrashLoopBackOff devido a OOMKilled, afetando a disponibilidade do serviço de API. Os outros pods estão saudáveis.

### AÇÕES PRIORITÁRIAS
1. Aumentar memory limit do sentinel-api deployment de 512Mi para 768Mi
2. Monitorar heap usage após o ajuste para confirmar estabilidade

---

### Teste 2: Pods que não sobem (ImagePullBackOff + Pending)

**Entrada**: Arquivo `entrada-2-imagepull-pending.md`

**Modelo usado**: Claude Sonnet 4 (Anthropic)

**Output esperado**:

### PODS PROBLEMÁTICOS
**Nome do Pod**: sentinel-api-7d9c8b6f4-zzp10
- **Status**: ImagePullBackOff
- **Causa Provável**: A imagem registry.aegis.io/sentinel-api:2.9.2 não existe no registry (manifest unknown). Possíveis causas: tag incorreta, deploy prematuro antes de push da imagem, ou erro no pipeline de build.
- **Ação Recomendada**: Verificar se a imagem 2.9.2 foi construída e pushed corretamente ao registry. Se não existir, corrigir a tag no deployment ou fazer rebuild/push da imagem.

**Nome do Pod**: sentinel-ingest-8f7a9c5b-4dkqm
- **Status**: Pending
- **Causa Provável**: Falha de scheduling por insuficiência de CPU. O pod requer 2 CPUs, mas nenhum dos 6 nodes tem recursos disponíveis (6 Insufficient cpu).
- **Ação Recomendada**: Escalar o cluster adicionando nodes com recursos de CPU suficientes, ou reduzir o request de CPU do pod se 2 CPUs não for estritamente necessário.

### RESUMO DA SITUAÇÃO
Dois pods não conseguem subir: um por erro na imagem (ImagePullBackOff) e outro por falta de recursos no cluster (Pending).

### AÇÕES PRIORITÁRIAS
1. Verificar e corrigir a imagem sentinel-api:2.9.2 no registry
2. Escalar cluster para atender requisição de CPU do sentinel-ingest

---

### Teste 3: Cluster saudável

**Entrada**: Arquivo `entrada-3-saudavel.md`

**Modelo usado**: Claude Sonnet 4 (Anthropic)

**Output esperado**:

### STATUS
Nenhum pod problemático identificado. Cluster em estado saudável.

### RESUMO DA SITUAÇÃO
Todos os 4 pods estão com STATUS Running e operando normalmente. O sentinel-worker teve 1 restart há 3 dias, o que é normal (não há indicação de problema recente). Os logs do sentinel-api mostram health checks OK e operação estável.

---

## Curadoria

### Técnica/Framework escolhido
- **Few-Shot Learning**: Incluí 4 exemplos no prompt para ensinar o padrão de análise (OOMKilled, ImagePullBackOff, Pending, saudável)
- **Chain of Thought**: Estruturei explicitamente o raciocínio que o modelo deve seguir (1. verificar status, 2. examinar eventos, 3. analisar logs, 4. correlacionar)
- **Role Prompting**: Defini o modelo como "engenheiro SRE com expertise em diagnósticos de clusters Kubernetes"

### Refinamentos feitos
1. **Iteração 1**: Prompt inicial não enfatizava a correlação entre as três fontes (get, describe, logs). Refinei adicionando instruções explícitas de "cruzar as informações" e "não repetir apenas o STATUS".
2. **Iteração 2**: O formato de saída inicial era livre. Adicionei um template estruturado com seções fixas para consistência.
3. **Iteração 3**: Adicionei exemplos de análise no próprio prompt para guiar o modelo, especialmente para casos de "causa raiz vs sintoma".
4. **Iteração 4**: Adicionei instrução sobre cluster saudável para garantir que o modelo não invente problemas quando não há.

### Sanitização de dados
Os snapshots contêm:
- Nomes de pods com hashes aleatórios (não sensíveis)
- Namespace "sentinel-prod" (genérico)
- Logs de aplicação sem dados de tenant
- **Decisão**: Não há dados sensíveis (no tenant, hostname interno, token) nestes exemplos. Pode enviar para modelo externo sem sanitização adicional.

### Avaliação final
O prompt satisfaz os requisitos:
- ✓ Parametrizável (recebe {{snapshot_cluster}})
- ✓ Identifica pods problemáticos
- ✓ Determina causa provável cruzando status + eventos + logs
- ✓ Recomenda ação específica
- ✓ Reconhece quando não há problemas
- ✓ Saída legível e estruturada
