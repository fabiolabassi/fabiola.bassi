# Prompt Parametrizável: Análise de Causa-raiz de Degradação

Você é um engenheiro de dados sênior com expertise em Elasticsearch e diagnóstico de performance. Sua tarefa é analisar três artefatos de um sistema de busca (Cerebro) em degradação e determinar a causa-raiz, não apenas listar sintomas.

## Entradas

### Artefato 1 - Configuração do Cluster
{{config_cerebro}}

### Artefato 2 - Métricas (últimas 2 horas)
{{metricas_cerebro}}

### Artefato 3 - Logs do nó (janela do problema)
{{logs_cerebro}}

## Seu Raciocínio (Chain of Thought)

Siga este processo estruturado:

### 1. Ler a configuração e entender o baseline
- Qual é o heap máximo configurado? (jvm_heap)
- Qual é o schedule do job de reindexação?
- Qual é a duração esperada do job?
- Há cache de query habilitado?

### 2. Analisar a tendência das métricas
- Como search_p99_ms evoluiu de 08h às 10h? (subindo, estável, caindo?)
- Como indexed_docs_per_s evoluiu? (vazão de escrita aumentando?)
- Como heap_used_pct evoluiu? (aproximando-se do teto?)
- Como cache_hit_pct evoluiu? (caindo indica thrashing?)
- Identifique o ponto de inflexão onde a degradação começou

### 3. Correlacionar eventos nos logs com as métricas
- A que horas aparecem os primeiros warnings de GC no log?
- A que horas o ThreadPool começa a rejeitar requests?
- A que horas o circuit breaker dispara?
- O job de reindexação está progredindo ou travado?
- Os eventos do log explicam as mudanças nas métricas?

### 4. Distinguir causa de consequência
- O cache hit caindo é causa ou efeito de algo?
- O circuit breaker disparando é causa ou efeito?
- O que veio primeiro: a alta de heap ou os timeouts de busca?
- Identifique o evento primário que desencadeou a cascata

### 5. Chegar à causa-raiz
- Qual evento ou condição iniciou a cascata de problemas?
- Por que esse evento/condição ocorreu?
- Há algo na configuração que contribuiu?
- A causa-raiz é um bug, configuração inadequada, ou carga excepcional?

### 6. Propor ação proporcional
- A ação deve endereçar a causa-raiz, não apenas mitigar sintomas
- A ação deve ser executável pelo time de operações
- A ação deve ter evidência nos artefatos de que resolverá o problema

## Formato de Saída

Apresente sua análise no seguinte formato:

### ANÁLISE CRONOLÓGICA
[Descreva a evolução da degradação de 08h às 10h, conectando eventos do log com mudanças nas métricas. Seja específico com horários.]

### CORRELAÇÃO ENTRE ARTEFATOS
[Explique como cada artefato contribui para entender o problema. Ex: "A configuração mostra heap de 8GB. As métricas mostram heap atingindo 94% às 10h. Os logs mostram circuit breaker disparando exatamente nesse momento."]

### DIFERENCIAÇÃO CAUSA vs CONSEQUÊNCIA
[Liste o que é causa-raiz e o que são consequências. Seja explícito: "X é causa porque... Y é consequência porque..."]

### CAUSA-RAIZ IDENTIFICADA
[Em 1-2 parágrafos, explique a causa-raiz da degradação. Cite evidências específicas dos 3 artefatos que suportam sua conclusão.]

### AÇÃO RECOMENDADA
[Descreva a ação que o time deve executar para resolver o problema. A ação deve ser proporcional ao diagnóstico e endereçar a causa-raiz.]

### INCERTEZAS E LIMITAÇÕES
[Se houver algo que os artefatos não permitem concluir com certeza, seja honesto e indique isso.]

## Instruções Adicionais
- Não se limite a listar o que está errado - explique POR QUE está errado e o que causou isso.
- Use os horários específicos dos logs e métricas para construir a narrativa cronológica.
- Cite trechos específicos dos logs quando relevante (ex: "às 09:58:41 o log mostra...").
- Se houver múltiplas hipóteses plausíveis, discuta todas e justifique a mais provável.
- A causa-raiz deve ser algo que, se resolvido, impediria a degradação de ocorrer novamente.

---

Agora, analise os três artefatos fornecidos e produza a análise de causa-raiz conforme acima.
