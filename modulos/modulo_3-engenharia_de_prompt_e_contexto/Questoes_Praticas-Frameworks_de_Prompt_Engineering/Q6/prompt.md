CONTEXT:
A Hill Valley Tech padronizou infra as a code com terraform. Padrão interno (Strickland, segurança):
- Tags obrigatórias: Owner, CostCenter, Environment
- Prefixo "hvt-" em todos os recursos
- Todo bucket s3: encryption SSE-S3, versioning ativo, block public access total, logging
- variables.tf: campos description e type obrigatórios

O módulo será consumido por todos os times como bloco reutilizável.
 
ACTION:
Crie um módulo Terraform completo para s3 aderente ao padrão:
- variables.tf — variáveis com description e type
- main.tf — recursos: aws_s3_bucket, aws_s3_bucket_versioning,
aws_s3_bucket_server_side_encryption_configuration,
aws_s3_bucket_public_access_block, aws_s3_bucket_logging
- outputs.tf — bucket_id, bucket_arn, bucket_domain_name
- examples/basic/main.tf — exemplo de consumo do módulo
 
RESULT:
delimitar cada arquivo com # === FILE: <nome> ===
nenhum default que viole o padrão. Todos os recursos usam local.common_tags.
versão de terraform >= 1.3 compatível.
 
EXAMPLE: 
Seguir o estilo do módulo de VPC interno:
 
variable "environment" {
  description = "Nome do ambiente (dev, staging, production)"
  type        = string
}
 
locals {
  common_tags = {
    Owner       = var.owner
    CostCenter  = var.cost_center
    Environment = var.environment
  }
}
 
resource "aws_vpc" "this" {
  cidr_block = var.cidr_block
  tags = merge(local.common_tags, {
    Name = "hvt-vpc-${var.environment}"
  })
}