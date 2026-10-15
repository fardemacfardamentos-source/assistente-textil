import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Assistente de Atendimento Têxtil", page_icon="🧵", layout="wide")

st.title("🧵 Painel Têxtil - Assistente de Atendimento")
st.markdown("Gerencie clientes, atendimentos, orçamentos e mensagens para WhatsApp de forma simples e integrada.")

uploaded_file = st.file_uploader("Envie a sua planilha Excel atualizada (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    @st.cache_data
    def load_excel(file):
        xls = pd.ExcelFile(file)
        data = {}
        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet, header=3)
                if df.empty or len(df.columns) < 2:
                    df = pd.read_excel(xls, sheet_name=sheet, header=0)
            except:
                df = pd.read_excel(xls, sheet_name=sheet, header=0)
            data[sheet] = df
        return xls, data

    xls, dfs = load_excel(uploaded_file)
    
    menu = st.sidebar.selectbox("Navegação", ["Painel / Início", "Clientes", "Atendimentos", "Orçamentos", "Modelos de Mensagens (WhatsApp)"])
    
    if menu == "Painel / Início":
        st.header("📊 Painel de Acompanhamento")
        
        col1, col2, col3 = st.columns(3)
        
        df_cli = dfs.get("CLIENTES", pd.DataFrame())
        df_atend = dfs.get("ATENDIMENTOS", pd.DataFrame())
        df_orc = dfs.get("ORÇAMENTOS", pd.DataFrame())
        
        with col1:
            st.metric("Clientes Cadastrados", len(df_cli.dropna(subset=[df_cli.columns[0]])))
        with col2:
            st.metric("Atendimentos Registrados", len(df_atend.dropna(subset=[df_atend.columns[0]])))
        with col3:
            st.metric("Orçamentos Gerados", len(df_orc.dropna(subset=[df_orc.columns[0]])))
            
        st.markdown("---")
        st.info("💡 **Dica:** Utilize o menu lateral para navegar entre as abas e gerenciar o seu fluxo comercial.")

    elif menu == "Clientes":
        st.header("👥 Cadastro de Clientes")
        df_cli = dfs.get("CLIENTES", pd.DataFrame())
        st.dataframe(df_cli, use_container_width=True)

    elif menu == "Atendimentos":
        st.header("📋 Registro de Atendimentos | Fluxo Comercial")
        df_atend = dfs.get("ATENDIMENTOS", pd.DataFrame())
        st.dataframe(df_atend, use_container_width=True)
        
        with st.expander("➕ Gerar Link Rápido de WhatsApp"):
            with st.form("form_atendimento"):
                segmento = st.selectbox("Segmento", ["Fardamento profissional", "Camisa para festa religiosa", "Uniforme escolar", "Evento", "Outro"])
                qtd = st.number_input("Quantidade de peças", min_value=1, value=10)
                material = st.text_input("Material / Malha / Tecido")
                whatsapp = st.text_input("WhatsApp do Cliente (apenas dígitos, ex: 5575...)")
                
                submit_atend = st.form_submit_button("Gerar Link WhatsApp")
                if submit_atend:
                    msg = f"Olá! Recebi a sua solicitação para {segmento}. Para a quantidade de {qtd} peças em {material}, precisamos alinhar os detalhes..."
                    link = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(msg)}"
                    if whatsapp:
                        st.markdown(f"📱 **[Clique aqui para abrir o WhatsApp do cliente]({link})**")

    elif menu == "Orçamentos":
        st.header("💰 Gerador de Orçamentos")
        df_orc = dfs.get("ORÇAMENTOS", pd.DataFrame())
        st.dataframe(df_orc, use_container_width=True)

    elif menu == "Modelos de Mensagens (WhatsApp)":
        st.header("💬 Modelos de Mensagens para Atendimento")
        df_msg = dfs.get("MENSAGENS", pd.DataFrame())
        if not df_msg.empty:
            for idx, row in df_msg.iterrows():
                etapa = row.get(df_msg.columns[0], "")
                quando = row.get(df_msg.columns[1], "")
                msg = row.get(df_msg.columns[2], "")
                if pd.notna(etapa) and str(etapa).strip() != "":
                    with st.expander(f"📌 {etapa} ({quando})"):
                        st.write(msg)
else:
    st.info("👈 Por favor, faça o carregamento do seu ficheiro Excel (`Assistente_Atendimento_Textil_Fluxo_Atualizado.xlsx`) usando o botão ao lado para iniciar o painel.")
