import pandas as pd
import streamlit as st



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


# Função para carregar os dados do Google Sheets
@st.cache_data(ttl=5)
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    df.columns = [str(col).strip() for col in df.columns]
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
