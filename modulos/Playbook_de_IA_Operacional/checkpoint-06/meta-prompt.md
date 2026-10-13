# Meta-prompting para Checkpoint 06 - NetworkPolicy do Sentinel

## Objetivo
Criar um prompt parametrizável que recebe um manifesto permissivo de NetworkPolicy, as regras de segurança e o mapa de serviços, e devolve a versão corrigida e endurecida (default-deny com regras explícitas).

## Estratégia
- Ensinar o padrão de segurança da Aegis (default-deny, regras explícitas, comentários)
- Fornecer o mapa de serviços para que o modelo use labels corretas
- Exigir que cada regra tenha comentário explicando o fluxo legítimo
- O prompt deve gerar a v1, que será submetida a verificação

## Entradas (Parâmetros)
- {{manifesto_permissivo}}: NetworkPolicy permissivo a ser corrigida
- {{regras_seguranca}}: Padrão de segurança da Aegis
- {{mapa_servicos}}: Labels e ports de cada serviço

## Padrão esperado
- default-deny explícito (podSelector: {} com policyTypes mas sem regras de allow)
- ingress só permite Relay e API gateway
- egress só permite Forge (5432), Cerebro (9200) e DNS (53)
- Toda regra tem comentário
- Nenhum allow-all (- {})

## Processo de verificação
Após gerar a v1, vou conduzir verificação:
1. Criticar a saída como um revisor de segurança (Natasha Romanoff)
2. Levantar perguntas que um revisor faria
3. Gerar v2 endereçando os pontos
4. Repetir se necessário
