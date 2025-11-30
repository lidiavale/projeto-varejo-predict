# 🛍️ Varejo PredictAI: Previsão de Demanda com BigQuery ML

Este projeto implementa uma arquitetura completa de **Lakehouse Híbrido** e **MLOps** no Google Cloud Platform (GCP) para prever a demanda de vendas de um varejo alimentício real. 

A solução resolve o problema da fragmentação de dados integrando o **legado** (histórico em CSV) com a **operação diária** (lançamentos em Google Sheets), utilizando o BigQuery ML para treinar modelos de série temporal (ARIMA_PLUS) focados em Logística e Finanças.

## 🏗️ Arquitetura da Solução

A solução segue o fluxo **Ingestão Híbrida -> Processamento ELT -> Multi-Model AI -> Aplicação**.

![Arquitetura da Solução](docs/arquitetura_varejo_predict_(final).png)

### Componentes:
1.  **Ingestão (Cloud Functions + Scheduler):** Script Python agendado (06:00 AM) que se conecta à API do **Google Sheets** para coletar as vendas do dia anterior lançadas pelo lojista, garantindo integração com a operação real.
2.  **Armazenamento (Cloud Storage):** Camada *Raw* para armazenamento de arquivos brutos (JSONL), unificando o histórico (Backfill via CSV) com a carga diária.
3.  **Data Warehouse (BigQuery):**
    * **Tabelas Externas:** Virtualização dos dados do Storage.
    * **Camada Gold:** Agregação de vendas por categoria e data via SQL.
    * **Machine Learning:** Estratégia **Multi-Model** com dois modelos `ARIMA_PLUS` treinados nativamente no banco:
        * 🧠 **Modelo de Estoque:** Previsão de quantidade física (unidades).
        * 💰 **Modelo Financeiro:** Previsão de faturamento (R$).
4.  **Backend (FastAPI + Cloud Run):** API REST que orquestra a consulta aos dois modelos e consolida os resultados.
5.  **Frontend (Streamlit + Cloud Run):** Dashboard interativo com abas para visualização de Estoque e Fluxo de Caixa.

## 🛠️ Tecnologias Utilizadas

* **Cloud:** Google Cloud Platform (GCP)
* **Linguagem:** Python 3.10
* **Frameworks:** FastAPI, Streamlit, Pandas, Plotly
* **Integração:** GSpread (Google Sheets API), OAuth2
* **Infraestrutura:** Cloud Run (Serverless), Cloud Functions (2nd Gen), BigQuery, Cloud Storage
* **IA/ML:** BigQuery ML (Time Series Forecasting)

## 📂 Estrutura do Repositório

* `/ingestao`: Código da Cloud Function (Coleta Google Sheets).
* `/backend`: API desenvolvida em FastAPI (Query Dupla).
* `/frontend`: Dashboard desenvolvido em Streamlit (Com Abas).
* `/scripts`: Scripts de preparação de dados (Backfill e Limpeza).
* `/docs`: Diagramas e documentação da arquitetura.

---
*Projeto desenvolvido como requisito da disciplina de Processamento de Dados Massivos.*
