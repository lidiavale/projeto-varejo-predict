from diagrams import Diagram, Cluster, Edge
from diagrams.gcp.analytics import BigQuery
from diagrams.gcp.compute import Functions, Run
from diagrams.gcp.devtools import Scheduler
from diagrams.gcp.storage import GCS
from diagrams.onprem.client import User
from diagrams.saas.filesharing import Drive # Representando o Google Sheets

# Configuração Visual
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.5"
}

with Diagram("Arquitetura Varejo Predict (Final)", show=False, direction="LR", graph_attr=graph_attr):
    
    # Atores
    gestor = User("Gestor/Usuário")
    lojista = User("Lojista\n(Input Manual)")
    
    # Grupo de Ingestão
    with Cluster("Ingestão Híbrida"):
        planilha = Drive("Google Sheets\n(Vendas Diárias)")
        gatilho = Scheduler("Cloud Scheduler\n(Trigger 06:00)")
        coleta = Functions("Cloud Function\n(Coletor Python)")
        
    # Grupo de Dados
    with Cluster("Lakehouse (Storage + BQ)"):
        datalake = GCS("Cloud Storage\n(Raw JSONL)")
        dw = BigQuery("BigQuery\n(Tabelas Gold)")
        
        with Cluster("Múltiplos Modelos IA"):
            ml_qtd = BigQuery("ARIMA\n(Estoque/Qtd)")
            ml_fin = BigQuery("ARIMA\n(Financeiro/R$)")

    # Grupo de Aplicação
    with Cluster("Aplicação Serverless"):
        frontend = Run("Frontend\n(Streamlit com Abas)")
        backend = Run("Backend API\n(FastAPI)")

    # Fluxo de Ingestão
    lojista >> Edge(label="Preenche") >> planilha
    gatilho >> Edge(label="Aciona") >> coleta
    planilha >> Edge(label="Leitura via API") >> coleta
    coleta >> Edge(label="Salva JSON") >> datalake
    
    # Fluxo de Dados
    datalake >> Edge(label="External Table") >> dw
    dw - Edge(style="dotted") - ml_qtd
    dw - Edge(style="dotted") - ml_fin

    # Fluxo do Usuário
    gestor >> Edge(label="HTTPS") >> frontend
    frontend >> Edge(label="POST /predict") >> backend
    backend >> Edge(label="Query Dupla") >> ml_qtd
    backend >> Edge(label="Query Dupla") >> ml_fin
