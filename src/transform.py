import json
import os
import re
import pandas as pd
import glob
from datetime import datetime

def transform_data(empresa):
    buscar = f'data/bronze/dashboard_{empresa}_*.json'
    arquivos = glob.glob(buscar)

    if not arquivos:
        return f"Erro: nenhum arquivo encontrado."
    
    transformar = max(arquivos, key=os.path.getmtime)

    with open(transformar, 'r', encoding='utf8') as f:
        dados_brutos = json.load(f)
    
    dados_limpos = {
        "empresa": dados_brutos["empresa"],
        "data_coleta": dados_brutos["data_coleta"]
    }

    def limpar_dados(texto, chave=""):
        if texto == 'N/A': return 0.0

        if "Nota Média" in chave:
            busca = re.findall(r"(\d+\.\d+)", texto)
            if busca:
                return float(busca[0])
            else:
                busca_inteira = re.findall(r"(\d+)\/10", texto)
                return float(busca_inteira[0]) if busca_inteira else 0.0
        busca = re.findall(r"(\d+\.?\d*)", texto)
        return float(busca[0]) if busca else 0.0
    
    dados_limpos["total_reclamacoes"] = int(limpar_dados(dados_brutos["Total Reclamações"]))
    dados_limpos["nota_media"] = limpar_dados(dados_brutos["Nota Média"], chave="Nota Média")
    dados_limpos["indice_solucao"] = limpar_dados(dados_brutos["Índice de Solução"])
    dados_limpos["respondidas"] = limpar_dados(dados_brutos["Respondidas"])
    dados_limpos["voltaram_negociar"] = limpar_dados(dados_brutos["Voltariam a Negociar"])
    dados_limpos["aguardando"] = limpar_dados(dados_brutos["Aguardando"])
    dados_limpos["tempo_resposta"] = dados_brutos["Tempo Médio"]

    if not os.path.exists('data/silver'):
        os.makedirs('data/silver')

    df = pd.DataFrame([dados_limpos])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_saida = f'data/silver/dashboard_{empresa}_{timestamp}.csv'

    df.to_csv(caminho_saida, index=False, encoding='utf8')

    return dados_limpos