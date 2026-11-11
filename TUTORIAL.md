# 📖 Tutorial Prático: Implantação e Operação do Dify Enterprise Hub

Este tutorial guia você passo a passo na inicialização do **Dify Enterprise Hub**, na criação da sua primeira **Knowledge Base com Qdrant**, na integração da **Custom Tools API de ERP/RH** e na montagem de um fluxo visual completo de IA.

---

## 📋 Índice
1. [Preparação do Ambiente](#1-preparação-do-ambiente)
2. [Inicialização dos Serviços com Docker Compose](#2-inicialização-dos-serviços-com-docker-compose)
3. [Configuração Inicial do Dify](#3-configuração-inicial-do-dify)
4. [Carregando Documentos na Knowledge Base (Qdrant)](#4-carregando-documentos-na-knowledge-base-qdrant)
5. [Integrando a Ferramenta de ERP/RH no Dify (OpenAPI)](#5-integrando-a-ferramenta-de-erprh-no-dify-openapi)
6. [Criando o Assistente no Canvas Visual](#6-criando-o-assistente-no-canvas-visual)
7. [Testes e Verificação de Conectividade](#7-testes-e-verificação-de-conectividade)
8. [Procedimentos de Backup e Disaster Recovery](#8-procedimentos-de-backup-e-disaster-recovery)
9. [Troubleshooting e Resolução de Problemas](#9-troubleshooting-e-resolução-de-problemas)

---

## 1. Preparação do Ambiente

Antes de iniciar, certifique-se de ter instalado:
- **Docker Engine 24+** e plugin do **Docker Compose v2**
- **Python 3.11+** (caso deseje rodar a API de testes localmente fora do Docker)
- Git

Clone ou posicione-se no diretório do projeto:
```bash
cd dify-enterprise-hub/docker
```

Copie o arquivo de variáveis de ambiente e gere chaves criptográficas seguras:
```bash
cp .env.example .env

# DICA: Gerar chaves seguras para produção via openssl
openssl rand -base64 42 # DIFY_SECRET_KEY
openssl rand -hex 16    # REDIS_PASSWORD, DB_PASSWORD, SANDBOX_API_KEY, TOOLS_API_KEY
```

---

## 2. Inicialização dos Serviços com Docker Compose

Inicie toda a stack de microsserviços em segundo plano com build dos contêineres internos:
```bash
docker compose up -d --build
```

Verifique a integridade e os healthchecks de todos os serviços:
```bash
docker compose ps
```

Você verá os seguintes contêineres em execução:
- `dify_enterprise_nginx` (Gateway Nginx nas portas 80 e 443)
- `dify_enterprise_web` (Frontend Dify Next.js na porta 3000 interna)
- `dify_enterprise_api` (Motor Python do Dify na porta 5001 interna)
- `dify_enterprise_worker` (Processamento assíncrono Celery)
- `dify_enterprise_tools` (API FastAPI corporativa na porta 8080 interna)
- `dify_enterprise_qdrant` (Base Vetorial Qdrant v1.10.0 na porta 6333 interna)
- `dify_enterprise_sandbox` (Isolamento de execução RCE na porta 8194 interna, com cgroups limitados)
- `dify_enterprise_ssrf_proxy` (Proxy Squid de proteção anti-SSRF)
- `dify_enterprise_redis` (Broker Celery e Cache Redis 7)
- `dify_enterprise_db` (PostgreSQL 15)

---

## 3. Configuração Inicial do Dify

1. Acesse o painel pelo seu navegador em: `http://localhost` (ou `http://<IP_DO_SERVIDOR>`).
2. No primeiro acesso, defina a conta de Administrador da plataforma (E-mail e Senha).
3. No menu superior direito, vá em **Configurações (Settings) -> Provedores de Modelos (Model Providers)**:
   - Configure sua chave de API preferida (OpenAI, Anthropic, Google Gemini, Bedrock ou Groq).
   - Caso utilize modelos locais privados, adicione o provedor **Ollama** apontando para o seu IP da rede.

---

## 4. Carregando Documentos na Knowledge Base (Qdrant)

O módulo de Knowledge Base transforma documentos estáticos em conhecimento pesquisável por similaridade vetorial via Qdrant:

1. Clique na aba **Conhecimento (Knowledge)** no topo da página.
2. Clique no botão **Criar Conhecimento (Create Knowledge)**.
3. Arraste e solte o arquivo da empresa (exemplo: `Politica_de_Reembolso_2025.pdf`).
4. Selecione a estratégia de divisão de texto (Chunking):
   - **Segmentação Automática (Default)**: Pedaços de 500 a 800 tokens com overlap de 10% para manter coerência semântica.
   - **Modo de Limpeza de Texto**: Remove espaços em branco redundantes e formatações indesejadas.
5. Selecione o modelo de embeddings (ex: `text-embedding-3-small` da OpenAI ou modelo local via Ollama).
6. Clique em **Salvar e Processar (Save and Process)**. O contêiner `dify-worker` fará a leitura assíncrona e salvará os embeddings diretamente no Qdrant via `backend_net`.

---

## 5. Integrando a Ferramenta de ERP/RH no Dify (OpenAPI)

Para permitir que a IA consulte o saldo de férias e reembolsos diretamente no ERP:

1. No Dify, navegue até a aba **Ferramentas (Tools)** no topo da tela.
2. No menu lateral esquerdo, clique em **Personalizado (Custom)** e em seguida no botão **Criar Ferramenta Personalizada (Create Custom Tool)**.
3. Preencha as informações:
   - **Nome da Ferramenta**: `EnterpriseLegacyConnect`
   - **Esquema (Schema)**: Selecione **Importar a partir de URL** apontando para `http://nginx/tools/openapi.json` (ou copie o schema de `dify-enterprise-hub/openapi.json`).
4. No campo de **Autenticação (Auth)**:
   - Selecione **API Key**.
   - **Método**: `Bearer`
   - **Valor**: Insira a chave definida em `TOOLS_API_KEY` (por exemplo, `erp-enterprise-secure-token-2025`).
5. Clique em **Salvar**. A ferramenta disponibilizará 2 blocos de ação prontos:
   - `get_vacation_balance` (Consulta saldo de férias de funcionário)
   - `submit_reimbursement` (Registra solicitação de reembolso de despesa)

---

## 6. Criando o Assistente no Canvas Visual

1. Vá para a aba **Estúdio (Studio)** e clique em **Criar do Zero (Create from Blank)** -> Selecione **Chatflow / Workflow**.
2. No Canvas arrastável (Drag-and-Drop):
   - **Bloco de Início (Start Node)**: Recebe a mensagem do colaborador (ex: *"Quero saber quantos dias de férias tenho sobrando"*).
   - **Bloco de Conhecimento (Knowledge Retrieval)**: Conecte à base de conhecimento criada no passo 4.
   - **Bloco de Ferramenta (Tool Node)**: Arraste a ação `get_vacation_balance` da ferramenta `EnterpriseLegacyConnect`. Mapeie o parâmetro `employee_id` para a matrícula informada pelo usuário no formato `EMP-XXXX`.
   - **Bloco LLM**: Conecte o modelo selecionado com as diretrizes corporativas.
   - **Bloco de Resposta (Answer Node)**: Apresenta a resposta sintetizada com precisão e segurança.
3. Clique em **Depurar e Testar (Debug and Test)** para simular o atendimento em tempo real.
4. Quando satisfeito, clique em **Publicar (Publish)**.

---

## 7. Testes e Verificação de Conectividade

Para validar o microsserviço de ferramentas e as rotas de OpenAPI localmente:
```bash
# Rodar os testes automatizados da API
PYTHONPATH=dify-enterprise-hub:dify-enterprise-hub/tools_api python3 -m pytest dify-enterprise-hub/tests/ -v

# Gerar novamente as especificações OpenAPI caso adicione novos endpoints
PYTHONPATH=dify-enterprise-hub/tools_api python3 dify-enterprise-hub/scripts/export_openapi.py
```

Testar a consulta de férias via `curl`:
```bash
curl -X POST http://localhost/tools/api/v1/hr/vacation-balance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer erp-enterprise-secure-token-2025" \
  -d '{"employee_id": "EMP-10492"}'
```

Resposta esperada:
```json
{
  "employee_id": "EMP-10492",
  "employee_name": "Carlos Silva de Oliveira",
  "accrued_days": 22,
  "next_expiry_date": "2027-04-30",
  "can_schedule": true
}
```

---

## 8. Procedimentos de Backup e Disaster Recovery

### Executando Backup Consistente
```bash
./scripts/backup_db.sh
```
O script gera arquivos comprimidos no diretório `./backups/<TIMESTAMP>/`:
- `postgres_dify_<TIMESTAMP>.sql.gz`
- `qdrant_storage_<TIMESTAMP>.tar.gz`

### Restaurando a Base em Caso de Desastre
```bash
./scripts/restore_db.sh ./backups/<TIMESTAMP>/postgres_dify_<TIMESTAMP>.sql.gz
```

---

## 9. Troubleshooting e Resolução de Problemas

- **Acesso direto a bancos recusado na máquina host:** Com o isolamento Zero-Trust, portas como 5432, 6379, 6333 e 8194 ficam restritas à rede `backend_net`. Utilize `docker exec -it dify_enterprise_db psql -U dify -d dify_db` para inspeções administrativas.
- **Falha de autenticação na Custom Tool:** Certifique-se de selecionar o método `Bearer` no painel do Dify e passar o valor exato configurado em `TOOLS_API_KEY`.
- **Limites de CPU/Memória atingidos no Sandbox:** Se scripts Python complexos de agentes abortarem por falta de memória, altere as cotas em `dify-sandbox` no `docker-compose.yml` (`cpus` e `memory`).
