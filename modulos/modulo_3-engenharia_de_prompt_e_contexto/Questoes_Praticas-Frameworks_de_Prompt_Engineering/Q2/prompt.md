vc é um engenheiro DevOps sênior especializado em PostgreSQL, backups em
ambientes AWS e scripting bash para operações de banco de dados em produção.
 
Escreva um script bash de backup automatizado para o seguinte ambiente:
 
AMBIENTE:
- Host: ledger-db.internal.hvt.io, Porta: 5432
- Banco: ledger_prod, Usuário: backup_user
- Senha: variável de ambiente PGPASSWORD (populada via AWS Secrets Manager / IAM role)
- SO: Ubuntu 22.04 LTS
- Diretório de trabalho: /var/backups/ledger (80 GB livres)
- Dump compactado médio: ~12 GB
- Bucket S3 de destino: hvt-ledger-backups (região us-east-1)
 
REQUISITOS FUNCIONAIS:
1. Exportar o banco com pg_dump
2. Compactar o arquivo gerado com gzip
3. Fazer upload do arquivo para o S3 com aws s3 cp
4. Manter retenção de 30 dias no S3 (deletar arquivos mais antigos automaticamente)
5. Registrar cada execução em /var/log/ledger-backup.log com timestamp ISO-8601
6. Sair com exit code 1 (e logar o erro) em qualquer falha; exit code 0 em sucesso
 
BOAS PRÁTICAS OBRIGATÓRIAS:
- set -euo pipefail no início
- Validar dependências (pg_dump, gzip, aws) antes de executar
- Nome do arquivo: ledger_prod_YYYYMMDD_HHMMSS.sql.gz
- Clean up: não deixar arquivos temporários em disco em caso de falha
- Comentários explicando cada seção do script
 
FORMATO DA ENTREGA:
- Um único arquivo bash
- Comentário de cabeçalho com descrição, uso e linha de cron sugerida (diária às 02:00 UTC)
- Nenhum texto fora do script (sem markdown, sem explicações externas)