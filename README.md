# 🏢 Dify Enterprise Hub – A Fábrica de IA Corporativa

[![Platform Status](https://img.shields.io/badge/Platform-Dify%20Enterprise%20Latest-blue)](#)
[![Vector Engine](https://img.shields.io/badge/Vector%20Store-Qdrant%201.10-green)](#)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-brightgreen)](#)
[![Security & DLP](https://img.shields.io/badge/Security-Zero--Trust%20%7C%20SSRF%20Proxy%20%7C%20Cgroups%20Sandbox-orange)](#)
[![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey)](#)

O **Dify Enterprise Hub** é uma plataforma corporativa de engenharia de IA visual, orquestração de fluxos complexos (RAG Híbrido, Agentes Autônomos e Chatbots) e governança centralizada de modelos. A solução combina o motor open-source do Dify, busca vetorial em alta performance com Qdrant, execução segura de código isolado via Dify Sandbox, barramento assíncrono com Celery/Redis, barreira de segurança DLP (Data Loss Prevention) com proxy de saída anti-SSRF e extensão para sistemas corporativos legados (ERP, CRM, RH) via Custom OpenAPI Tools.

Este projeto resolve o principal obstáculo na adoção corporativa de IA: **O Gargalo da Engenharia**, transformando a TI de uma executora de pedidos manuais em uma verdadeira **Fábrica de IA** interna e descentralizada com governança, segurança e controle orçamentário (FinOps).

---

## 🏛️ 1. Topologia da Arquitetura e Rede Segura

```
                                [ Usuários / Aplicações Consumidoras ]
                                                  │
                                                  ▼ HTTPS (:443) / HTTP (:80)
┌─────────────────────────────────────────────────┴─────────────────────────────────────────────────┐
│                                    NGINX EDGE GATEWAY & PROXY                                     │
│  - Terminação TLS 1.3                   - Rate Limiting por IP/API Key                            │
│  - Mascaramento de Cabeçalhos           - Roteamento Interno com Resiliência                      │
└───────┬─────────────────────────┬─────────────────────────┬───────────────────────────────┬───────┘
        │                         │                         │                               │
        │ /                       │ /console/api            │ /v1 (Chat/Completion)         │ /tools/api
        ▼                         ▼                         ▼                               ▼
┌──────────────┐          ┌──────────────────────────────────┐             ┌────────────────────────┐
│  dify-web    │          │             dify-api             │             │  enterprise-tools-api  │
│  (Next.js)   │          │          (Flask/Gunicorn)        │             │   (FastAPI / Python)   │
│  Porta: 3000 │          │            Porta: 5001           │             │      Porta: 8080       │
└──────────────┘          └────────────────┬─────────────────┘             └───────────┬────────────┘
                                           │                                           │
       ┌───────────────────────────────────┼───────────────────────────────────┐       │
       ▼                                   ▼                                   ▼       ▼
┌──────────────┐                    ┌──────────────┐                    ┌───────────────────────────┐
│  PostgreSQL  │                    │ Redis Cluster│                    │      Sistemas Legados     │
│  (Metadata)  │                    │ (Broker/Queue│                    │    (ERP, SAP, TOTVS, RH)  │
│ Porta: 5432* │                    │ Porta: 6379* │                    └───────────────────────────┘
└──────────────┘                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │ dify-worker  │
                                    │ (Celery App) │
                                    └──────┬──────┘
                                           │
             ┌─────────────────────────────┼─────────────────────────────┐
             ▼                             ▼                             ▼
      ┌─────────────┐               ┌─────────────┐               ┌─────────────┐
      │   Qdrant    │               │  SSRF Proxy │               │dify-sandbox │
      │(Vector HNSW)│               │ (Squid Out) │               │(Isolated RCE│
      │ Porta: 6333*│               └──────┬──────┘               │ Porta: 8194*│
      └─────────────┘                      │                      └─────────────┘
                                           ▼
                            [ Provedores de LLM Externos ]
                            (OpenAI, Anthropic, Bedrock)

*Portas internas: fechadas para a internet, acessíveis exclusivamente na bridge network do Docker.
```

---

## 📁 2. Estrutura Canônica de Diretórios

```
dify-enterprise-hub/
├── docker/
│   ├── docker-compose.yml              # Orquestrador corporativo com redes segregadas
│   ├── .env.example                    # Template de variáveis de ambiente de produção
│   └── nginx/
│       ├── conf.d/
│       │   └── default.conf            # Roteamento de rotas e políticas de cabeçalho
│       └── ssl/                        # Certificados TLS corporativos
├── tools_api/                          # Microserviço de Ferramentas Corporativas
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # Entrypoint FastAPI e rotas de extensão
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic Settings e tokens de segurança
│   │   │   └── security.py             # Validação de API Key entre Dify e Ferramentas
│   │   └── routers/
│   │       ├── hr.py                   # Integração com sistemas de férias/benefícios
│   │       └── finance.py              # Integração de autorização de despesas e reembolsos
│   ├── Dockerfile
│   └── requirements.txt
├── scripts/
│   ├── backup_db.sh                    # Backup consistente de Postgres e Qdrant
│   ├── restore_db.sh                   # Procedimento de Disaster Recovery
│   └── export_openapi.py               # Exportador de schemas OpenAPI para o Dify
├── tests/
│   └── test_tools_api.py               # Testes automatizados com pytest e TestClient
├── openapi.json                        # Schema OpenAPI 3.1 para importação no Dify
├── openapi.yaml                        # Schema OpenAPI YAML
├── TUTORIAL.md                         # Guia prático passo a passo de operação
└── README.md
```

---

## 📊 Roteiro de Apresentação Executiva: A Fábrica de IA

### Slide 1: O Gargalo da Inovação
> *"Hoje, todas as áreas da nossa empresa querem usar Inteligência Artificial para ganhar tempo. O problema é que todas essas ideias caem na fila da equipe de Tecnologia, que precisa programar cada solução do zero. A inovação está refém da nossa capacidade de desenvolvimento de software."*

### Slide 2: A Solução – A Nossa Fábrica de IA Visual
> *"Apresentamos o nosso Hub de IA Corporativo. Com o projeto dify-enterprise-hub, instalamos uma plataforma visual de engenharia de IA. O que antes demorava 2 meses de programação em código, agora pode ser desenhado visualmente em uma tarde, conectando LLMs, bases de conhecimento e sistemas internos."*

### Slide 3: Democratização e Autonomia com Governança
> *"O maior poder desta plataforma é a descentralização assistida. Com um treinamento breve, gestores de RH, Finanças ou Operações podem criar assistentes para sua equipe, enquanto a TI garante isolamento de rede, políticas de DLP, mascaramento de credenciais e controle de execução via cgroups."*

### Slide 4: Segurança (Zero-Trust & Anti-SSRF) e FinOps
> *"Ao isolar bancos de dados e motores vetoriais em rede interna restrita e rotear requisições externas via Squid SSRF Proxy, evitamos vazamento de dados internos. Ao mesmo tempo, auditamos o consumo de tokens e custos por departamento em tempo real."*

---

## 🛠️ Extensibilidade Corporativa: Custom Tools API

O microsserviço corporativo em `tools_api/` exporta contratos compatíveis com o padrão OpenAPI 3.0/3.1 e autenticação via Bearer Token (`HTTPBearer`):

- **`POST /api/v1/hr/vacation-balance`**: Consulta sistemas legados de folha de pagamento e retorna o saldo de dias de férias vigentes e data limite de concessão para matrículas no formato `EMP-XXXX`.
- **`POST /api/v1/finance/submit-reimbursement`**: Encaminha notas fiscais de despesas corporativas para a esteira de auditoria financeira.

O contrato OpenAPI gerado em `openapi.yaml` e `openapi.json` pode ser importado com 1 clique no menu **Tools -> Custom Tools** do Dify.

---

## 🚀 Guia Rápido de Operação em Produção

### 1. Inicialização da Infraestrutura
```bash
cd dify-enterprise-hub/docker

# 1. Gerar e configurar chaves criptográficas no .env
cp .env.example .env

# DICA: Gerar chaves seguras para produção via openssl
openssl rand -base64 42 # Use para DIFY_SECRET_KEY
openssl rand -hex 16    # Use para REDIS_PASSWORD, DB_PASSWORD, SANDBOX_API_KEY, TOOLS_API_KEY

# 2. Subir o cluster completo com rebuild de containers internos
docker compose up -d --build

# 3. Validar a inicialização e os healthchecks de todos os serviços
docker compose ps
```

### 2. Configuração do OpenAPI Custom Tool no Console do Dify
1. Acesse o painel do Dify via navegador: `http://<IP_DO_SERVIDOR>/`.
2. Vá em **Ferramentas (Tools)** -> **Personalizadas (Custom Tools)** -> **Criar Ferramenta Personalizada**.
3. Preencha os campos estruturais:
   - **Nome da Ferramenta**: `EnterpriseLegacyConnect`
   - **Esquema**: Selecione **Importar a partir de URL** e aponte para `http://nginx/tools/openapi.json` (ou cole o schema JSON gerado em `http://localhost/tools/openapi.json`).
   - **Tipo de Autenticação**: **API Key** -> **Método**: `Bearer` -> Insira o valor configurado na variável `TOOLS_API_KEY`.
4. Os blocos de consulta de férias e solicitação de reembolso estarão imediatamente disponíveis para inclusão em qualquer nó do Dify Workflow Engine.

---

## 📊 Matriz Comparativa: Versão Anterior vs. Versão Corporativa

| Dimensão | Versão Anterior | Versão Corporativa Refatorada |
|---|---|---|
| **Isolamento de Portas** | Portas do Postgres, Redis, Sandbox e Qdrant abertas no host (5432, 6379, 8194, 6333) | Isolamento estrito em rede interna (`backend_net`); apenas o Nginx expõe 80/443 |
| **Proteção contra SSRF** | Não implementado (suscetível a varredura interna pela LLM) | Proxy de filtragem de saída Squid (`ssrf-proxy`) para requisições externas |
| **Execução de Código (RCE)** | Dify Sandbox sem cotas de hardware declaradas | Sandbox com limitação estrita de CPU (2 cores) e memória (2048M) via cgroups |
| **Custom Tools API** | Menção teórica a endpoints sem código modular nem contrato Bearer | Microsserviço FastAPI modularizado (`core/`, `routers/`), Bearer Token e schema OpenAPI 3.0/3.1 |
| **Governança de Dados** | Logs em texto puro e credenciais padrão sem validação estrita | Credenciais validadas via variáveis obrigatórias com checagem `:?` no Compose |
| **Disaster Recovery** | Ausência de automação de backup e recuperação | Scripts operacionais de backup e restauração consistente (`backup_db.sh`, `restore_db.sh`) |
