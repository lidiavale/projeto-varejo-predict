import pandas as pd
import os

# CONFIGURAÇÃO
BUCKET_NAME = "datalake-varejo" 
NOME_ARQUIVO_LOCAL = "dados_vendas.csv"

def preparar_dados():
    print("--- Processando Arquivo e Filtrando Colunas ---")
    
    # 1. Leitura
    if NOME_ARQUIVO_LOCAL.endswith('.xlsx'):
        df = pd.read_excel(NOME_ARQUIVO_LOCAL)
    else:
        try:
            df = pd.read_csv(NOME_ARQUIVO_LOCAL, sep=';', encoding='latin1')
        except:
            df = pd.read_csv(NOME_ARQUIVO_LOCAL, sep=',', encoding='utf-8')

    # 2. Renomear (Padronização)
    df.columns = [c.strip() for c in df.columns] # Remove espaços extras
    
    de_para = {
        'N Doc': 'id_venda',
        'Data': 'data',
        'Descrição': 'produto_nome',
        'Categoria': 'produto_categoria',
        'Qtde': 'quantidade_vendida',
        'Total': 'receita_total'
    }
    
    # Renomeia o que encontrar
    df = df.rename(columns=de_para)

    # 3. Tratamento
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
    df = df.dropna(subset=['data'])
    
    # Números
    def limpar_numero(val):
        if isinstance(val, str):
            val = val.replace('.', '').replace(',', '.')
        return float(val)

    if 'receita_total' in df.columns: df['receita_total'] = df['receita_total'].apply(limpar_numero)
    if 'quantidade_vendida' in df.columns: df['quantidade_vendida'] = df['quantidade_vendida'].apply(limpar_numero)
    if 'produto_categoria' not in df.columns: df['produto_categoria'] = 'Geral'
    else: df['produto_categoria'] = df['produto_categoria'].fillna('Geral')

    
    colunas_finais = ['id_venda', 'data', 'produto_nome', 'produto_categoria', 'quantidade_vendida', 'receita_total']
    
    
    for col in colunas_finais:
        if col not in df.columns:
            df[col] = None
            
    df_limpo = df[colunas_finais] 

    print(f"Colunas Finais: {list(df_limpo.columns)}")
    
    # 4. Salva e Envia
    df_limpo.to_csv("erp_master.csv", index=False)
    os.system(f"gsutil cp erp_master.csv gs://{BUCKET_NAME}/source/erp_master.csv")
    print("Sucesso! Arquivo limpo enviado.")

if __name__ == "__main__":
    preparar_dados()
