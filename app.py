import streamlit as st
import pandas as pd
import urllib.parse

# Configuração da página
st.set_page_config(
    page_title="Gestão Têxtil | Atendimento & Contatos",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .whatsapp-btn {
        display: inline-block;
        background-color: #25D366;
        color: white !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        margin: 5px 0;
    }
    .gcal-btn {
        display: inline-block;
        background-color: #4285F4;
        color: white !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧵 Gestão Têxtil — Painel Integrado")
st.caption("Controle de clientes, atalhos para WhatsApp, Google Agenda e exportação para Google Contatos.")

# Carregamento do ficheiro Excel
uploaded_file = st.sidebar.file_uploader("📂 Envie a sua planilha Excel (.xlsx)", type=["xlsx"])

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
            df = df.dropna(how='all', axis=1)
            data[sheet] = df
        return data

    dfs = load_excel(uploaded_file)
    
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("📍 **Navegação**", ["📊 Visão Geral", "👥 Clientes & Google Contatos", "📋 Atendimentos", "📅 Google Agenda", "💰 Orçamentos", "💬 Mensagens"])
    
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
        st.info("💡 **Dica:** Na aba de Clientes, pode gerar cartões de contacto prontos a importar para o Google Contatos.")

    # ----------------------------------------------------
    # 2. CLIENTES & GOOGLE CONTATOS
    # ----------------------------------------------------
    elif menu == "👥 Clientes & Google Contatos":
        st.subheader("👥 Gestão de Clientes e Integração com Google Contatos")
        df_cli = dfs.get("CLIENTES", pd.DataFrame())
        
        tab1, tab2 = st.tabs(["🔍 Consultar & Gerar Contactos vCard", "➕ Novo Cliente"])
        
        with tab1:
            busca = st.text_input("🔎 Buscar cliente por Nome ou Organização:")
            if busca and not df_cli.empty:
                col_nome = df_cli.columns[1] if len(df_cli.columns) > 1 else df_cli.columns[0]
                df_filtrado = df_cli[df_cli[col_nome].astype(str).str.contains(busca, case=False, na=False)]
                st.dataframe(df_filtrado, use_container_width=True)
            else:
                st.dataframe(df_cli, use_container_width=True)
                
            st.markdown("---")
            st.markdown("### 📇 Gerar Cartão de Contacto (Google Contatos)")
            st.markdown("Insira os dados abaixo para gerar um ficheiro `.vcf` compatível com o Google Contatos:")
            
            with st.form("form_vcard"):
                c_nome = st.text_input("Nome Completo / Organização")
                c_tel = st.text_input("Telemóvel / WhatsApp (com DDI, ex: +5575999999999)")
                c_email = st.text_input("E-mail do Cliente")
                c_org = st.text_input("Empresa / Segmento Têxtil")
                
                if st.form_submit_button("Gerar Ficheiro para Google Contatos"):
                    vcard_texto = f"""BEGIN:VCARD
VERSION:3.0
FN:{c_nome}
ORG:{c_org}
TEL;TYPE=CELL:{c_tel}
EMAIL:{c_email}
END:VCARD"""
                    
                    st.success("Cartão gerado com sucesso!")
                    st.download_button(
                        label="📥 Descarregar Contacto (.vcf)",
                        data=vcard_texto,
                        file_name=f"{c_nome.replace(' ', '_')}.vcf",
                        mime="text/vcard"
                    )

        with tab2:
            with st.form("form_novo_cliente"):
                col_a, col_b = st.columns(2)
                with col_a:
                    nome = st.text_input("Nome / Organização *")
                    whatsapp = st.text_input("WhatsApp (ex: 5575999999999) *")
                with col_b:
                    cidade = st.text_input("Cidade/UF")
                    tipo = st.selectbox("Tipo de Cliente", ["Pessoa física", "Empresa", "Paróquia / Igreja", "Grupo"])
                if st.form_submit_button("💾 Salvar Cadastro"):
                    st.success(f"Cliente **{nome}** simulado com sucesso!")

    # ----------------------------------------------------
    # 3. ATENDIMENTOS
    # ----------------------------------------------------
    elif menu == "📋 Atendimentos":
        st.subheader("📋 Controle de Atendimentos & Ações Rápidas")
        df_atend = dfs.get("ATENDIMENTOS", pd.DataFrame())
        
        tab1, tab2 = st.tabs(["📄 Lista de Atendimentos", "🚀 Criar Atendimento & Ações"])
        
        with tab1:
            st.dataframe(df_atend, use_container_width=True)
            
        with tab2:
            with st.form("form_novo_atendimento"):
                col1, col2 = st.columns(2)
                with col1:
                    cliente = st.text_input("Cliente / Organização")
                    whatsapp = st.text_input("WhatsApp (DDI + DDD + número)")
                    segmento = st.selectbox("Segmento", ["Fardamento profissional", "Camisa festa religiosa", "Uniforme escolar", "Evento", "Outro"])
                with col2:
                    qtd = st.number_input("Quantidade de Peças", min_value=1, value=10)
                    material = st.text_input("Material / Malha / Tecido")
                    prazo_evento = st.text_input("Data Limite / Evento (Ex: 2026-06-15)")
                
                if st.form_submit_button("Gerar Links de Ação"):
                    msg = f"Olá {cliente}! Recebi seu contato para o segmento {segmento} ({qtd} peças em {material}). Podemos alinhar os detalhes?"
                    link_wpp = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(msg)}"
                    
                    titulo_evento = f"Entrega Pedido: {cliente} ({segmento})"
                    detalhes_evento = f"Quantidade: {qtd} peças\nMaterial: {material}\nCliente: {cliente}"
                    link_gcal = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(titulo_evento)}&details={urllib.parse.quote(detalhes_evento)}"
                    
                    st.success("Atendimento processado com sucesso!")
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if whatsapp:
                            st.markdown(f'<a href="{link_wpp}" target="_blank" class="whatsapp-btn">💬 Enviar Mensagem WhatsApp</a>', unsafe_allow_html=True)
                    with col_b2:
                        st.markdown(f'<a href="{link_gcal}" target="_blank" class="gcal-btn">📅 Adicionar ao Google Agenda</a>', unsafe_allow_html=True)

    # ----------------------------------------------------
    # 4. GOOGLE AGENDA
    # ----------------------------------------------------
    elif menu == "📅 Google Agenda":
        st.subheader("📅 Central de Marcação no Google Agenda")
        with st.form("form_agenda_direta"):
            c_titulo = st.text_input("Título do Evento (ex: Prova de Fardamento - Colégio X)")
            c_desc = st.text_area("Descrição / Observações do Compromisso")
            c_data = st.text_input("Data e Hora (Ex: 15/06/2026 às 14:00)")
            
            if st.form_submit_button("📅 Criar Evento no Google Agenda"):
                titulo_final = f"{c_titulo} ({c_data})"
                link_agenda = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote(titulo_final)}&details={urllib.parse.quote(c_desc)}"
                st.success("Evento preparado com sucesso!")
                st.markdown(f'<a href="{link_agenda}" target="_blank" class="gcal-btn" style="font-size: 16px; padding: 12px 24px;">👉 Clique aqui para gravar no Google Agenda</a>', unsafe_allow_html=True)

    # ----------------------------------------------------
    # 5. ORÇAMENTOS
    # ----------------------------------------------------
    elif menu == "💰 Orçamentos":
        st.subheader("💰 Tabela de Orçamentos")
        df_orc = dfs.get("ORÇAMENTOS", pd.DataFrame())
        st.dataframe(df_orc, use_container_width=True)

    # ----------------------------------------------------
    # 6. MENSAGENS
    # ----------------------------------------------------
    elif menu == "💬 Mensagens":
        st.subheader("💬 Modelos Prontos para Atendimento")
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
    st.info("👈 **Para começar:** Faça o carregamento da sua planilha Excel (`Assistente_Atendimento_Textil_Fluxo_Atualizado.xlsx`) no menu à esquerda.")
