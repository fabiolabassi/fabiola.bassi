# Justificativa — Questão 02

O componente ROLE define a persona de engenheiro DevOps sênior especializado em PostgreSQL, backups em ambientes AWS e scripting bash, estabelecendo o nível técnico e o domínio esperado para o script

O componente INPUT junto com AMBIENTE fornece todos os detalhes de infraestrutura necessários: host, porta, banco, usuário, credenciais (via variável de ambiente), SO, diretório de trabalho, tamanho do dump e bucket S3 de destino, eliminando ambiguidades sobre onde o script será executado

O componente REQUISITOS FUNCIONAIS lista as 6 tarefas específicas que o script deve executar: pg_dump, gzip, upload S3, retenção 30 dias, logging com timestamp ISO-8601 e exit codes apropriados, garantindo que todas as funcionalidades necessárias sejam implementadas

O componente BOAS PRÁTICAS OBRIGATÓRIAS impõe padrões de qualidade: set -euo pipefail, validação de dependências, naming convention, cleanup de arquivos temporários e comentários explicativos, assegurando que o script seja robusto e mantível

O componente FORMATO DA ENTREGA especifica a estrutura exata: único arquivo bash, cabeçalho com descrição/uso/cron, e nenhum texto fora do script, garantindo que a saída seja diretamente utilizável em produção