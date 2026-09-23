import pandas as pd
import streamlit as st



import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Restrito", layout="wide")


# --- FUNÇÃO DE AUTENTICAÇÃO ---
def check_password():
    """Retorna True se o usuário digitou o login e senha corretos."""

    def password_entered():
        """Verifica se o usuário e senha correspondem aos cadastrados nos Secrets."""
        user = st.session_state["username"]
        pwd = st.session_state["password"]

        if user in st.secrets.get("passwords", {}) and st.secrets[
            "passwords"
        ].get(user) == pwd:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Limpa a senha da memória
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Se já autenticado, retorna True
    if st.session_state.get("password_correct", False):
        return True

    # Exibe a tela de Login
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


# Se a senha não for válida, interrompe a execução e exibe apenas a tela de login
if not check_password():
    st.stop()

# ==============================================================================
# A PARTIR DAQUI O CÓDIGO SÓ É EXECUTADO APÓS O LOGIN COM SUCESSO
# ==============================================================================

# Botão de Logout na Barra Lateral
st.sidebar.title(f"Bem-vindo(a)!")
if st.sidebar.button("🚪 Sair / Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

# --- CARREGAMENTO DOS DADOS ---
SHEET_ID = st.secrets["SHEET_ID"]


@st.cache_data(ttl=5)
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url, header=6)
    df.columns = [
        str(col).strip().replace(":", "-") for col in df.columns
    ]
    df = df.fillna("-")
    return df


try:
    df = load_data(SHEET_ID)

    st.title("📊 Dashboard de Movimentações")
    st.markdown("---")

    # Exibição dos dados e filtros do seu dashboard
    st.subheader("📋 Registros Encontrados")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")



# --- CENTRALIZANDO E APROXIMANDO AS IMAGENS ---
# Criamos 4 colunas: [Espaço Esquerdo, Imagem 1, Imagem 2, Espaço Direito]
# Os valores controlam a proporção de largura de cada coluna
_, col_img1, col_img2, _ = st.columns([2, 1, 1, 2])

with col_img1:
    st.image("images.png", width=140)

with col_img2:
    st.image("11679.png", width=140)

st.markdown("<h1 style='text-align: center;'>📊 DGP - Dados dos Militares</h1>", unsafe_allow_html=True)
st.markdown("---")


@st.cache_data(ttl=5)
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    # header=6 indica que os nomes das colunas estão na Linha 7 do Google Sheets
    df = pd.read_csv(url, header=8)

    # Limpeza dos nomes das colunas (remove espaços e dois-pontos)
    df.columns = [
        str(col).strip().replace(":", "-") for col in df.columns
    ]

    # Preenche células vazias com hífen
    df = df.fillna("-")

    return df

# --- INSIRA O ID DA SUA PLANILHA ABAIXO ---
SHEET_ID = st.secrets["SHEET_ID"]

try:
    # Botão de atualização manual na barra lateral
    if st.sidebar.button("🔄 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

    df = load_data(SHEET_ID)

    # --- BARRA DE BUSCA DIGITADA ---
    st.subheader("🔍 Busca por Texto")
    termo_busca = st.text_input(
        "Digite algo para pesquisar na planilha inteira:", ""
    )

    df_filtrado = df.copy()

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
        valores_unicos = (
            df[coluna].dropna().astype(str).unique().tolist()
        )
        valores_unicos.sort()

        opcoes = ["Todos"] + valores_unicos
        escolha = st.sidebar.selectbox(f"{coluna}:", opcoes, key=coluna)

        if escolha != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado[coluna].astype(str) == escolha
            ]

    # --- MÉTRICAS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Registros Filtrados", len(df_filtrado))
    m2.metric("Total de Registros na Planilha", len(df))
    m3.metric(
        "% Exibido",
        f"{(len(df_filtrado) / len(df)) * 100:.1f}%" if len(df) > 0 else "0%",
    )

    st.markdown("---")

    # --- TABELA DE DADOS ---
    st.subheader("📋 Registros Encontrados")
    st.dataframe(df_filtrado, use_container_width=True)

    # --- GRÁFICO AUTOMÁTICO ---
    st.subheader("📈 Análise Visual")
    coluna_grafico = st.selectbox(
        "Escolha a coluna para o gráfico:", list(df.columns)
    )
    if len(df_filtrado) > 0:
        st.bar_chart(df_filtrado[coluna_grafico].value_counts())

except Exception as e:
    st.error(f"Erro ao carregar ou processar os dados: {e}")
