import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DGP - Dados dos Militares", layout="wide")

# --- ESCOPOS PARA A API DO GOOGLE SHEETS ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# --- FUNÇÃO DE AUTENTICAÇÃO DO USUÁRIO ---
def check_password():
    """Valida usuário e senha comparando com o bloco [passwords] nos Secrets."""

    def password_entered():
        user = st.session_state.get("username", "").strip()
        pwd = st.session_state.get("password", "").strip()
        passwords_dict = st.secrets.get("passwords", {})

        if user in passwords_dict and str(passwords_dict[user]) == pwd:
            st.session_state["password_correct"] = True
            if "password" in st.session_state:
                del st.session_state["password"]
            if "username" in st.session_state:
                del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Acesso Restrito ao Dashboard")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)

        if "password_correct" in st.session_state and not st.session_state[
            "password_correct"
        ]:
            st.error("😕 Usuário ou senha incorretos.")

    return False


# Bloqueia a execução se não estiver autenticado
if not check_password():
    st.stop()


# --- FUNÇÃO DE AUTENTICAÇÃO COM O GOOGLE SHEETS (GSPREAD) ---
def get_gspread_client():
    """Autentica na API do Google usando o bloco [gcp_service_account] dos Secrets."""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(credentials)


# --- BARRA LATERAL (LOGOUT E REFRESH) ---
st.sidebar.success("Autenticado com sucesso!")
if st.sidebar.button("🚪 Sair / Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

if st.sidebar.button("🔄 Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()

# --- CABEÇALHO E LOGOS ---
_, col_img1, col_img2, _ = st.columns([2, 1, 1, 2])
with col_img1:
    st.image("images.png", width=140)
with col_img2:
    st.image("11679.png", width=140)

st.markdown(
    "<h1 style='text-align: center;'> DGP - Dados dos Militares</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")


# --- FUNÇÃO DE CARREGAMENTO DOS DADOS ---
@st.cache_data(ttl=5)
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    # header=0 lê a linha 1 como cabeçalho
    df = pd.read_csv(url, header=0)
    df.columns = [str(col).strip().replace(":", "-") for col in df.columns]
    df = df.fillna("-")
    return df


try:
    SHEET_ID = st.secrets["SHEET_ID"]

    # ==============================================================================
    # 1. CARREGAMENTO INICIAL DO DATAFRAME
    # ==============================================================================
    df = load_data(SHEET_ID)
    df_filtrado = df.copy()

    # ==============================================================================
    # 🕵️ PAINEL DE DIAGNÓSTICO: CONFERÊNCIA DAS COLUNAS
    # ==============================================================================
    with st.expander("🔍 **Clique para Conferir a Ordem Exata das Colunas da Planilha**", expanded=False):
        colunas_planilha = list(df.columns)
        st.write(f"**Total de colunas encontradas:** {len(colunas_planilha)}")
        for idx, col in enumerate(colunas_planilha, start=1):
            st.text(f"Coluna {idx}: {col}")

    # ==============================================================================
    # 2. FORMULÁRIO DE CADASTRO DE NOVOS REGISTROS (50 CAMPOS)
    # ==============================================================================
    with st.expander("➕ **Cadastrar Novo Militar**", expanded=False):
        with st.form("novo_registro_militar_form", clear_on_submit=True):

            tab_pessoal, tab_lotacao, tab_cessao, tab_ltip, tab_outros = st.tabs([
                "👤 Identificação & Pessoal",
                "🏢 Lotação & Promoção",
                "🔄 Cessão & Movimentação",
                "⏳ LTIP & Afastamentos",
                "📝 Documentos & Observações",
            ])

            # --- ABA 1: IDENTIFICAÇÃO PESSOAL ---
            with tab_pessoal:
                c1, c2, c3 = st.columns(3)
                with c1:
                    num_funcional = st.text_input("nº Funcional:")
                    matricula = st.text_input("Matrícula:")
                    cpf_ponto = st.text_input("CPF.:")
                    cpf = st.text_input("CPF:")
                    num_ident = st.text_input("Nº IDENT.:")
                with c2:
                    nome = st.text_input("Nome:")
                    nome_guerra = st.text_input("Nome de Guerra:")
                    sexo = st.selectbox("SEXO:", ["", "MASCULINO", "FEMININO"])
                    raca_cor = st.selectbox(
                        "Raça/Cor:",
                        ["", "BRANCA", "PRETA", "PARDA", "AMARELA", "INDÍGENA"],
                    )
                with c3:
                    posto_grad = st.text_input("Posto/ Grad:")
                    fones = st.text_input("Fones:")
                    ano_ingresso = st.text_input("Ano de ingresso:")
                    data_praca = st.date_input("Data de praça:", value=None)

            # --- ABA 2: LOTAÇÃO & PROMOÇÃO ---
            with tab_lotacao:
                c1, c2, c3 = st.columns(3)
                with c1:
                    ome = st.text_input("OME:")
                    ome_qod = st.text_input("OME QOD:")
                    atividade = st.text_input("Atividade:")
                    municipio = st.text_input("Município:")
                    regiao = st.text_input("Região:")
                with c2:
                    tempo_servico_anos = st.number_input(
                        "Tempo de serviço (anos):", min_value=0, step=1
                    )
                    tempo_servico_amd = st.text_input(
                        "Tempo de serviço (ano, mês, dias):"
                    )
                    tempo_servico_dias = st.number_input(
                        "Tempo de serviço (dias):", min_value=0, step=1
                    )
                    tempo_obm_atual = st.text_input("Tempo na OBM atual:")
                with c3:
                    data_ult_promocao = st.date_input(
                        "Data da última promoção ou Implant. PCNH:", value=None
                    )
                    principio_ult_promocao = st.text_input(
                        "Princípio da última promoção:"
                    )
                    tempo_posto_atual_dias = st.number_input(
                        "Tempo no Posto/Grad. atual EM DIAS:", min_value=0, step=1
                    )

            # --- ABA 3: CESSÃO & MOVIMENTAÇÃO ---
            with tab_cessao:
                c1, c2, c3 = st.columns(3)
                with c1:
                    data_mov_sp = st.date_input(
                        "Data da Movimentação em SP:", value=None
                    )
                    ome_anterior = st.text_input(
                        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:"
                    )
                    data_chegada_obm_anterior = st.date_input(
                        "Data de chegada na OBM Anteior:", value=None
                    )
                    movimentado = st.text_input(
                        "Movimentado (apagar antes de atualizar o SP):"
                    )
                with c2:
                    orgao = st.text_input("ÓRGÃO:")
                    poder = st.text_input("Poder:")
                    onus_origem = st.selectbox(
                        "Ônus para Origem:", ["", "SIM", "NÃO"]
                    )
                    inicio_cessao = st.date_input(
                        "Início da Cessão ou requisição:", value=None
                    )
                with c3:
                    renovacao_cessao_atos = st.text_input(
                        "Renovação de cessão - Atos/Portarias/Documentos:"
                    )
                    doe_bgsds_renovacao = st.text_input("DOE/BGSDS de renovação:")
                    sei_deslig = st.text_input("SEI deslig.:")

            # --- ABA 4: LTIP & AFASTAMENTOS ---
            with tab_ltip:
                c1, c2 = st.columns(2)
                with c1:
                    afastamentos_sup_90 = st.text_area(
                        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP:"
                    )
                    inicio_ltip = st.date_input("INÍCIO DA LTIP:", value=None)
                    termino_ltip = st.date_input(
                        "TÉRMINO DA LTIP (inserir data de apresentação):", value=None
                    )
                with c2:
                    somatorio_ltip_anos = st.text_input(
                        "Somatório LTIP gozada em anos:"
                    )
                    somatorio_ltip_amd = st.text_input(
                        "Somatório LTIP gozada em anos/meses/dias:"
                    )
                    somatorio_ltip_dias = st.number_input(
                        "Somatório de todas LTIP gozadas em dias:",
                        min_value=0,
                        step=1,
                    )
                    total_dias_ltip_posto = st.number_input(
                        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:",
                        min_value=0,
                        step=1,
                    )

            # --- ABA 5: DOCUMENTOS & OBSERVAÇÕES ---
            with tab_outros:
                c1, c2 = st.columns(2)
                with c1:
                    ato = st.text_input("Ato:")
                    doc_publicacao = st.text_input("Doc. Publicação:")
                    sp_adicao = st.text_input("SP da Adição:")
                    processo_rr = st.text_input("Processo RR:")
                with c2:
                    suplemento_pessoal_num_ano = st.text_input(
                        "Suplemento de Pessoal nº/Ano:"
                    )
                    data_suplemento_pessoal = st.date_input(
                        "Data Suplemento de Pessoal:", value=None
                    )
                    hoje_data = st.date_input("Hoje:", value=None)
                    obs = st.text_area("OBS:")

            st.markdown("---")
            btn_salvar = st.form_submit_button(
                "💾 Salvar Registro Completo na Planilha"
            )

       # --- LÓGICA DE GRAVAÇÃO COM DIAGNÓSTICO DETALHADO ---
        if btn_salvar:
            if not nome and not matricula:
                st.warning(
                    "⚠️ Preencha ao menos o Nome ou a Matrícula do militar antes de salvar."
                )
            else:
                try:
                    client = get_gspread_client()
                    sheet = client.open_by_key(SHEET_ID).sheet1

                    def formatar_valor(val):
                        if val is None:
                            return ""
                        return str(val).strip()

                    nova_linha = [
                        formatar_valor(posto_grad),
                        formatar_valor(ome_qod),
                        formatar_valor(atividade),
                        formatar_valor(ome),
                        formatar_valor(data_mov_sp),
                        formatar_valor(municipio),
                        formatar_valor(regiao),
                        formatar_valor(obs),
                        formatar_valor(afastamentos_sup_90),
                        formatar_valor(orgao),
                        formatar_valor(num_funcional),
                        formatar_valor(matricula),
                        formatar_valor(nome),
                        formatar_valor(nome_guerra),
                        formatar_valor(ome_anterior),
                        formatar_valor(data_chegada_obm_anterior),
                        formatar_valor(onus_origem),
                        formatar_valor(poder),
                        formatar_valor(inicio_cessao),
                        formatar_valor(ato),
                        formatar_valor(doc_publicacao),
                        formatar_valor(sp_adicao),
                        formatar_valor(renovacao_cessao_atos),
                        formatar_valor(doe_bgsds_renovacao),
                        formatar_valor(num_ident),
                        formatar_valor(cpf_ponto),
                        formatar_valor(cpf),
                        formatar_valor(sexo),
                        formatar_valor(raca_cor),
                        formatar_valor(ano_ingresso),
                        formatar_valor(data_praca),
                        formatar_valor(tempo_servico_anos),
                        formatar_valor(tempo_servico_amd),
                        formatar_valor(tempo_servico_dias),
                        formatar_valor(data_ult_promocao),
                        formatar_valor(principio_ult_promocao),
                        formatar_valor(tempo_posto_atual_dias),
                        formatar_valor(sei_deslig),
                        formatar_valor(tempo_obm_atual),
                        formatar_valor(hoje_data),
                        formatar_valor(somatorio_ltip_anos),
                        formatar_valor(somatorio_ltip_amd),
                        formatar_valor(somatorio_ltip_dias),
                        formatar_valor(total_dias_ltip_posto),
                        formatar_valor(inicio_ltip),
                        formatar_valor(termino_ltip),
                        formatar_valor(movimentado),
                        formatar_valor(suplemento_pessoal_num_ano),
                        formatar_valor(data_suplemento_pessoal),
                        formatar_valor(fones),
                    ]

                    # Envia para a planilha
                    sheet.append_row(
                        nova_linha, value_input_option="USER_ENTERED"
                    )

                    st.success("✅ Registro cadastrado com sucesso!")
                    st.cache_data.clear()
                    st.rerun()

                except Exception as err_grava:
                    import traceback

                    st.error(f"❌ Erro ao gravar registro: {err_grava}")
                    st.code(traceback.format_exc(), language="python")

    # ==============================================================================
    # 3. FILTROS E BUSCA POR TEXTO
    # ==============================================================================
    st.subheader("🔍 Busca por Texto")
    termo_busca = st.text_input(
        "Digite algo para pesquisar na planilha inteira:", ""
    )

    if termo_busca:
        mascara = df_filtrado.astype(str).apply(
            lambda col: col.str.contains(termo_busca, case=False, na=False)
        )
        df_filtrado = df_filtrado[mascara.any(axis=1)]

    # --- FILTROS LATERAIS ---
    st.sidebar.header("🎛️ Filtros por Coluna")

    if st.sidebar.button("🧹 Limpar Filtros"):
        st.rerun()

    for coluna in df.columns:
        valores_unicos = df[coluna].dropna().astype(str).unique().tolist()
        valores_unicos.sort()

        opcoes = ["Todos"] + valores_unicos
        escolha = st.sidebar.selectbox(f"{coluna}:", opcoes, key=coluna)

        if escolha != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado[coluna].astype(str) == escolha
            ]

    # ==============================================================================
    # 4. MÉTRICAS, TABELA E GRÁFICOS
    # ==============================================================================
    m1, m2, m3 = st.columns(3)
    m1.metric("Registros Filtrados", len(df_filtrado))
    m2.metric("Total de Registros na Planilha", len(df))
    m3.metric(
        "% Exibido",
        f"{(len(df_filtrado) / len(df)) * 100:.1f}%" if len(df) > 0 else "0%",
    )

    st.markdown("---")

    # Tabela
    st.subheader("📋 Registros Encontrados")
    st.dataframe(df_filtrado, use_container_width=True)

    # Gráfico
    st.subheader("📈 Análise Visual")
    coluna_grafico = st.selectbox(
        "Escolha a coluna para o gráfico:", list(df.columns)
    )

    if len(df_filtrado) > 0:
        st.bar_chart(df_filtrado[coluna_grafico].value_counts())
    else:
        st.warning("⚠️ Nenhum registro encontrado para gerar o gráfico.")

except KeyError as err_key:
    st.error(f"❌ Chave ausente nos Secrets: {err_key}")
except Exception as e:
    st.error(f"Erro ao carregar ou processar os dados: {e}")
