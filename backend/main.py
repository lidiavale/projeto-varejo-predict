import os
from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
from pydantic import BaseModel

app = FastAPI(title="API Varejo Predict")
client = bigquery.Client()

class PrevisaoRequest(BaseModel):
    dias_para_prever: int = 7

@app.post("/predict")
def gerar_previsao(request: PrevisaoRequest):
    try:
        
        query = f"""
            WITH 
            PrevEstoque AS (
              SELECT 
                forecast_timestamp as data, 
                forecast_value as qtd,
                prediction_interval_lower_bound as qtd_min,
                prediction_interval_upper_bound as qtd_max
              FROM ML.FORECAST(MODEL `varejo_analytics.modelo_previsao_vendas`, 
                               STRUCT({request.dias_para_prever} AS horizon, 0.8 AS confidence_level))
            ),
            PrevFinanceiro AS (
              SELECT 
                forecast_timestamp as data, 
                forecast_value as fat,
                prediction_interval_lower_bound as fat_min,
                prediction_interval_upper_bound as fat_max
              FROM ML.FORECAST(MODEL `varejo_analytics.modelo_previsao_faturamento`, 
                               STRUCT({request.dias_para_prever} AS horizon, 0.8 AS confidence_level))
            )
            SELECT 
              FORMAT_DATE('%Y-%m-%d', e.data) as data_futura,
              ROUND(e.qtd, 0) as qtd_prevista,
              ROUND(e.qtd_min, 0) as qtd_minima,
              ROUND(e.qtd_max, 0) as qtd_maxima,
              ROUND(f.fat, 2) as fat_previsto,
              ROUND(f.fat_min, 2) as fat_minimo,
              ROUND(f.fat_max, 2) as fat_maximo
            FROM PrevEstoque e
            JOIN PrevFinanceiro f ON e.data = f.data
            ORDER BY data_futura
        """
        
        query_job = client.query(query)
        results = []
        for row in query_job.result():
            results.append({
                "data": row.data_futura,
                "qtd_prevista": row.qtd_prevista,
                "qtd_min": row.qtd_minima,
                "qtd_max": row.qtd_maxima,
                "fat_previsto": row.fat_previsto,
                "fat_min": row.fat_minimo,
                "fat_max": row.fat_maximo
            })
            
        return {"horizonte_dias": request.dias_para_prever, "resultados": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
