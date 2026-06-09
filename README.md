# API McDonald's Simplificada

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571.svg?style=for-the-badge&logo=fastapi)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23D71F00.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-5469d4?style=for-the-badge&logo=stripe&logoColor=ffffff)

API REST desenvolvida com FastAPI para gerenciamento de usuários, produtos, pedidos e pagamentos. O projeto foi construído seguindo boas práticas de arquitetura, autenticação, validação de dados, testes automatizados e integração com serviços externos.

- Link da API: https://api-mcdonalds-simplificada.onrender.com/docs
* OBS: Por estar hospedada em plano gratuito as requisições podem ter um leve atraso para responder

## Objetivo

O objetivo desta aplicação é simular o fluxo de um sistema de pedidos online, permitindo:

* Cadastro e autenticação de usuários
* Gerenciamento de produtos
* Criação e consulta de pedidos
* Processamento de pagamentos via Stripe
* Atualização automática do status dos pedidos através de webhooks

---

## Tecnologias Utilizadas

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL
* Pydantic
* JWT Authentication

### Segurança

* Passlib
* Argon2
* Python-JOSE

### Pagamentos

* Stripe Checkout
* Stripe Webhooks

### Testes

* Pytest

### Deploy

* Render

---

## Funcionalidades

### Usuários

* Criar conta
* Realizar login
* Atualizar perfil
* Consultar do usuário autenticado

### Produtos

* Listar produtos por categoria
* Buscar produto por slug
* Controle de disponibilidade

### Pedidos

* Criar pedido
* Consultar pedidos do usuário
* Paginação de resultados
* Validação de quantidade de items no pedido

### Pagamentos

* Geração de checkout do Stripe
* Registro do link de pagamento
* Atualização automática do pedido após pagamento

---

## Arquitetura

O projeto segue uma separação em camadas para facilitar manutenção, escalabilidade e testes.

```text
app/
├── api/
├── core/
├── helpers/
├── models/
├── schemas/
├── services/
└── main.py
```

## Estrutura do Projeto

```text
.
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── deps.py
│   ├── core/
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── stripe.py
│   │   └── vars.py
│   ├── helpers/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── tests/
│   ├── services/
│   ├── test_database.py
│   └── conftest.py
│
├── alembic/
│
├── requirements.txt
├── pyproject.toml
├── alembic.ini
└── README.md
```

---

## Banco de Dados

A aplicação utiliza PostgreSQL como banco principal hospedado no supabase

As migrações são gerenciadas pelo Alembic.

## Executando Localmente

### Clonar repositório

```bash
git clone https://github.com/gabrielferreira02/api-mcdonalds-simplificada.git
cd api-mcdonalds-simplificada
```

### Criar ambiente virtual

```bash
python -m venv venv
```

### Ativar ambiente

Windows:

```bash
venv\Scripts\activate
```

Linux:

```bash
source venv/bin/activate
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

### Configurar variáveis de ambiente

Criar arquivo `.env`:

```env
SUPABASE_BUCKET=
DB_URL=
SUPABASE_KEY=
SUPABASE_URL=
STRIPE_KEY=
STRIPE_ENDPOINT_SECRET=
SECRET_KEY=
ALGORITHM=
JWT_EXPIRATION_TIME=
```

### Executar aplicação

```bash
fastapi dev
```

---

## Testes

Executar todos os testes:

```bash
pytest
```
---

## Documentação

Após iniciar a aplicação:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

## Fluxo de Pagamento

1. Usuário cria um pedido.
2. API gera uma sessão de checkout Stripe.
3. Usuário realiza o pagamento.
4. Stripe envia evento para o webhook.
5. API atualiza o status do pedido.

---

## Destaques Técnicos

* Arquitetura em camadas
* Integração com Stripe Checkout
* Webhooks para atualização automática
* Autenticação JWT
* Hash de senha com Argon2
* Testes automatizados
* Migrações versionadas com Alembic
* Deploy da base de dados e de storage no Supabase
* Deploy em produção no Render

---

## Autor

Gabriel Ferreira

Desenvolvedor Backend focado em Python, FastAPI, bancos relacionais e desenvolvimento de APIs REST.

