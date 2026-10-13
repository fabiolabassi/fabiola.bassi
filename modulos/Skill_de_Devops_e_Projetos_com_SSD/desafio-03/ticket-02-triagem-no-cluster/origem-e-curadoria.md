# Origem da Skill e Curadoria - Ticket 02

## Origem da Skill

### Fluxo de Criação
A skill nasceu do seguinte fluxo:

1. **Análise dos 3 chamados reais**: Li os manifests dos 3 chamados fornecidos (nyx-prod, orion-stg, nyx-stg) para entender os diferentes tipos de problemas que podem ocorrer.

2. **Identificação de padrões de triagem**: Analisei cada chamado para identificar:
   - Como o problema se manifesta (sintoma)
   - Em que ordem as camadas devem ser verificadas
   - Quando cruzar fontes vs aprofundar numa só
   - Quando parar (causa identificada)

3. **Definição do método**: Defini um método estruturado de triagem:
   - Por onde começar (sintoma → recurso mais próximo da superfície)
   - Ordem das camadas (Pod → Eventos → Logs → Deployment → Service → Endpoints)
   - Quando cruzar (Service sem endpoint + Pods saudáveis)
   - Quando parar (causa identificada)

4. **Verificação dos 3 chamados**: Apliquei o método aos 3 chamados para validar:
   - Chamado 1 (nyx-prod): OOMKilled → Pod → Events → Logs → Resources → Identificado
   - Chamado 2 (orion-stg): Pods não substituídos → Deployment → Pods → Imagem → Identificado
   - Chamado 3 (nyx-stg): 503 → Deployment → Pods → Service → Endpoints → Seletor vs Rótulos → Identificado

5. **Teste de roteamento**: Testei 10 frases para ver qual skill dispara (padrão de manifests vs triagem) e ajustei as descrições das skills para evitar disparos incorretos.

6. **Comparação com e sem skill**: Executei 2 casos com skill e sem skill para medir qualidade, tempo e custo.

### Ferramenta Usada
- **Claude (Anthropic)**: Para escrita da skill e execução dos chamados
- **mcp-server-kubernetes**: Ferramenta mencionada no exercício para acesso ao cluster (simulado via kubectl)
- **kubectl**: Comandos específicos para triagem

## Curadoria

### O que o Método Fixou vs O que Ficou a Critério do Agente

#### Fixo pelo Método
1. **Por onde começar**: Sempre começa pelo recurso mais próximo da superfície do sintoma
2. **Ordem das camadas**: Ordem fixa (Pod → Events → Logs → Deployment → Service → Endpoints)
3. **Quando cruzar fontes**: Quando o sintoma sugere correlação (ex: Service sem endpoint + Pods saudáveis)
4. **Quando parar**: Sempre para quando causa é identificada ou próximo passo claro é definido
5. **Limite absoluto**: Nenhuma correção é aplicada, mesmo que o agente tenha permissão

#### A Critério do Agente
1. **Quais comandos específicos usar**: O agente decide quais comandos kubectl usar (get, describe, logs, rollout history)
2. **Quanto detalhar**: O agente decide o nível de detalhe dos logs e eventos (show recentes vs todos)
3. **Como interpretar**: O agente interpreta os dados e forma a conclusão da causa

### Como Garanti que a Skill Não Escreve no Cluster

A skill garante modo não destrutivo de 3 formas:

1. **Uso de mcp-server-kubernetes em modo não destrutivo**: A ferramenta mcp-server-kubernetes mencionada no exercício tem modo não destrutivo que só permite operações de leitura. A skill assume que esse modo está ativo.

2. **Limite absoluto documentado**: A skill tem seção explícita "Limite Absoluto" que diz: "A triagem SÓ LÊ o cluster. Nenhuma correção é aplicada, nem quando o agente tem permissão para isso. Se o agente tentar aplicar correção, a skill deve interromper."

3. **Verificação de permissões**: A skill pede explicitamente "NÃO permissões de escrita (apply, delete, scale, edit)" na seção de permissões. Isso garante que, mesmo que o agente tenha essas permissões no cluster, a skill não as usa.

**Adicionalmente**: Em todos os exemplos de execução, a skill termina com "Próximo Passo (Sem Aplicar Correção)", reforçando que a triagem é diagnóstico, não correção.

### Aprendizados Durante Execução

#### Chamado 1 (nyx-prod)
**O que funcionou**: O método de começar pelo Deployment e depois descer para Pods funcionou bem. A verificação de resources foi crítica para identificar o problema.

