# ADR - Architecture Decision Record: Linguagem e Stack

## Status
Aceito

## Contexto
O dashboard do cluster precisa ser uma aplicação local que mostra o estado do cluster. Precisa escolher linguagem e stack para UI.

## Decisão
Usar Python 3.10+ com Streamlit para UI.

## Drivers
- **Time de infraestrutura vai manter**: Python é linguagem já usada em Ticket 03 (auditor de VM), curva de aprendício menor
- **Rapidez de desenvolvimento**: Streamlit permite criar dashboards com muito pouco código
- **Familiaridade com Python**: Time já usa Python para automação (Ansible, Terraform providers)
- **Simplicidade de UI**: Streamlit abstrai HTML/CSS/JS, foca em Python

## Alternativas Consideradas

### A1: Go com Servidor HTTP + HTML/JS
**Descrição**: Usar Go para backend HTTP e HTML/JS vanilla ou framework (React, Vue) para frontend

**Prós**:
- Binário único, sem dependência de runtime
- Performance superior
- Ecossistema maduro de Go

**Contras**:
- Curva de aprendizado mais íngreme para time de infraestrutura
- Desenvolvimento de UI mais complexo (duas linguagens: Go + JS)
- Build e deploy mais complexos

**Decisão**: Rejeitado. Time de infraestrutura já conhece Python e está usando em Ticket 03. O ganho de performance não é crítico para dashboard de triagem (latência de rede é fator dominante).

### A2: JavaScript (React/Next.js)
**Descrição**: Usar JavaScript com React ou Next.js para UI

**Prós**:
- Ecossistema maduro de componentes UI
- Frameworks modernos (Next.js, Vite)
- Performance no frontend

**Contras**:
- Curva de aprendizado para time de infraestrutura
- Requer bundler/compilação (não é executável direto)
- Menos familiar para time de infraestrutura

**Decisão**: Rejeitado. Time de infraestrutura provavelmente não tem expertise recente em JavaScript moderno. Curva de aprendizado seria significativa.

### A3: Python com Dash
**Descrição**: Usar Python com Dash (plotly) para UI

**Prós**:
- Similar ao Streamlit (Python-only)
- Ecossistema maduro de dashboards

**Contras**:
- Menos popular que Streamlit para dashboards simples
- Curva de aprendício maior
- Mais verboso para dashboards simples

**Decisão**: Rejeitado. Streamlit é mais simples e popular para dashboards Python. Dash é mais adequado para dashboards de dados complexos com gráficos, não para visualização de estado de cluster.

## Consequências
- Aplicação requer Python 3.10+ e Streamlit instalados
- Código é interpretado, não compilado
- UI é declarativa em Python (sem HTML/CSS/JS)
- Time de infraestrutura já conhece Python

## Referências
- Streamlit documentation: https://docs.streamlit.io/
- Python Kubernetes client: https://github.com/kubernetes-client/python
