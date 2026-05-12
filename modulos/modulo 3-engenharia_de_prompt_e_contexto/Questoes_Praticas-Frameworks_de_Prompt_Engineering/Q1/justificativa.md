# Justificativa — Questão 01

## Data: 11-05-26

## Modelo utilizado

Provider: ChatGPT  
Modelo: OpenAI GPT

O modelo e provider foram escolhidos pela simplicidade de output do dockerfile.

## Framework

R-T-F (Role, Task, Format)

## Aplicação do framework no prompt

### Role

No prompt foi definido o papel:

> Você é um engenheiro de software sênior especialista em microserviços, Docker e Kubernetes.

A definição do papel orienta o modelo a responder com nível técnico compatível com um profissional experiente, aplicando boas práticas de containerização e deploy.

### Task

A tarefa foi descrita de forma direta:

> Criar um Dockerfile para o serviço Lift, considerando sua estrutura de projeto, dependências, porta de execução, variáveis de ambiente e comando de inicialização.

Também foram incluídos no prompt:
- estrutura do projeto;
- conteúdo do requirements.txt;
- variáveis de ambiente necessárias;
- comando real utilizado em produção.

Essas informações contextualizam corretamente a geração do Dockerfile.

### Format

O formato solicitado foi:

> Responder apenas com o conteúdo final do Dockerfile em bloco de código.

Esse componente garante que a saída seja objetiva, padronizada e pronta para uso no projeto.