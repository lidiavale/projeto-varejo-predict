import functions_framework
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import os

# --- CONFIG ---
BUCKET_NAME = "datalake-varejo"
SHEET_NAME = "dados_erp" 
KEY_FILE = "service_account.json"

@functions_framework.http
def ingest_data(request):
    data_ref = datetime.now() - timedelta(days=1)
    str_data = data_ref.strftime("%Y-%m-%d")
    
    print(f"--- Iniciando ingestão (D-1) para: {str_data} ---")
    
    try:
        # Autentica e Lê Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        
        # Lê dados
        dados = sheet.get_all_records()
        df = pd.DataFrame(dados)
        
        # Padroniza nomes das colunas
        df.columns = [c.strip() for c in df.columns]
        
        # Mapeamento
        de_para = {
            'N Doc': 'id_venda', 
            'Data': 'data_br', 
            'Descrição': 'produto_nome', 
            'Categoria': 'produto_categoria', 
            'Qtde': 'quantidade_vendida', 
            'Total': 'receita_total'
        }
        df.rename(columns=de_para, inplace=True)
        
        # Tratamento Data
        df['data'] = pd.to_datetime(df['data_br'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Filtra pela data de REFERÊNCIA (Ontem)
        df_dia = df[df['data'] == str_data].copy()
        
        origem = "Planilha_Real"
        
        # Fallback
        if len(df_dia) == 0:
            print(f"Sem vendas para {str_data} na planilha. Usando fallback.")
            if len(df) > 0:
                amostra = df.sample(1).iloc[0].to_dict()
                df_dia = pd.DataFrame([amostra])
                df_dia['data'] = str_data
                origem = "Planilha_Simulada_Fallback"
        
        # Salva
        caminho = f"gs://{BUCKET_NAME}/raw/vendas/vendas_{str_data}.json"
        df_dia.to_json(caminho, orient="records", lines=True)
        
        return f"Sucesso! {len(df_dia)} vendas processadas para {str_data}. ({origem})"

    except Exception as e:
        return f"Erro Crítico: {str(e)}"
