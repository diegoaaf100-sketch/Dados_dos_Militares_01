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
    "<h1 style='text-align: center;'>📊 DGP - Dados dos Militares</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")


# --- FUNÇÃO DE CARREGAMENTO DOS DADOS ---
@st.cache_data(ttl=5)
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    # header=8 lê a linha 9 como cabeçalho
    df = pd.read_csv(url, header=8)
    df.columns = [str(col).strip().replace(":", "-") for col in df.columns]
    df = df.fillna("-")
    return df


try:
    SHEET_ID = st.secrets["SHEET_ID"]

    # ==============================================================================
    # 1. CARREGAMENTO INICIAL DO DATAFRAME
    # ==============================================================================
    df = load_data(SHEET_ID)

    # Criação imediata do df_filtrado como cópia do df original
    df_filtrado = df.copy()

    # ==============================================================================
    # 2. FORMULÁRIO DE CADASTRO DE NOVOS REGISTROS
    # ==============================================================================
    with st.expander("➕ **Cadastrar Novo Registro na Planilha**", expanded=False):
        with st.form("novo_registro_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome / Militar")
                posto = st.selectbox(
                    "Posto/Graduação",
                    ["Soldado", "Cabo", "Sargento", "Tenente", "Capitão"],
                )
            with c2:
                movimentacao = st.selectbox(
                    "Tipo de Movimentação",
                    ["Entrada", "Saída", "Transferência"],
                )
                observacao = st.text_area("Observações")

            btn_salvar = st.form_submit_button("💾 Salvar Registro na Planilha")

        if btn_salvar:
            if not nome:
                st.warning("⚠️ Preencha o nome do militar antes de salvar.")
            else:
                try:
                    client = get_gspread_client()
                    sheet = client.open_by_key(SHEET_ID).sheet1

                    nova_linha = [nome, posto, movimentacao, observacao]
                    sheet.append_row(nova_linha)

                    st.success("✅ Registro inserido com sucesso!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as err_grava:
                    st.error(f"Erro ao gravar registro na planilha: {err_grava}")

    st.markdown("---")

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
