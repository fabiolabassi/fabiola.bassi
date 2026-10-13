# Meta-prompting para Checkpoint 02 - Notas de Triagem

## Objetivo
Criar um prompt parametrizável que transforma alertas crus em notas de triagem padronizadas.

## Estratégia
- Usar os exemplos de formato de saída como few-shot
- Ensinar o padrão estruturado (5 campos obrigatórios)
- O prompt deve inferir impacto, hipótese e ação a partir do alerta cru

## Entrada (Parâmetro)
- {{alerta_cru}}: Alerta bruto do sistema

## Formato de Saída (ensinado via few-shot)
ALERTA: [resumo do alerta]
IMPACTO: [afetação de serviço/tenant]
HIPÓTESE INICIAL: [causa provável]
AÇÃO IMEDIATA: [ação do plantonista]
ESCALAR PARA: [@handle com timeout]

## Decisão de Método
Vou usar few-shot learning com os 3 exemplos de saída como demonstração do padrão. Isso é mais efetivo que tentar descrever o padrão em texto, pois o modelo aprende por exemplo o tom, nível de detalhe e formato exato.
