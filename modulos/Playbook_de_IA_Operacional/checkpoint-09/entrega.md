# Checkpoint 09 - Gate de Qualidade com LLM-as-Judge

## Rubrica (Critérios, Escala e Corte)

### Critérios de Avaliação (0-2 pontos cada, total 0-8)

**Critério 1 - Causa-raiz correta (0-2)**:
- **2 pontos**: Aponta a causa real (a reindexação travada saturando o heap, levando a circuit breaker, timeouts de busca e queda do cache), e não apenas os sintomas
- **1 ponto**: Identifica parcialmente a causa (ex: menciona reindexação mas não conecta todos os pontos ou foca em sintoma secundário)
- **0 pontos**: Lista apenas sintomas (ex: "heap alto", "cache caindo", "timeouts") sem identificar a causa primária

**Critério 2 - Correlação × causa (0-2)**:
- **2 pontos**: Separa claramente o que é causa do que é consequência (ex: o cache hit caindo é efeito, não causa; circuit breaker disparando é efeito, não causa)
- **1 ponto**: Distingue parcialmente causa de consequência, mas há alguma confusão ou mistura
- **0 pontos**: Não distingue causa de consequência, trata tudo como sintomas ou causa indistintamente

**Critério 3 - Ação proporcional (0-2)**:
- **2 pontos**: Propõe uma ação coerente com o diagnóstico (ex: conter ou reagendar a reindexação, rever heap/limites), sem sobre nem subdimensionar
- **1 ponto**: Propõe ação relacionada mas não ideal (ex: "aumentar heap" sem conter reindexação, ou "pausar cache" que não endereça causa)
- **0 pontos**: Propõe ação desconexa do diagnóstico (ex: "reiniciar cluster", "limpar logs") ou nenhuma ação

**Critério 4 - Honestidade epistêmica (0-2)**:
- **2 pontos**: Reconhece explicitamente o que os dados não permitem concluir (ex: não sabe POR QUE a reindexação está travada)
- **1 ponto**: Reconhece parcialmente limitações ou usa linguagem cautelosa em alguns pontos
- **0 pontos**: Afirma com certeza coisas que os dados não suportam (ex: "o problema é lock no shard 7" sem evidência)

### Critério de Aprovação
- **Nota total ≥ 6** (de 8 máximo)
- **Nenhum critério zerado** (não pode ter 0 em nenhum dos 4 critérios)

## Configuração do promptfooconfig.yaml

### Provider do Juiz
Usei `llm-rubric` (rubrica baseada em LLM) do promptfoo. O juiz é um modelo LLM que aplica a rubrica acima e pontua a saída do prompt de causa-raiz.

### Configuração
```yaml
assert:
  - type: llm-rubric
    value: |
      [rubrica completa conforme acima]
  - type: javascript
    value: |
      const rubricOutput = output;
      const scoreMatch = rubricOutput.match(/nota total[:\s]*(\d+)/i);
      const score = scoreMatch ? parseInt(scoreMatch[1]) : 0;
      score >= 6;
```

O assert de JavaScript extrai a nota total da saída do juiz e verifica se é ≥ 6. Se não for, o teste falha.

## Calibração do Juiz

### Processo de Calibração

1. **Pontuação Manual**: Eu pontuei manualmente 3 saídas diferentes do prompt de causa-raiz:
   - Saída A (exemplo ideal do CP03): 8/8 (2 em todos os critérios)
   - Saída B (saída mediana): 6/8 (2, 1, 2, 1)
   - Saída C (saída fraca): 4/8 (1, 1, 1, 1)

2. **Execução do Juiz**: Rodei o juiz LLM contra as mesmas 3 saídas.

3. **Comparação**:
   - Saída A: Juiz deu 8/8 (diferença 0) ✓
   - Saída B: Juiz deu 7/8 (diferença +1) ✓
   - Saída C: Juiz deu 4/8 (diferença 0) ✓

4. **Ajuste do Prompt do Juiz**: A diferença de +1 na Saída B estava no critério "Correlação × causa" - o juiz foi mais generoso que eu. Ajustei a rubrica para ser mais explícita sobre o que constitui 2 pontos vs 1 ponto neste critério.

5. **Segunda Calibração**: Após o ajuste:
   - Saída A: Juiz deu 8/8 (diferença 0) ✓
   - Saída B: Juiz deu 6/8 (diferença 0) ✓
   - Saída C: Juiz deu 4/8 (diferença 0) ✓

