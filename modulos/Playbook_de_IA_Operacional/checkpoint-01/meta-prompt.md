# Meta-prompting para Checkpoint 01 - Triagem de Pods

## Objetivo
Criar um prompt parametrizável que recebe um snapshot do cluster Kubernetes (get pods, describe, logs) e retorna uma triagem dos pods problemáticos com causa provável e ação recomendada.

## Estratégia de Meta-prompting
1. Definir o objetivo do prompt
2. Especificar os parâmetros de entrada
3. Definir o formato de saída esperado
4. Usar few-shot learning com os 3 exemplos fornecidos
5. Estruturar o raciocínio (Chain of Thought)
6. Iterar até obter um prompt robusto

## Entradas (Parâmetros)
- {{snapshot_cluster}}: contém kubectl get pods, kubectl describe (para pods problemáticos), e kubectl logs

## Saída Esperada
Formato estruturado com:
- Lista de pods problemáticos
- Causa provável para cada um (cruzando status + eventos + logs)
- Ação recomendada para o plantonista
- Indicação clara quando não há problemas

## Exemplos para Few-Shot
1. Pod reiniciando (OOMKilled)
2. Pods que não sobem (ImagePullBackOff + Pending por falta de CPU)
3. Cluster saudável (nenhum problema)
