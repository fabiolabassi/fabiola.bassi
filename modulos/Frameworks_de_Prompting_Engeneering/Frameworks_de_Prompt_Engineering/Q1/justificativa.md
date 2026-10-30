# Justificativa — Questão 01

No prompt, o componente Role aparece ao definir o modelo como um engenheiro de software sênior especialista em microserviços, Docker e Kubernetes.
O componente Task está na solicitação de criação do Dockerfile para o serviço Lift, incluindo requisitos técnicos do projeto.
O componente Format foi aplicado ao instruir que a resposta fosse entregue apenas como o conteúdo final do Dockerfile em bloco de código.

## Melhorias implementadas após feedback

Com base no feedback recebido, o prompt foi atualizado para especificar explicitamente as boas práticas de segurança esperadas:

1. **Multi-stage build**: O Dockerfile agora usa dois estágios - builder para instalar dependências e runtime para a imagem final, reduzindo o tamanho da imagem e excluindo ferramentas de build desnecessárias.

2. **Usuário não-root**: Foi criado um usuário `appuser` para rodar a aplicação, seguindo a best practice de não executar containers como root para reduzir o risco de segurança.

3. **Secrets apenas em runtime**: As variáveis de ambiente sensíveis `DATABASE_URL` e `API_KEY` NÃO são definidas no Dockerfile. Somente são fornecidas em runtime via Kubernetes secrets ou env vars, evitando que secrets fiquem gravados na imagem Docker.

4. **Imagem otimizada**: O multi-stage build e o uso de `--no-cache-dir` no pip garantem uma imagem menor e mais eficiente.