**O que poderia ser melhor**: O método poderia incluir verificação de ResourceQuota do namespace antes de verificar resources do container, para contextualizar melhor o "corte de custos".

#### Chamado 2 (orion-stg)
**O que funcionou**: Verificar rollout history foi decisivo para identificar que não houve rollout recente.

**O que poderia ser melhor**: O método poderia incluir verificação da imagem nos pods vs manifesto do Deployment para detectar drift de versão mais cedo.

#### Chamado 3 (nyx-stg)
**O que funcionou**: Verificar Endpoints foi o passo crítico. Sem isso, o problema não seria encontrado.

**O que poderia ser melhor**: O método poderia ser mais explícito sobre quando verificar Endpoints (só quando Service parece OK mas Pods não são alcançáveis).

### Ajustes Feitos na Skill Após Execução

#### Ajuste 1: Adicionar verificação de ResourceQuota
**O que mudou**: Adicione ao método: "Se houver suspeita de problema de recursos, verificar ResourceQuota do namespace antes de resources do container."

**Por quê**: O Chamado 1 menciona "corte de custos que mudou os limites de recurso do namespace inteiro". Verificar ResourceQuota ajudaria a confirmar isso.

#### Ajuste 2: Adicionar verificação de rollout history
**O que mudou**: Adicione ao método: "Se Deployment parece saudável mas há suspeita de problema de versão, verificar rollout history."

**Por quê**: O Chamado 2 não teve rollout recente mesmo após release anunciado. Verificar rollout history confirma isso.

#### Ajuste 3: Adicionar verificação de drift de imagem
**O que mudou**: Adicione ao método: "Se há suspeita de problema de versão, comparar imagem nos pods vs manifesto do Deployment."

**Por quê**: O Chamado 2 poderia ter sido identificado mais cedo comparando a imagem nos pods com o manifesto.

### Decisões de Curadoria

#### Por que o Método Começa pelo Deployment em Vez de Pods
**Decisão**: O método começa pelo Deployment quando o sintoma é genérico ("está fora do ar"), e pelo Pod quando o sintoma menciona um recurso específico ("o pod X não sobe").

**Alternativas consideradas**:
- Sempre começar pelos Pods: Seria consistente, mas menos eficiente para sintomas genéricos
- Sempre começar pelo Deployment: Seria menos preciso para sintomas específicos de Pod

**Justificativa**: Começar pelo recurso mais próximo da superfície do sintoma é mais eficiente. Se o sintoma menciona um Pod específico, não faz sentido começar pelo Deployment. Se o sintoma é genérico, o Deployment é o melhor ponto de partida.

#### Por que a Ordem das Camadas É Fixa
**Decisão**: A ordem (Pod → Events → Logs → Deployment → Service → Endpoints) é fixa, não adaptável.

**Alternativas consideradas**:
- Ordem adaptável: Deixar o agente decidir a ordem baseado no contexto
- Ordem aleatória: Sem ordem definida

**Justificativa**: Ordem fixa garante consistência e que nada seja esquecido. Ordem adaptável poderia deixar o agente pular partes importantes. Ordem fixa também é mais fácil de ensinar e seguir por humanos.

#### Por que Não Incluí Verificação de Metrics
**Decisão**: O método não inclui verificação de métricas (CPU, memória, latência).

**Alternativas consideradas**:
- Incluir verificação de métricas: Adicionar kubectl top ou metrics-server
- Não incluir métricas: Manter apenas objetos Kubernetes

**Justificativa**: O foco da skill é triagem de objetos Kubernetes (Pod, Deployment, Service), não performance de aplicação. Métricas adicionariam complexidade e muitas vezes não são necessárias para identificar a causa (ex: mismatch de seletor não aparece em métricas). Além disso, o exercício não menciona métricas nos chamados.

#### Por que a Skill Não Faz Correção Automática
**Decisão**: A skill é estritamente leitura, não faz correção automática.

**Alternativas consideradas**:
- Fazer correção automática para problemas simples (ex: aumentar memory limit)
- Fazer correção só com confirmação do usuário
- Manter apenas leitura

**Justificativa**: Correção automática é perigosa em produção - pode piorar o problema ou causar efeitos colaterais não previstos. O exercício exige "modo não destrutivo", o que reforça leitura apenas. Além disso, a triagem é diagnóstico, não correção - a decisão de corrigir cabe ao plantonista.
