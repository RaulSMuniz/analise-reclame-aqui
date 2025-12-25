import streamlit as st
import pandas as pd
from scraper import capturar_dados_dashboard
from transform import transform_data

st.set_page_config(
    page_title="Análise do Reclame Aqui",
    page_icon="📊",
    layout="wide"
)

if "dados_coletados" not in st.session_state:
    st.session_state.dados_coletados = None

with st.sidebar:
    st.title("Análise de Empresas no Reclame Aqui")
    st.markdown("---")
    
    empresa_input = st.text_input(
        "Nome da Empresa (URL):", 
        placeholder="ex: kabum, amazon, magazineluiza"
    )
    
    botao_analisar = st.button("🚀 Iniciar Análise")
    
    if st.session_state.dados_coletados:
        st.markdown("---")
        if st.button("🗑️ Limpar Resultados"):
            st.session_state.dados_coletados = None
            st.rerun()

if botao_analisar:
    if empresa_input:
        try:
            with st.status("Extraindo informações...", expanded=True) as status:
                st.write("🕵️ Acessando Reclame Aqui...")
                capturar_dados_dashboard(empresa_input)

                st.write("🧹 Limpando dados...")
                dados_limpos = transform_data(empresa_input)
                
                status.update(label="Processamento Concluído!", state="complete", expanded=False)

            st.session_state.dados_coletados = dados_limpos
            st.rerun()
            
        except Exception as e:
            st.error(f"Erro na execução: {e}")
    else:
        st.warning("⚠️ Digite o nome da empresa na barra lateral.")

if st.session_state.dados_coletados:
    d = st.session_state.dados_coletados

    st.header(f"📊 Relatório de Performance: {d['empresa'].upper()}")
    
    # Métricas / KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nota Geral", f"{d['nota_media']}/10")
    col2.metric("Total de Queixas", int(d['total_reclamacoes']))
    
    # Calculando um dado novo: % de Reclamações não resolvidas
    nao_resolvidas_pct = round(100 - d['indice_solucao'], 1)
    col3.metric("Falta Resolver", f"{nao_resolvidas_pct}%", delta="Pendentes", delta_color="inverse")

    st.divider()

    # Gráficos
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Eficiência")

        df_gap = pd.DataFrame({
            "Etapa": ["Respondidas", "Resolvidas"],
            "Percentual": [d['respondidas'], d['indice_solucao']]
        })
        st.bar_chart(data=df_gap, x="Etapa", y="Percentual", color="#29b5e8")

    with c2:
        st.subheader("Fidelização")

        confianca_data = pd.DataFrame({
            "Categoria": ["Voltaram a Negociar", "Média do Mercado (Ref)"],
            "Valor": [d['voltaram_negociar'], 70]
        })
        st.area_chart(data=confianca_data, x="Categoria", y="Valor")
        
        if d['voltaram_negociar'] > 80:
            st.success("✅ Alta Retenção: A empresa possui clientes leais.")
        elif d['voltaram_negociar'] > 60:
            st.warning("⚠️ Retenção Moderada: Atenção ao pós-venda.")
        else:
            st.error("🚨 Baixa Retenção: Risco crítico de perda de clientes.")

    # Status de Reclamações
    st.divider()
    st.subheader("📑 Status Atual de Reclamações")
    
    progresso_resposta = d['respondidas'] / 100
    st.write(f"Taxa de resposta atual: **{d['respondidas']}%**")
    st.progress(progresso_resposta)
    st.write(f"Existem **{int(d['aguardando'])}** pessoas esperando uma resposta neste momento.")
    st.info(f"⏱️ **Tempo de Resposta:** \n\n {d['tempo_resposta']}")
    st.divider()
    