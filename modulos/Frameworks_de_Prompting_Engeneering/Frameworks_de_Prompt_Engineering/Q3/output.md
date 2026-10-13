A conta AWS atual totaliza USD 41.800/mês. Para atingir a meta de 15%, é necessário gerar uma economia de pelo menos USD 6.270/mês sem degradação de SLA.
Os maiores desperdícios concentram-se em EC2 on-demand (45% de utilização, USD 8.200/mês), ElastiCache Redis (40% de uso, USD 2.100/mês) e CloudWatch Logs com retenção excessiva de 90 dias (USD 2.800/mês). Juntos representam 31% da conta.
As oportunidades mapeadas somam até USD 9.840/mês (23,5% da conta) — meta de 15% plenamente atingível já na Onda 1.

Tabela de Oportunidades

Oportunidade	Serviço(s)	Economia Est. USD/mês	% Conta	Esforço	Riscos
Converter EC2 on-demand → Savings Plans	EC2 on-demand	~2.460	5,9%	Baixo	Compromisso 1 ano; validar workloads
Reduzir retenção CloudWatch Logs 90→14d	CloudWatch Logs	~1.860	4,5%	Baixo	Verificar requisitos de compliance
Rightsizing EKS clusters (uso 58%)	EKS	~1.005	2,4%	Alto	Testes de carga; risco instabilidade
Redimensionar ElastiCache Redis (uso 40%)	ElastiCache	~840	2,0%	Médio	Testar em staging; picos de carga
Consolidar NAT Gateways 3→1 + VPC endpoints	NAT Gateway	~800	1,9%	Médio	Redesenho de rede; deps cross-AZ
Otimizar RDS PostgreSQL (uso 62%)	RDS PostgreSQL	~820	2,0%	Alto	Janela de manutenção obrigatória
Migrar S3 Standard frio → S3-IA	S3 Standard	~620	1,5%	Baixo	Mapear padrões de acesso
Eliminar EBS volumes órfãos	EBS gp3	~432	1,0%	Baixo	Auditar snapshots antes de deletar

Roadmap de 3 Ondas
Onda 1 — Quick Wins (≤30 dias) | ~USD 5.172/mês
Savings Plans EC2, CloudWatch Logs 14d, S3-IA, EBS órfãos.
Onda 2 — Otimizações (31–90 dias) | ~USD 1.640/mês
Redimensionar ElastiCache Redis, consolidar NAT Gateways.
Onda 3 — Complexas (>90 dias) | ~USD 1.825/mês
Rightsizing EKS, otimização RDS PostgreSQL.