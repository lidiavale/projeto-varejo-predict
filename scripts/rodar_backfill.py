import pandas as pd
import os

BUCKET_NAME = "datalake-varejo"

def backfill():
    print("Lendo Mestre...")
    df = pd.read_csv(f"gs://{BUCKET_NAME}/source/erp_master.csv")
    
    dias = df['data'].unique()
    print(f"Gerando arquivos para {len(dias)} dias...")
    
    for data in dias:
        df_dia = df[df['data'] == data]
        caminho = f"gs://{BUCKET_NAME}/raw/vendas/vendas_{data}.json"
        df_dia.to_json(caminho, orient="records", lines=True)
        
    print("Backfill Finalizado!")

if __name__ == "__main__":
    backfill()
