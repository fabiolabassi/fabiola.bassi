# === FILE: variables.tf ===
 
variable "environment" {
  description = "Nome do ambiente (dev, staging, production)"
  type        = string
}
variable "owner" {
  description = "Time ou pessoa responsável pelo recurso (tag Owner)"
  type        = string
}
variable "cost_center" {
  description = "Centro de custo associado (tag CostCenter)"
  type        = string
}
variable "bucket_name_suffix" {
  description = "Sufixo único: hvt-{suffix}-{environment}"
  type        = string
}
variable "logging_target_bucket" {
  description = "ID do bucket de destino para logs de acesso"
  type        = string
}
variable "logging_target_prefix" {
  description = "Prefixo dos objetos de log"
  type        = string
  default     = "s3-access-logs/"
}
 
# === FILE: main.tf ===
 
terraform {
  required_version = ">= 1.3"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
}
 
locals {
  bucket_name = "hvt-${var.bucket_name_suffix}-${var.environment}"
  common_tags = {
    Owner       = var.owner
    CostCenter  = var.cost_center
    Environment = var.environment
  }
}
 
resource "aws_s3_bucket" "this" {
  bucket = local.bucket_name
  tags   = merge(local.common_tags, { Name = local.bucket_name })
}
 
resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration { status = "Enabled" }
}
 
resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
    bucket_key_enabled = true
  }
}
 
resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
 
resource "aws_s3_bucket_logging" "this" {
  bucket        = aws_s3_bucket.this.id
  target_bucket = var.logging_target_bucket
  target_prefix = var.logging_target_prefix
}
 
# === FILE: outputs.tf ===
 
output "bucket_id"          { value = aws_s3_bucket.this.id }
output "bucket_arn"         { value = aws_s3_bucket.this.arn }
output "bucket_domain_name" { value = aws_s3_bucket.this.bucket_domain_name }
 
# === FILE: examples/basic/main.tf ===
 
module "lift_artifacts" {
  source                = "../../"
  environment           = "production"
  owner                 = "lift-team"
  cost_center           = "CC-1042"
  bucket_name_suffix    = "lift-artifacts"
  logging_target_bucket = "hvt-access-logs-production"
}