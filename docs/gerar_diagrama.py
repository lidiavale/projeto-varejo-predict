from diagrams import Diagram, Cluster, Edge
from diagrams.gcp.analytics import BigQuery
from diagrams.gcp.compute import Functions, Run
from diagrams.gcp.devtools import Scheduler
from diagrams.gcp.storage import GCS
from diagrams.onprem.client import User
from diagrams.generic.network import Firewall

# Configuração do Diagrama
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white"
}

with Diagram("Arquitetura Varejo Predict", show=False, direction="LR", graph_attr=graph_attr):
    
    usuario = User("Gestor/Usuário")

    # Grupo de Ingestão
    with Cluster("Ingestão Automatizada"):
        gatilho = Scheduler("Cloud Scheduler\n(06:00 AM)")
        coleta = Functions("Cloud Functions\n(Coleta + API Feriados)")
    
    # Grupo de Dados
    with Cluster("Plataforma de Dados (Lakehouse)"):
        datalake = GCS("Cloud Storage\n(Raw JSON)")
        warehouse = BigQuery("BigQuery\n(Tabelas Externas + Gold)")
        ml_model = BigQuery("BigQuery ML\n(Modelo ARIMA)")

    # Grupo de Aplicação
    with Cluster("Aplicação Serverless"):
        frontend = Run("Frontend\n(Streamlit)")
        backend = Run("Backend API\n(FastAPI)")

    # Fluxo de Ingestão
    gatilho >> Edge(label="HTTP Trigger") >> coleta 
    coleta >> Edge(label="Salva JSON") >> datalake
    datalake >> Edge(label="Leitura Direta") >> warehouse
    warehouse - Edge(style="dotted") - ml_model # Conexão lógica

    # Fluxo do Usuário
    usuario >> Edge(label="Acessa Dashboard") >> frontend
    frontend >> Edge(label="POST /predict") >> backend
    backend >> Edge(label="SQL Query") >> ml_model
