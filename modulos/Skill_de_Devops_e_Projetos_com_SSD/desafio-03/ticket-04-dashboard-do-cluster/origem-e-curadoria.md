# Origem e Curadoria - Ticket 04

## Origem do Projeto

### Fluxo de Criação
O projeto nasceu do seguinte fluxo:

1. **Leitura do PRD**: Li o PRD criado anteriormente para entender o problema (triagem repetitiva com comandos de terminal) e a solução (dashboard local).

2. **Escrita do TRD**: Escrevi o TRD documentando as decisões técnicas:
   - Linguagem e stack (Python + Streamlit)
   - Comunicação com API do Kubernetes (cliente oficial)
   - Como manter tela atualizada (refresh manual)
   - Fonte dos endpoints (EndpointSlice)
   - Recorte da primeira fatia (MVP)

3. **Criação de ADRs**: Criei dois ADRs:
   - ADR-001: Linguagem e stack
   - ADR-002: Comunicação com API do Kubernetes

4. **Ciclo do OpenSpec**: Criei proposta.md, tarefas.md e specs.md seguindo o ciclo do OpenSpec.

5. **Registro de skills**: Durante o desenvolvimento, as skills dos Tickets 01 e 02 estavam instaladas. Documentei o que aconteceu (registro-skills.md).

### Ferramenta Usada
- **Claude (Anthropic)**: Para escrita de PRD, TRD, ADRs, specs
- **Python 3.10+**: Linguagem de implementação (especificada, não implementada)
- **Streamlit**: Framework de UI (especificado, não implementado)

## Curadoria

### Onde a Spec Precisou Ser Corrigida Durante Implementação

**Nota**: Como o código não foi implementado (apenas spec), não houve correções durante implementação. No entanto, durante a escrita da spec, fiz alguns ajustes:

#### Ajuste 1: Adição de EndpointSlice
**O que estava na spec inicial**: Usar Endpoints para verificar se service tem endpoint.

**O que o agente sugeriu**: EndpointSlice está sendo descontinuado, usar EndpointSlice em vez de Endpoints.

**Correção**: Ajustei a spec para usar EndpointSlice internamente, mas mostrar "Endpoint" na UI para familiaridade do usuário.

#### Ajuste 2: Tratamento de Permissão Negada
**O que estava na spec inicial**: Se permissão negada, mostrar erro e parar.

**O que o agente sugeriu**: Se permissão negada para um recurso, mostrar erro mas continuar mostrando outros recursos.

**Correção**: Ajustei a spec para permitir que outros recursos continuem sendo mostrados mesmo se um recurso tiver permissão negada.

### O que o Agente Entendeu Diferente do que Eu Escrevi

#### Diferença 1: Leitura de Manifests vs Leitura da API
**O que eu escrevi**: O dashboard lê manifests do kubeconfig.

**O que o agente entendeu**: O dashboard lê objetos da API do Kubernetes usando o kubeconfig.

**Diferença**: "Ler manifests" implica ler arquivos YAML. "Ler objetos da API" implica fazer chamadas à API do Kubernetes.

**Decisão**: A interpretação do agente está correta. O dashboard lê o estado atual dos objetos da API, não arquivos de manifesto. Ajustei a spec para refletir isso.

#### Diferença 2: Refresh Automático vs Manual
**O que eu escrevi**: A tela se atualiza automaticamente.

**O que o agente sugeriu**: Refresh manual com botão é melhor para evitar carga no apiserver.

**Decisão**: A interpretação do agente está correta. Refresh manual é mais apropriado para ferramenta de triagem. Ajustei a spec para refresh manual.

### Decisões de Curadoria

#### Por que Python + Streamlit em Vez de Go + React
**Decisão**: Python 3.10+ com Streamlit em vez de Go com servidor HTTP + React

**Alternativas consideradas**:
- Go + React: Binário único, performance superior, mas curva de aprendizado mais íngreme para time de infraestrutura
- JavaScript (React/Next.js): Ecossistema maduro, mas curva de aprendizado para time de infraestrutura

**Justificativa**: Python é linguagem que time já conhece (usado em Ticket 03). Streamlit permite criar dashboards com pouco código. Time de infraestrutura pode manter facilmente.

#### Por que Cliente Oficial em Vez de kubectl Subprocesso
**Decisão**: Cliente oficial Python (kubernetes/python-client) em vez de kubectl como subprocesso

**Alternativas consideradas**:
- kubectl subprocesso: Usa kubectl que time já conhece, mas parsing de YAML é frágil
- HTTP direto: Máximo controle, mas complexidade alta

**Justificativa**: Cliente oficial abstrai autenticação, contexto, tipagem. Objetos Python são mais seguros que strings YAML. Parsing de YAML é frágil e propenso a erros.

#### Por que Refresh Manual em Vez de Polling
**Decisão**: Refresh manual em vez de polling (consulta em intervalo fixo)

**Alternativas consideradas**:
- Polling: Tela sempre atualizada, mas carga constante no apiserver
- Watch: Reativo, carga mínima, mas complexidade de implementação

**Justificativa**: Refresh manual é mais simples e não impõe carga. Para triagem, plantonista sabe quando precisa de dados atualizados.

#### Por que EndpointSlice em Vez de Endpoints
**Decisão**: EndpointSlice em vez de Endpoints

**Alternativas consideradas**:
- Endpoints: Simples, mas está sendo descontinuado
- EndpointSlice: Futuro do Kubernetes, escalável

**Justificativa**: O exercício menciona que Endpoints está sendo descontinuado. EndpointSlice é o futuro e continuará funcionando.

#### Por que Recorte Limitado a 5 Recursos
**Decisão**: MVP inclui apenas Namespaces, Pods, Deployments, Services, Events

**Alternativas consideradas**:
- Incluir todos os recursos: ConfigMaps, Secrets, Ingress, StatefulSets, DaemonSets, Jobs, CronJobs
- Incluir graficos/métricas
- Incluir logs de pods

**Justificativa**: PRD especifica "mínimo". Os 5 recursos listados são o essencial para triagem. Adicionar mais recursos estende o escopo sem valor claro para MVP. Fica para iterações futuras.

### Limitações Conhecidas

1. **Código não implementado**: Apenas spec foi escrita, código não foi implementado. Em produção, seria necessário implementar app.py, k8s_client.py e views/.

2. **Sem testes reais**: Como código não foi implementado, não há testes. Em produção, seria necessário testar contra cluster real.

3. **Sem validação real**: A validação dos cenários de falha (cluster não responde, credencial expirada, permissão negada) é especulativa. Em produção, seria necessário testar.

4. **Skills durante desenvolvimento**: As skills dos Tickets 01 e 02 apareceram em contextos onde não eram úteis (escrita de documentação). Isso não atrapalhou, mas indica que skills podem ser mais contextuais.

### Próximos Passos (Se Fosse Continuar)

1. **Implementar código**: Criar app.py, k8s_client.py e views/
2. **Testar contra cluster real**: Validar que tudo funciona
3. **Testar cenários de falha**: Cluster não responde, credencial expirada, permissão negada
4. **Adicionar mais recursos**: ConfigMaps, Secrets, Ingress, StatefulSets, DaemonSets
5. **Adicionar graficos/métricas**: Integrar com Prometheus ou Metrics Server
6. **Adicionar logs**: Mostrar logs de pods
7. **Multicluster**: Permitir troca de contexto por dentro da aplicação
