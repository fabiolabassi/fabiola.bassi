ROLE:
Você é um engenheiro de software sênior especialista em microserviços, Docker e Kubernetes.

TASK:
Criar um Dockerfile para o serviço Lift, uma API Python/Flask que será migrada de VMs para um cluster Kubernetes.

Estrutura do projeto:

lift/
├── app.py
├── requirements.txt
├── lib/
│   ├── auth.py
│   └── storage.py
└── tests/
    └── test_app.py

Conteúdo do requirements.txt:
Flask==3.0.0
gunicorn==21.2.0
requests==2.31.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9

Em produção o serviço sobe com:
gunicorn --bind 0.0.0.0:8080 --workers 4 app:app

A aplicação roda na porta 8080 e precisa das variáveis de ambiente:
- DATABASE_URL
- API_KEY

Seguir boas práticas de criação de imagem Docker para produção em Kubernetes.

FORMAT:
Responder apenas com o conteúdo final do Dockerfile em bloco de código.