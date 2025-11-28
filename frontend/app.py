import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Varejo Analytics AI", layout="wide")
API_URL = "https://api-previsao-varejo-484353111974.us-central1.run.app/predict"

st.title("🛍️ Varejo Analytics: Previsão de Demanda & Receita")
st.markdown("---")

with st.sidebar:
    st.header("Parâmetros")
    dias = st.slider("Horizonte (Dias)", 7, 90, 30)
    st.info("Sistema utilizando **Multi-Model AI** (ARIMA Plus) para prever Estoque e Fluxo de Caixa simultaneamente.")

if st.button("Gerar Previsões", type="primary"):
    with st.spinner('Processando modelos de IA...'):
        try:
            response = requests.post(API_URL, json={"dias_para_prever": dias})
            
            if response.status_code == 200:
                data = response.json()['resultados']
                df = pd.DataFrame(data)
                
                # ABAS PARA SEPARAR OS TEMAS
                tab1, tab2 = st.tabs(["📦 Previsão de Estoque (Qtd)", "💰 Previsão Financeira (R$)"])
                
                # --- ABA 1: ESTOQUE ---
                with tab1:
                    total_qtd = df['qtd_prevista'].sum()
                    col1, col2 = st.columns(2)
                    col1.metric("Volume Total Previsto", f"{int(total_qtd):,} un".replace(",", "."))
                    col2.metric("Média Diária", f"{int(df['qtd_prevista'].mean()):,} un".replace(",", "."))
                    
                    fig_qtd = px.line(df, x='data', y='qtd_prevista', title="Demanda Física (Unidades)", markers=True)
                    fig_qtd.add_scatter(x=df['data'], y=df['qtd_max'], mode='lines', line=dict(width=0), showlegend=False)
                    fig_qtd.add_scatter(x=df['data'], y=df['qtd_min'], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(0,100,255,0.1)', showlegend=False, name='Intervalo')
                    st.plotly_chart(fig_qtd, use_container_width=True)

                # --- ABA 2: FINANCEIRO ---
                with tab2:
                    total_fat = df['fat_previsto'].sum()
                    colA, colB = st.columns(2)
                    colA.metric("Faturamento Previsto", f"R$ {total_fat:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    colB.metric("Ticket Médio Esperado", f"R$ {total_fat/total_qtd:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    fig_fat = px.line(df, x='data', y='fat_previsto', title="Projeção de Caixa (R$)", markers=True, color_discrete_sequence=['green'])
                    fig_fat.add_scatter(x=df['data'], y=df['fat_max'], mode='lines', line=dict(width=0), showlegend=False)
                    fig_fat.add_scatter(x=df['data'], y=df['fat_min'], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(0,255,100,0.1)', showlegend=False)
                    st.plotly_chart(fig_fat, use_container_width=True)

            else:
                st.error("Erro na API.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
