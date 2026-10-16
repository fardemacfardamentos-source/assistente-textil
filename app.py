import streamlit as st
import pandas as pd
import urllib.parse

# Configuração da página com layout amplo
st.set_page_config(
    page_title="Gestão Têxtil | Atendimento & Orçamentos",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para deixar a interface moderna
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .whatsapp-btn {
        display: inline-block;
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧵 Gestão Têxtil — Painel do Atendente")
st.caption("Sistema integrado para controle de clientes, atendimentos, orçamentos e mensagens rápidas.")

# Upload do ficheiro
uploaded_file = st.sidebar.file_uploader("📂 Envie a planilha Excel (.xlsx)", type=["xlsx"])

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
            # Remove colunas inteiramente vazias
            df = df.dropna(how='all', axis=1)
            data[sheet] = df
        return data

    dfs = load_excel(uploaded_file)
    
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("📍 **Navegação**", ["📊 Visão Geral", "👥 Clientes", "📋 Atendimentos", "💰 Orçamentos", "💬 Modelos de Mensagens"])
    
    # ----------------------------------------------------
    # 1. VISÃO GERAL
    # ----------------------------------------------------
    if menu == "📊 Visão Geral":
        st.subheader("📊 Resumo das Operações")
        
        df_cli = dfs.get("CLIENTES", pd.DataFrame())
        df_atend = dfs.get("ATENDIMENTOS", pd.DataFrame())
        df_orc = dfs.get("ORÇAMENTOS", pd.DataFrame())
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("👤 Clientes Cadastrados", len(df_cli.dropna(subset=[df_cli.columns[0]])) if not df_cli.empty else 0)
        with c2:
            st.metric("📞 Atendimentos Abertos", len(df_atend.dropna(subset=[df_atend.columns[0]])) if not df_atend.empty else 0)
        with c3:
            st.metric("📑 Orçamentos Gerados", len(df_orc.dropna(subset=[df_orc.columns[0]])) if not df_orc.empty else 0)
            
        st.markdown("---")
        st.info("💡 **Instruções Rápida:** Utilize o menu lateral para gerenciar cada etapa da sua produção e atendimento.")

    # ----------------------------------------------------
    # 2. CLIENTES
    # ----------------------------------------------------
    elif menu == "👥 Clientes":
        st.subheader("👥 Gestão de Clientes")
        df_cli = dfs.get("CLIENTES", pd.DataFrame())
        
        tab1, tab2 = st.tabs(["🔍 Consultar Clientes", "➕ Novo Cliente"])
        
        with tab1:
            busca = st.text_input("🔎 Buscar cliente por Nome ou Organização:")
            if busca and not df_cli.empty:
                col_nome = df_cli.columns[1] if len(df_cli.columns) > 1 else df_cli.columns[0]
                df_filtrado = df_cli[df_cli[col_nome].astype(str).str.contains(busca, case=False, na=False)]
                st.dataframe(df_filtrado, use_container_width=True)
            else:
                st.dataframe(df_cli, use_container_width=True)
                
        with tab2:
            st.markdown("#### Formulario de Cadastro")
            with st.form("form_novo_cliente"):
                col_a, col_b = st.columns(2)
                with col_a:
                    nome = st.text_input("Nome / Organização *")
                    whatsapp = st.text_input("WhatsApp (ex: 5575999999999) *")
                    email = st.text_input("E-mail")
                with col_b:
                    cidade = st.text_input("Cidade/UF")
                    tipo = st.selectbox("Tipo de Cliente", ["Pessoa física", "Empresa", "Paróquia / Igreja", "Grupo / Organização"])
                    obs = st.text_area("Observações")
                
                if st.form_submit_button("💾 Salvar Cadastro"):
                    st.success(f"Cliente **{nome}** cadastrado com sucesso no fluxo!")

    # ----------------------------------------------------
    # 3. ATENDIMENTOS
    # ----------------------------------------------------
    elif menu == "📋 Atendimentos":
        st.subheader("📋 Controle de Atendimentos")
        df_atend = dfs.get("ATENDIMENTOS", pd.DataFrame())
        
        tab1, tab2 = st.tabs(["📄 Lista de Atendimentos", "🚀 Gerar Atendimento & WhatsApp"])
        
        with tab1:
            st.dataframe(df_atend, use_container_width=True)
            
        with tab2:
            with st.form("form_novo_atendimento"):
                col1, col2 = st.columns(2)
                with col1:
                    cliente = st.text_input("Cliente / Organização")
                    whatsapp = st.text_input("WhatsApp (DDI + DDD + número)")
                    segmento = st.selectbox("Segmento", ["Fardamento profissional", "Camisa para festa religiosa", "Uniforme escolar", "Evento", "Outro"])
                with col2:
                    qtd = st.number_input("Quantidade de Peças", min_value=1, value=10)
                    material = st.text_input("Material / Malha / Tecido")
                    prazo = st.text_input("Prazo do Cliente / Data do Evento")
                
                detalhes = st.text_area("Detalhes do Pedido / Observações")
                
                if st.form_submit_button("📱 Gerar Link para WhatsApp"):
                    msg = f"Olá {cliente}! Recebi seu contato para o segmento {segmento} ({qtd} peças em {material}). Podemos alinhar os detalhes?"
                    link = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(msg)}"
                    
                    st.success("Atendimento registrado!")
                    if whatsapp:
                        st.markdown(f'<a href="{link}" target="_blank" class="whatsapp-btn">💬 Abrir WhatsApp de {cliente}</a>', unsafe_allow_html=True)

    # ----------------------------------------------------
    # 4. ORÇAMENTOS
    # ----------------------------------------------------
    elif menu == "💰 Orçamentos":
        st.subheader("💰 Tabela de Orçamentos")
        df_orc = dfs.get("ORÇAMENTOS", pd.DataFrame())
        st.dataframe(df_orc, use_container_width=True)

    # ----------------------------------------------------
    # 5. MODELOS DE MENSAGENS
    # ----------------------------------------------------
    elif menu == "💬 Modelos de Mensagens":
        st.subheader("💬 Modelos Prontos para Atendimento no WhatsApp")
        df_msg = dfs.get("MENSAGENS", pd.DataFrame())
        
        if not df_msg.empty:
            for idx, row in df_msg.iterrows():
                etapa = row.get(df_msg.columns[0], "Mensagem")
                quando = row.get(df_msg.columns[1], "")
                msg = row.get(df_msg.columns[2], "")
                
                if pd.notna(etapa) and str(etapa).strip() != "":
                    with st.expander(f"📌 **{etapa}** — *({quando})*"):
                        st.write(msg)
                        st.code(msg, language="text")

else:
    st.info("👈 **Para começar:** Faça o upload da sua planilha Excel (`Assistente_Atendimento_Textil_Fluxo_Atualizado.xlsx`) no menu à esquerda.")
