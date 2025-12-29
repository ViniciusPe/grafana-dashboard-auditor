# 📊 Grafana Dashboard Auditor — Backend Documentation

Este backend audita dashboards do Grafana e coleta estatísticas de acesso, identificando painéis quebrados e dashboards inativos para análise de remoção.

---

## 🗂 Estrutura do Projeto

| Arquivo              | Responsabilidade principal                     |
| -------------------- | ---------------------------------------------- |
| `main.py`            | Declara a API e expõe endpoints                |
| `analyzer.py`        | Analisa dashboards e detecta erros estruturais |
| `access_audit.py`    | Identifica dashboards não acessados por X dias |
| `access_tracking.py` | Registra acessos e gera ranking de uso         |
| `removal_audit.py`   | Consolida dashboards candidatos à remoção      |
| `usage_analyzer.py`  | Gera relatórios por períodos de inatividade    |
| `db.py`              | Conexão com Postgres                           |
| `config.py`          | Variáveis de ambiente do Grafana e banco       |

---

## 🌐 Endpoints Disponíveis

### 1️⃣ Health Check

**Rota:**
`GET /health`

**O que faz:**
Verifica se a API está online.

**Implementado em:**
`main.py → health()`

**Retorno esperado:**

```json
{ "status": "ok" }
```

---

### 2️⃣ Configuração em uso

**Rota:**
`GET /config-check`

**O que faz:**
Exibe as variáveis essenciais carregadas do ambiente (`Grafana URL`, `Host do DB`, `Nome do DB`).

**Implementado em:**
`main.py → config_check()`

**Retorno esperado:**

```json
{
  "grafana_url": "http://grafana:3000",
  "db_host": "postgres",
  "db_name": "grafana"
}
```

---

### 3️⃣ Status do Grafana (simples)

**Rota:**
`GET /grafana-health`

**O que faz:**
Retorna o status básico de conectividade do Grafana configurado.

**Implementado em:**
`main.py → grafana_health_check()`

**Retorno esperado:**

```json
{
  "status": "ok",
  "grafana_url": "http://grafana:3000"
}
```

---

### 4️⃣ Auditar dashboards quebrados

**Rota:**
`GET /audit/broken-dashboards`

**O que faz:**
Lista dashboards que não carregam, não possuem datasource ou queries válidas.

**Implementado em:**
`analyzer.py → find_broken_dashboards()`

**Exemplo de retorno:**

```json
[
  {
    "uid": "ad4zgh9",
    "title": "quebradin",
    "reason": "Dashboard sem queries"
  }
]
```

---

### 5️⃣ Auditar dashboards não acessados recentemente

**Rota:**
`GET /audit/unused-dashboards?days={N}`

**O que faz:**
Busca dashboards que não foram acessados nos últimos `N` dias.

**Implementado em:**
`access_audit.py → dashboards_not_viewed(days)`

**Parâmetro:**
`days: int` (default = 30)

**Exemplo de retorno:**

```json
[
  {
    "uid": "ad9gbnp",
    "title": "Up",
    "access_count": 2,
    "last_access": "2025-09-24T18:42:18",
    "reason": "Not accessed in last 30 days"
  }
]
```

---

### 6️⃣ Registrar acesso a um dashboard (tracking interno)

**Rota:**
`POST /track/dashboard-access`

**O que faz:**
Registra no banco que um dashboard foi acessado (não integrado automaticamente ao Grafana ainda).

**Implementado em:**
`access_tracking.py → track_dashboard_access(uid)`

**Body JSON esperado:**

```json
{ "dashboard_uid": "UID_AQUI" }
```

**Retorno esperado:**

```json
{ "status": "ok" }
```

---

### 7️⃣ Ranking dos dashboards mais acessados no tracking interno

**Rota:**
`GET /audit/most-accessed-dashboards?limit={N}`

**O que faz:**
Gera ranking baseado nos acessos registrados no Postgres.

**Implementado em:**
`access_tracking.py → get_most_accessed(limit)`

**Parâmetro:**
`limit: int` (default = 10)

**Exemplo de retorno:**

```json
[
  {
    "uid": "teste-dashboard-1",
    "title": "teste-dashboard-1",
    "access_count": 5,
    "last_access": "2025-12-23T18:28:49",
    "reason": "Most accessed"
  }
]
```

---

### 8️⃣ Relatório de uso por períodos de inatividade

**Rota:**
`GET /docs/usage-report?periods=1,3,7,15,30`

**O que faz:**
Retorna dashboards que estão inativos comparando múltiplos períodos.

**Implementado em:**
`usage_analyzer.py → get_dashboards_by_usage(days_list)`

**Parâmetro:**
`periods: str` (lista separada por vírgula em dias)

**Exemplo de retorno:**

```json
[
  {
    "period_days": 1,
    "dashboards": [
      { "uid": "abc", "title": "Up", "access_count": 2, "reason": "Not accessed in last 1 days" }
    ]
  }
]
```

---

### 9️⃣ Consolida candidatos à remoção

**Rota:**
`GET /audit/removal-candidates?days={N}`

**O que faz:**

* Inclui **todos dashboards quebrados**
* Inclui dashboards **inativos por mais de 15 dias**
* Entrega apenas os dados para o analista decidir

**Implementado em:**
`removal_audit.py → get_all_removal_candidates(days)`

**Parâmetro:**
`days: int` (default = 15)

**Exemplo de retorno:**

```json
[
  {
    "uid": "ad4zgh9",
    "title": "quebradin",
    "reason": "Broken dashboard (Panel without queries)"
  },
  {
    "uid": "ad9gbnp",
    "title": "Up",
    "access_count": 2,
    "last_access": "2025-09-24T18:42:18",
    "reason": "Inactive for more than 15 days"
  }
]
```

