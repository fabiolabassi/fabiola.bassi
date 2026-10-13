---
nome: Nota de Triagem Padronizada
descricao: Transforma alertas crus em notas de triagem padronizadas com 5 campos obrigatórios
versao: 1.0.0
tags: [sre, triagem, alertas, documentacao]
inputs:
  - nome: alerta_cru
    descricao: Alerta bruto do sistema contendo timestamp, sistema afetado e descrição do problema
---

# Nota de Triagem Padronizada

## Objetivo
Prompt para transformar alertas crus em notas de triagem padronizadas seguindo um formato estruturado de 5 campos (ALERTA, IMPACTO, HIPÓTESE INICIAL, AÇÃO IMEDIATA, ESCALAR PARA). Garante consistência na documentação de incidentes e facilita a continuidade entre turnos de plantão.

## Quando Usar
- Ao abrir uma nota de triagem para qualquer alerta do Sentinel, Relay, Forge ou Cerebro
- Para padronizar a documentação de incidentes entre diferentes engenheiros
- Para treinar novos membros do time no formato esperado de notas
- Para documentação pós-incidente (nota inicial)

## Exemplo de Uso

### Entrada
```
2026-05-12 14:02:09 UTC [Sentinel] autoscaler hit max replicas (60/60) on sentinel-api,
queue depth on Relay growing 2k/min, CPU avg 88%, tenant stark-industries
sending 4x baseline volume after onboarding new region
```

### Saída Esperada
```
ALERTA: Sentinel - autoscaler atingiu máximo de replicas (60/60) com CPU 88%
IMPACTO: tenant stark-industries pode ter latência degradada; Relay com fila crescendo 2k/min
HIPÓTESE INICIAL: onboarding de nova região do tenant stark-industries gerou pico de 4x volume
AÇÃO IMEDIATA: aumentar max replicas do autoscaler do sentinel-api temporariamente
ESCALAR PARA: @sentinel-core se fila do Relay não estabilizar em 10min
```

## Limitações
- O prompt infere impacto e hipótese baseado apenas no alerta cru - em situações complexas, pode ser necessário investigação adicional
- Assume familiaridade com os sistemas da Aegis (Relay, Forge, Cerebro, Sentinel)
- O @handle de escalonamento é uma sugestão baseada no sistema afetado - pode não corresponder exatamente à estrutura de times da empresa
- Não lida com alertas de múltiplos sistemas simultaneamente - cada alerta deve gerar uma nota separada
- A hipótese inicial é baseada apenas no alerta - investigação real pode revelar causa diferente

## Técnica Utilizada
- Few-Shot Learning: 3 exemplos de notas bem formatadas ensinam o padrão de tom, nível de detalhe e estrutura
- Role Prompting: define o modelo como "engenheiro de plantão na Aegis" para alinhar o contexto
- Constraint Specification: instruções explícitas sobre concisão (máximo 8 linhas) e formato do @handle
