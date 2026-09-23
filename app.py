
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Restrito", layout="wide")


# --- FUNÇÃO DE AUTENTICAÇÃO ---
def check_password():
    """Valida usuário e senha comparando com o bloco [passwords] nos Secrets."""

    def password_entered():
        # Remove espaços acidentais antes ou depois da digitação
        user = st.session_state.get("username", "").strip()
        pwd = st.session_state.get("password", "").strip()

        # Busca o dicionário de senhas nos Secrets
        passwords_dict = st.secrets.get("passwords", {})

        # Compara usuário e senha
        if user in passwords_dict and str(passwords_dict[user]) == pwd:
            st.session_state["password_correct"] = True
            # Limpa credenciais da memória
            if "password" in st.session_state:
                del st.session_state["password"]
            if "username" in st.session_state:
                del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Libera acesso se a sessão já estiver autenticada
    if st.session_state.get("password_correct", False):
        return True

    # Renderiza a Interface de Login
    st.title("🔒 Acesso Restrito ao Dashboard")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)

        # Exibe mensagem caso a autenticação falhe
        if "password_correct" in st.session_state and not st.session_state[
            "password_correct"
        ]:
            st.error("😕 Usuário ou senha incorretos.")

    return False


# Bloqueia a execução se não autenticado
if not check_password():
    st.stop()

# ==============================================================================
# CÓDIGO DO DASHBOARD (Apenas executado após login aprovado)
# ==============================================================================

st.sidebar.success("Autenticado com sucesso!")
if st.sidebar.button("🚪 Sair / Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

st.title("📊 Dashboard de Movimentações")
st.markdown("---")


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