---

## 🔧 Como validar a API localmente no Windows

No PowerShell ou CMD:

```powershell
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/config-check"
curl -X GET "http://localhost:8000/audit/broken-dashboards"
curl -X GET "http://localhost:8000/audit/unused-dashboards?days=7"
```

Registrar acesso manualmente:

```powershell
curl -X POST "http://localhost:8000/track/dashboard-access" `
  -H "Content-Type: application/json" `
  -d "{ \"dashboard_uid\": \"teste123\" }"
```

---

## 🧠 Observações importantes

* O `access_count` **não sobe automaticamente ainda** pois não há integração direta com eventos de acesso do Grafana.
* Atualmente o tracking é **backend-only** até o frontend e a integração serem implementados.
* Nenhum endpoint de remoção executa DELETE, apenas classifica e expõe dados.



# 📊 Grafana Dashboard Auditor — Setup do Banco de Dados & Integração do Plugin

Este documento descreve todas as ações necessárias no **PostgreSQL** para montar o laboratório e replicar a solução em outro ambiente, explicando a **necessidade de cada operação** para o funcionamento do plugin como um todo.

---

## 🧠 Contexto do Plugin

O auditor possui 3 pilares:

1. **Detecção de dashboards quebrados** → já funcional no backend (`/audit/broken-dashboards`)
2. **Coleta de estatísticas de uso** → tracking interno no Postgres (ainda sem integração direta com eventos da UI do Grafana)
3. **Classificação de candidatos a remoção** → consolida dashboards quebrados + inativos há mais de 15 dias (`/audit/removal-candidates`)

O frontend do plugin consumirá esses dados para exibir as 3 telas:

* Dashboards quebrados
* Relatório de uso (mais/menos acessados com range customizável)
* Candidatos à remoção (dados consolidados para análise do time)

---

## 🐘 Setup do PostgreSQL

### 1️⃣ Acessar o banco como admin

```bash
sudo -u postgres psql
```

**Por quê?**
É necessário entrar como usuário administrador do Postgres para criar schemas, roles e tabelas usadas pelo auditor.

---

### 2️⃣ Criar tabelas de auditoria

```sql
CREATE TABLE IF NOT EXISTS auditor_broken_dashboards (
    id SERIAL PRIMARY KEY,
    uid_dashboard TEXT NOT NULL,
    folder TEXT,
    error TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auditor_usage_stats (
    id SERIAL PRIMARY KEY,
    uid_dashboard TEXT NOT NULL,
    views BIGINT DEFAULT 0,
    last_viewed TIMESTAMP,
    calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auditor_removal_candidates (
    id SERIAL PRIMARY KEY,
    uid_dashboard TEXT NOT NULL,
    score_removal FLOAT DEFAULT 0,
    reason TEXT,
    suggested_at TIMESTAMP DEFAULT NOW()
);
```

**Por quê?**

| Tabela                       | Necessidade no Plugin                                                                  |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| `auditor_broken_dashboards`  | Armazena dashboards quebrados detectados pelo backend para exibição na 1ª tela         |
| `auditor_usage_stats`        | Guarda contagem de acessos internos para gerar ranking de uso e relatórios             |
| `auditor_removal_candidates` | Registra dashboards classificados como inativos e/ou problemáticos para análise humana |

Essas tabelas suportam a lógica do auditor sem executar remoções automáticas.

---

### 3️⃣ Criar role de acesso da aplicação

```sql
DO $$ BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'grafana_auditor') THEN
      CREATE ROLE grafana_auditor WITH LOGIN PASSWORD 'CHANGE_ME';
   END IF;
END $$;

GRANT USAGE ON SCHEMA public TO grafana_auditor;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO grafana_auditor;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO grafana_auditor;

\q
```

**Por quê?**
O backend em Python precisa de um usuário de banco para:

* **ler** dashboards quebrados e estatísticas
* **inserir** acessos manuais (tracking interno)
* **atualizar** timestamps de último acesso

Sem esse role e permissões, os endpoints do auditor não conseguem operar no Postgres.

---

### 4️⃣ Garantir que o PostgreSQL inicia corretamente

```bash
sudo systemctl enable postgresql
sudo systemctl restart postgresql
sudo -u postgres pg_isready
```

**Por quê?**

* `enable` → faz o serviço iniciar automaticamente após reboot
* `restart` → aplica alterações do schema/roles
* `pg_isready` → valida se o banco subiu e está aceitando conexões

Esses passos garantem que o banco esteja pronto para o backend do auditor.

---

## 🔌 Integração futura com acessos da UI do Grafana

> ⚠ Ainda não implementado: tracking automático de views via UI do Grafana.

A integração será feita **no frontend do plugin**, usando:

* `fetch()` ou `axios` para chamar `POST /track/dashboard-access`
* eventos de visualização da UI para disparar tracking real
* (sem necessidade de outro plugin ou backend separado)

O backend atual **já suporta receber o count**, mas o número **não sobe ainda automaticamente** pois não há coleta de eventos do Grafana integrada no frontend.

---

## 🧩 Conclusão

✔ O banco foi preparado para suportar **todas as 3 telas do plugin auditor**
✔ O backend já expõe **detecção de dashboards quebrados, relatórios de uso e candidatos a remoção**
✔ A integração automática de views será adicionada no **frontend do plugin** posteriormente, **sem necessidade de outro backend ou plugin separado**

---

## 👤 Autor

Vini Pess
SysAdmin / Backend Developer 🚀😎



---

## 👤 Autor

Vinicius Pessoa
Observability SRE

---