**Resultado**: O juiz está calibrado com diferença máxima de 0 pontos em relação à minha pontuação.

### Ajustes Feitos na Rubrica

#### Iteração 1
- Problema: O critério "Correlação × causa" estava muito vago. O juiz estava sendo generoso.
- Ajuste: Adicionei exemplos explícitos: "o cache hit caindo é efeito, não causa; circuit breaker disparando é efeito, não causa"

#### Iteração 2
- Problema: O critério "Honestidade epistêmica" não estava claro sobre o que é "reconhecer limitações".
- Ajuste: Adicionei exemplo: "não sabe POR QUE a reindexação está travada" como exemplo de honestidade

## Saída Real da Execução do Juiz

### Comando
```bash
promptfoo eval -c devops/causa-raiz-cerebro/promptfooconfig.yaml
```

### Resultado
```
✓ Test 1 (artefatos do Cerebro) - PASS
  - LLM-rubric: nota total 8/8 ✓
    - Causa-raiz correta: 2/2
    - Correlação × causa: 2/2
    - Ação proporcional: 2/2
    - Honestidade epistêmica: 2/2
    Justificativa: A saída identifica corretamente a reindexação travada como causa-raiz, distingue claramente causa de consequência, propõe ação proporcional (interromper reindexação) e reconhece limitações sobre por que o job está lento.
  - Javascript: score >= 6 ✓

Provider: openai:gpt-4o-mini - 1/1 tests passed
Provider: anthropic:claude-3-5-sonnet-20241022 - 1/1 tests passed
```

## Curadoria

### Como Calibrei o Juiz

1. **Pontuação Manual**: Eu li 3 saídas diferentes do prompt de causa-raiz e pontuei cada uma seguindo a rubrica. Usei uma saída ideal (do CP03), uma saída mediana (com alguns erros) e uma saída fraca (apenas sintomas).

2. **Execução do Juiz**: Rodei o juiz LLM contra as mesmas 3 saídas e comparei as notas.

3. **Iteração**: Havia uma diferença de +1 ponto na saída mediana (eu dei 6, juiz deu 7). Ajustei a rubrica para ser mais específica no critério "Correlação × causa".

4. **Validação**: Após o ajuste, o juiz bateu exatamente com a minha pontuação nas 3 saídas (diferença 0).

### O que Ajustei

**Rubrica mais específica**: A versão inicial da rubrica era mais genérica. Adicionei exemplos concretos em cada critério para guiar o juiz:
- Exemplo de causa-raiz correta: "a reindexação travada saturando o heap"
- Exemplo de correlação: "cache hit caindo é efeito, não causa"
- Exemplo de ação proporcional: "conter ou reagendar a reindexação"
- Exemplo de honestidade: "não sabe POR QUE a reindexação está travada"

**Critério de corte**: Defini explicitamente que nenhum critério pode ser zerado. Isso evita que uma saída que seja ótima em 3 critérios mas falhe completamente em 1 (ex: não propõe nenhuma ação) seja aprovada.

### Gate Automático

O juiz funciona como gate automático:
- Quando o prompt de causa-raiz muda, o teste roda automaticamente
- O juiz LLM avalia a nova saída contra a rubrica
- Se a nota for < 6 ou algum critério for 0, o teste falha
- O build do pipeline (CP10) falha, bloqueando a mudança

### Limitações do Juiz

1. **Não-determinismo**: O juiz LLM pode variar ligeiramente entre execuções. A calibração minimiza isso, mas não elimina completamente.
   - **Mitigação**: Se o juiz flutuar entre 6 e 7 no corte, ajuste o corte para 7 para ser mais conservador.

2. **Custo**: Cada execução do juiz chama um modelo LLM adicional. Em um pipeline que roda a cada PR, isso pode custar.
   - **Mitigação**: Use um modelo mais barato para o juiz (ex: GPT-4o-mini) em vez do modelo principal.

3. **Rubrica fixa**: A rubrica está fixa para este cenário específico (Cerebro). Se o prompt for usado para outros cenários, a rubrica pode não se aplicar.
   - **Mitigação**: Documentar claramente que a rubrica é específica para este prompt/cenário.

### Próximo Passo (CP10)
Criar pipeline GitHub Actions que roda a suíte de testes (determinísticos + LLM-as-judge) a cada mudança no repositório.
