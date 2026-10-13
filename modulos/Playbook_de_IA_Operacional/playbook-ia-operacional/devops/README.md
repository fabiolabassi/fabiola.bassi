# DevOps

Prompts voltados a **infraestrutura, automação e operação** de sistemas: pipelines de CI/CD, containers, orquestração, provisionamento, observabilidade, confiabilidade e segurança operacional.

## Escopo

Entram aqui prompts relacionados a:

- Pipelines de CI/CD (GitHub Actions, GitLab CI, Jenkins etc.).
- Containers e orquestração (Docker, Kubernetes, Helm).
- Infraestrutura como código (Terraform, Pulumi, Ansible).
- Provedores de nuvem (AWS, GCP, Azure) e seus recursos.
- Observabilidade (logs, métricas, tracing, alertas, dashboards).
- Confiabilidade, SRE, postmortems e análise de incidentes.
- Segurança operacional (hardening, secrets, políticas de acesso).

## Fora de escopo

- Escrita de código de aplicação → usar `desenvolvimento/`.
- Conteúdo educacional sobre DevOps (aulas, artigos, vídeos) → usar `criacao-conteudo/`.

## Prompts

- [triagem-de-pods](./triagem-de-pods/) — Analisa snapshot de cluster Kubernetes e identifica pods problemáticos com causa provável e ação recomendada
- [nota-de-triagem](./nota-de-triagem/) — Transforma alertas crus em notas de triagem padronizadas com 5 campos obrigatórios
- [causa-raiz-cerebro](./causa-raiz-cerebro/) — Analisa config, métricas e logs do Cerebro para identificar causa-raiz de degradação de busca
- [backpressure-relay](./backpressure-relay/) — Compara múltiplas abordagens de backpressure para o Relay, pesando prós e contras antes de recomendar
- [migracao-forge-diagnostico](./migracao-forge-diagnostico/) — Analisa o estado atual do Forge (pipeline batch) e identifica riscos, dependências e pontos de atenção para migração para event-driven
- [migracao-forge-planejamento](./migracao-forge-planejamento/) — Propõe um passo a passo da migração do Forge de batch para event-driven baseado no diagnóstico, com etapas reversíveis
- [migracao-forge-execucao](./migracao-forge-execucao/) — Detalha o plano de migração do Forge com ações específicas, rollback plan e critérios de sucesso medíveis
- [networkpolicy-sentinel](./networkpolicy-sentinel/) — Corrige manifesto permissivo de NetworkPolicy e transforma em política default-deny com regras explícitas
