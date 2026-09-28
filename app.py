import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="DGP - Dados dos Militares",
    page_icon="🚨",
    layout="wide",
)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ============================================================
# CABEÇALHOS EXATOS DA PÁGINA 1
# ============================================================

HEADERS_ESPERADOS = [
    "Posto/ Grad",
    "OME QOD",
    "Matrícula",
    "Nome de Guerra",
    "Nome",
    "nº Funcional",
    "Atividade",
    "OME",
    "Data da Movimentação em SP",
    "Município",
    "Região",
    "OBS",
    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP",
    "ÓRGÃO",
    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO",
    "Data de chegada na OBM Anteior",
    "Ônus para Origem",
    "Poder",
    "Início da Cessão ou requisição",
    "Ato",
    "Doc. Publicação",
    "SP da Adição",
    "Renovação de cessão - Atos/Portarias/Documentos",
    "DOE/BGSDS de renovação",
    "Nº IDENT.",
    "CPF",
    "SEXO",
    "Raça/Cor",
    "Ano de ingresso",
    "Data de praça",
    "Tempo de serviço (anos)",
    "Tempo de serviço (ano, mês, dias)",
    "Tempo de serviço (dias)",
    "Data da última promoção ou Implant. PCNH",
    "Princípio da última promoção",
    "Tempo no Posto/Grad. atual EM DIAS",
    "SEI deslig.",
    "Tempo na OBM atual",
    "Hoje",
    "Somatório LTIP gozada em anos",
    "Somatório LTIP gozada em anos/meses/dias",
    "Somatório de todas LTIP gozadas em dias",
    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.",
    "INÍCIO DA LTIP",
    "TÉRMINO DA LTIP (inserir data de apresentação)",
    "Movimentado (apagar antes de atualizar o SP)",
    "Suplemento de Pessoal nº/Ano",
    "Data Suplemento de Pessoal",
    "Fones",
]


# ============================================================
# FUNÇÕES GERAIS
# ============================================================

def texto(valor):
    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass

    return str(valor)


def normalizar_matricula(valor):
    return texto(valor).strip().upper()


def valor_para_filtro(valor):
    return texto(valor).strip()


# ============================================================
# AUTENTICAÇÃO
# ============================================================

def check_password():

    def password_entered():

        user = st.session_state.get(
            "username",
            ""
        ).strip()

        pwd = st.session_state.get(
            "password",
            ""
        ).strip()

        passwords_dict = st.secrets.get(
            "passwords",
            {}
        )

        if (
            user in passwords_dict
            and str(passwords_dict[user]) == pwd
        ):
            st.session_state["password_correct"] = True

            st.session_state.pop(
                "password",
                None
            )

            st.session_state.pop(
                "username",
                None
            )

        else:
            st.session_state["password_correct"] = False

    if st.session_state.get(
        "password_correct",
        False
    ):
        return True

    st.title("🔒 Acesso Restrito ao Dashboard")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.text_input(
            "Usuário",
            key="username"
        )

        st.text_input(
            "Senha",
            type="password",
            key="password"
        )

        st.button(
            "Entrar",
            on_click=password_entered
        )

        if (
            "password_correct" in st.session_state
            and not st.session_state["password_correct"]
        ):
            st.error(
                "😕 Usuário ou senha incorretos."
            )

    return False


if not check_password():
    st.stop()


# ============================================================
# GOOGLE SHEETS
# ============================================================

def get_gspread_client():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


def get_sheet():

    sheet_id = st.secrets["SHEET_ID"]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(sheet_id)

    worksheet = spreadsheet.worksheet("Página1")

    return worksheet


# ============================================================
# CARREGAR DADOS
# ============================================================

@st.cache_data(ttl=5)
def carregar_dados():

    worksheet = get_sheet()

    valores = worksheet.get_all_values()

    if not valores:
        return pd.DataFrame(
            columns=HEADERS_ESPERADOS
        )

    cabecalhos = [
        texto(x).strip()
        for x in valores[0]
    ]

    dados = valores[1:]

    # Verifica duplicidade
    duplicados = [
        x
        for x in set(cabecalhos)
        if cabecalhos.count(x) > 1
    ]

    if duplicados:
        raise ValueError(
            "Existem cabeçalhos duplicados na Página1: "
            + ", ".join(duplicados)
        )

    quantidade_colunas = len(cabecalhos)

    linhas_corrigidas = []

    for linha in dados:

        linha = list(linha)

        if len(linha) < quantidade_colunas:
            linha += [""] * (
                quantidade_colunas - len(linha)
            )

        elif len(linha) > quantidade_colunas:
            linha = linha[:quantidade_colunas]

        linhas_corrigidas.append(linha)

    df = pd.DataFrame(
        linhas_corrigidas,
        columns=cabecalhos
    )

    # Segurança adicional contra duplicidade
    df = df.loc[:, ~df.columns.duplicated()]

    return df


# ============================================================
# ESTRUTURA
# ============================================================

def verificar_estrutura(worksheet):

    headers = [
        texto(x).strip()
        for x in worksheet.row_values(1)
    ]

    if not headers:
        raise ValueError(
            "A primeira linha da Página1 está vazia."
        )

    duplicados = [
        x
        for x in set(headers)
        if headers.count(x) > 1
    ]

    if duplicados:
        raise ValueError(
            "Existem colunas duplicadas: "
            + ", ".join(duplicados)
        )

    faltantes = [
        x
        for x in HEADERS_ESPERADOS
        if x not in headers
    ]

    if faltantes:
        raise ValueError(
            "As seguintes colunas esperadas "
            "não foram encontradas:\n\n"
            + "\n".join(
                f"- {x}"
                for x in faltantes
            )
        )

    return headers


# ============================================================
# LOCALIZAR COLUNA
# ============================================================

def localizar_coluna(headers, nome):

    for i, header in enumerate(headers):

        if texto(header).strip() == nome:
            return i + 1

    return None


# ============================================================
# LOCALIZAR LINHA PELA MATRÍCULA
# ============================================================

def localizar_linha_por_matricula(
    worksheet,
    matricula
):

    valores = worksheet.get_all_values()

    if not valores:
        return None

    headers = valores[0]

    coluna = localizar_coluna(
        headers,
        "Matrícula"
    )

    if coluna is None:
        raise ValueError(
            "A coluna Matrícula não foi encontrada."
        )

    indice = coluna - 1

    matricula_procurada = normalizar_matricula(
        matricula
    )

    for numero_linha, linha in enumerate(
        valores[1:],
        start=2
    ):

        if indice < len(linha):

            matricula_linha = normalizar_matricula(
                linha[indice]
            )

            if matricula_linha == matricula_procurada:
                return numero_linha

    return None


# ============================================================
# MONTAR LINHA PARA GRAVAÇÃO
# ============================================================

def montar_linha(headers, dados):

    linha = []

    for header in headers:

        valor = dados.get(
            header,
            ""
        )

        linha.append(
            texto(valor)
        )

    return linha


# ============================================================
# FORMULÁRIO
# ============================================================

def campo_texto(
    label,
    dados,
    chave,
    coluna,
    tipo="text"
):

    valor = texto(
        dados.get(
            coluna,
            ""
        )
    )

    if tipo == "area":
        return st.text_area(
            label,
            value=valor,
            key=chave
        )

    return st.text_input(
        label,
        value=valor,
        key=chave
    )


def criar_formulario(
    dados,
    prefixo
):

    if dados is None:
        dados = {}

    resultado = {}

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "👤 Identificação & Pessoal",
            "🏢 Lotação & Promoção",
            "🔄 Cessão & Movimentação",
            "⏳ LTIP & Afastamentos",
            "📝 Documentos & Observações",
        ]
    )

    # ========================================================
    # TAB 1
    # ========================================================

    with tab1:

        c1, c2, c3 = st.columns(3)

        with c1:

            resultado["Matrícula"] = campo_texto(
                "Matrícula",
                dados,
                f"{prefixo}_matricula",
                "Matrícula"
            )

            resultado["nº Funcional"] = campo_texto(
                "nº Funcional",
                dados,
                f"{prefixo}_funcional",
                "nº Funcional"
            )

            resultado["Nº IDENT."] = campo_texto(
                "Nº IDENT.",
                dados,
                f"{prefixo}_ident",
                "Nº IDENT."
            )

            resultado["CPF"] = campo_texto(
                "CPF",
                dados,
                f"{prefixo}_cpf",
                "CPF"
            )

        with c2:

            resultado["Nome"] = campo_texto(
                "Nome",
                dados,
                f"{prefixo}_nome",
                "Nome"
            )

            resultado["Nome de Guerra"] = campo_texto(
                "Nome de Guerra",
                dados,
                f"{prefixo}_nome_guerra",
                "Nome de Guerra"
            )

            sexo_atual = texto(
                dados.get(
                    "SEXO",
                    ""
                )
            ).upper()

            opcoes_sexo = [
                "",
                "MASCULINO",
                "FEMININO"
            ]

            resultado["SEXO"] = st.selectbox(
                "SEXO",
                opcoes_sexo,
                index=(
                    opcoes_sexo.index(sexo_atual)
                    if sexo_atual in opcoes_sexo
                    else 0
                ),
                key=f"{prefixo}_sexo"
            )

            raca_atual = texto(
                dados.get(
                    "Raça/Cor",
                    ""
                )
            ).upper()

            opcoes_raca = [
                "",
                "BRANCA",
                "PRETA",
                "PARDA",
                "AMARELA",
                "INDÍGENA"
            ]

            resultado["Raça/Cor"] = st.selectbox(
                "Raça/Cor",
                opcoes_raca,
                index=(
                    opcoes_raca.index(raca_atual)
                    if raca_atual in opcoes_raca
                    else 0
                ),
                key=f"{prefixo}_raca"
            )

        with c3:

            resultado["Posto/ Grad"] = campo_texto(
                "Posto/ Grad",
                dados,
                f"{prefixo}_posto",
                "Posto/ Grad"
            )

            resultado["Fones"] = campo_texto(
                "Fones",
                dados,
                f"{prefixo}_fones",
                "Fones"
            )

            resultado["Ano de ingresso"] = campo_texto(
                "Ano de ingresso",
                dados,
                f"{prefixo}_ano",
                "Ano de ingresso"
            )

            resultado["Data de praça"] = campo_texto(
                "Data de praça",
                dados,
                f"{prefixo}_praca",
                "Data de praça"
            )

    # ========================================================
    # TAB 2
    # ========================================================

    with tab2:

        c1, c2, c3 = st.columns(3)

        with c1:

            resultado["OME"] = campo_texto(
                "OME",
                dados,
                f"{prefixo}_ome",
                "OME"
            )

            resultado["OME QOD"] = campo_texto(
                "OME QOD",
                dados,
                f"{prefixo}_ome_qod",
                "OME QOD"
            )

            resultado["Atividade"] = campo_texto(
                "Atividade",
                dados,
                f"{prefixo}_atividade",
                "Atividade"
            )

            resultado["Município"] = campo_texto(
                "Município",
                dados,
                f"{prefixo}_municipio",
                "Município"
            )

            resultado["Região"] = campo_texto(
                "Região",
                dados,
                f"{prefixo}_regiao",
                "Região"
            )

        with c2:

            resultado[
                "Tempo de serviço (anos)"
            ] = campo_texto(
                "Tempo de serviço (anos)",
                dados,
                f"{prefixo}_tempo_anos",
                "Tempo de serviço (anos)"
            )

            resultado[
                "Tempo de serviço (ano, mês, dias)"
            ] = campo_texto(
                "Tempo de serviço (ano, mês, dias)",
                dados,
                f"{prefixo}_tempo_amd",
                "Tempo de serviço (ano, mês, dias)"
            )

            resultado[
                "Tempo de serviço (dias)"
            ] = campo_texto(
                "Tempo de serviço (dias)",
                dados,
                f"{prefixo}_tempo_dias",
                "Tempo de serviço (dias)"
            )

            resultado[
                "Tempo na OBM atual"
            ] = campo_texto(
                "Tempo na OBM atual",
                dados,
                f"{prefixo}_tempo_obm",
                "Tempo na OBM atual"
            )

        with c3:

            resultado[
                "Data da última promoção ou Implant. PCNH"
            ] = campo_texto(
                "Data da última promoção ou Implant. PCNH",
                dados,
                f"{prefixo}_promocao_data",
                "Data da última promoção ou Implant. PCNH"
            )

            resultado[
                "Princípio da última promoção"
            ] = campo_texto(
                "Princípio da última promoção",
                dados,
                f"{prefixo}_promocao_principio",
                "Princípio da última promoção"
            )

            resultado[
                "Tempo no Posto/Grad. atual EM DIAS"
            ] = campo_texto(
                "Tempo no Posto/Grad. atual EM DIAS",
                dados,
                f"{prefixo}_tempo_posto",
                "Tempo no Posto/Grad. atual EM DIAS"
            )

    # ========================================================
    # TAB 3
    # ========================================================

    with tab3:

        c1, c2, c3 = st.columns(3)

        with c1:

            resultado[
                "Data da Movimentação em SP"
            ] = campo_texto(
                "Data da Movimentação em SP",
                dados,
                f"{prefixo}_mov_sp",
                "Data da Movimentação em SP"
            )

            resultado[
                "OME ANTERIOR AO ÚLTIMO SP PUBLICADO"
            ] = campo_texto(
                "OME ANTERIOR AO ÚLTIMO SP PUBLICADO",
                dados,
                f"{prefixo}_ome_anterior",
                "OME ANTERIOR AO ÚLTIMO SP PUBLICADO"
            )

            resultado[
                "Data de chegada na OBM Anteior"
            ] = campo_texto(
                "Data de chegada na OBM Anteior",
                dados,
                f"{prefixo}_chegada",
                "Data de chegada na OBM Anteior"
            )

            resultado[
                "Movimentado (apagar antes de atualizar o SP)"
            ] = campo_texto(
                "Movimentado (apagar antes de atualizar o SP)",
                dados,
                f"{prefixo}_movimentado",
                "Movimentado (apagar antes de atualizar o SP)"
            )

        with c2:

            resultado["ÓRGÃO"] = campo_texto(
                "ÓRGÃO",
                dados,
                f"{prefixo}_orgao",
                "ÓRGÃO"
            )

            resultado["Poder"] = campo_texto(
                "Poder",
                dados,
                f"{prefixo}_poder",
                "Poder"
            )

            onus_atual = texto(
                dados.get(
                    "Ônus para Origem",
                    ""
                )
            ).upper()

            opcoes_onus = [
                "",
                "SIM",
                "NÃO"
            ]

            resultado[
                "Ônus para Origem"
            ] = st.selectbox(
                "Ônus para Origem",
                opcoes_onus,
                index=(
                    opcoes_onus.index(onus_atual)
                    if onus_atual in opcoes_onus
                    else 0
                ),
                key=f"{prefixo}_onus"
            )

            resultado[
                "Início da Cessão ou requisição"
            ] = campo_texto(
                "Início da Cessão ou requisição",
                dados,
                f"{prefixo}_inicio_cessao",
                "Início da Cessão ou requisição"
            )

        with c3:

            resultado[
                "Renovação de cessão - Atos/Portarias/Documentos"
            ] = campo_texto(
                "Renovação de cessão - Atos/Portarias/Documentos",
                dados,
                f"{prefixo}_renovacao",
                "Renovação de cessão - Atos/Portarias/Documentos"
            )

            resultado[
                "DOE/BGSDS de renovação"
            ] = campo_texto(
                "DOE/BGSDS de renovação",
                dados,
                f"{prefixo}_doe",
                "DOE/BGSDS de renovação"
            )

            resultado["SEI deslig."] = campo_texto(
                "SEI deslig.",
                dados,
                f"{prefixo}_sei",
                "SEI deslig."
            )

    # ========================================================
    # TAB 4
    # ========================================================

    with tab4:

        c1, c2 = st.columns(2)

        with c1:

            resultado[
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP"
            ] = campo_texto(
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP",
                dados,
                f"{prefixo}_afastamentos",
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP",
                tipo="area"
            )

            resultado["INÍCIO DA LTIP"] = campo_texto(
                "INÍCIO DA LTIP",
                dados,
                f"{prefixo}_inicio_ltip",
                "INÍCIO DA LTIP"
            )

            resultado[
                "TÉRMINO DA LTIP (inserir data de apresentação)"
            ] = campo_texto(
                "TÉRMINO DA LTIP (inserir data de apresentação)",
                dados,
                f"{prefixo}_termino_ltip",
                "TÉRMINO DA LTIP (inserir data de apresentação)"
            )

        with c2:

            resultado[
                "Somatório LTIP gozada em anos"
            ] = campo_texto(
                "Somatório LTIP gozada em anos",
                dados,
                f"{prefixo}_ltip_anos",
                "Somatório LTIP gozada em anos"
            )

            resultado[
                "Somatório LTIP gozada em anos/meses/dias"
            ] = campo_texto(
                "Somatório LTIP gozada em anos/meses/dias",
                dados,
                f"{prefixo}_ltip_amd",
                "Somatório LTIP gozada em anos/meses/dias"
            )

            resultado[
                "Somatório de todas LTIP gozadas em dias"
            ] = campo_texto(
                "Somatório de todas LTIP gozadas em dias",
                dados,
                f"{prefixo}_ltip_dias",
                "Somatório de todas LTIP gozadas em dias"
            )

            resultado[
                "TOTAL DIAS EM LTIP no MESMO Posto/Grad."
            ] = campo_texto(
                "TOTAL DIAS EM LTIP no MESMO Posto/Grad.",
                dados,
                f"{prefixo}_total_ltip",
                "TOTAL DIAS EM LTIP no MESMO Posto/Grad."
            )

    # ========================================================
    # TAB 5
    # ========================================================

    with tab5:

        c1, c2 = st.columns(2)

        with c1:

            resultado["Ato"] = campo_texto(
                "Ato",
                dados,
                f"{prefixo}_ato",
                "Ato"
            )

            resultado["Doc. Publicação"] = campo_texto(
                "Doc. Publicação",
                dados,
                f"{prefixo}_doc",
                "Doc. Publicação"
            )

            resultado["SP da Adição"] = campo_texto(
                "SP da Adição",
                dados,
                f"{prefixo}_sp",
                "SP da Adição"
            )

            resultado[
                "Suplemento de Pessoal nº/Ano"
            ] = campo_texto(
                "Suplemento de Pessoal nº/Ano",
                dados,
                f"{prefixo}_suplemento",
                "Suplemento de Pessoal nº/Ano"
            )

            resultado[
                "Data Suplemento de Pessoal"
            ] = campo_texto(
                "Data Suplemento de Pessoal",
                dados,
                f"{prefixo}_data_suplemento",
                "Data Suplemento de Pessoal"
            )

        with c2:

            resultado["Hoje"] = campo_texto(
                "Hoje",
                dados,
                f"{prefixo}_hoje",
                "Hoje"
            )

            resultado["OBS"] = campo_texto(
                "OBS",
                dados,
                f"{prefixo}_obs",
                "OBS",
                tipo="area"
            )

    return resultado


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.success(
    "✅ Autenticado com sucesso!"
)

if st.sidebar.button(
    "🚪 Sair / Logout"
):

    st.session_state["password_correct"] = False
    st.rerun()


if st.sidebar.button(
    "🔄 Atualizar dados da planilha"
):

    st.cache_data.clear()
    st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================

col1, col2, col3, col4 = st.columns(
    [2, 1, 1, 2]
)

with col2:

    try:
        st.image(
            "images.png",
            width=140
        )
    except Exception:
        pass


with col3:

    try:
        st.image(
            "11679.png",
            width=140
        )
    except Exception:
        pass


st.markdown(
    "<h1 style='text-align:center;'>"
    "🚨 DGP - Dados dos Militares"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# CONEXÃO
# ============================================================

try:

    worksheet = get_sheet()

    headers = verificar_estrutura(
        worksheet
    )

    df = carregar_dados()

except Exception as erro:

    st.error(
        "❌ Não foi possível carregar a Página1."
    )

    st.exception(erro)

    st.stop()


# ============================================================
# SEGURANÇA CONTRA COLUNAS DUPLICADAS
# ============================================================

if df.columns.duplicated().any():

    duplicadas = list(
        df.columns[
            df.columns.duplicated()
        ]
    )

    st.error(
        "❌ Existem colunas duplicadas no DataFrame: "
        + ", ".join(duplicadas)
    )

    st.stop()


# ============================================================
# MENSAGEM DE SUCESSO
# ============================================================

if st.session_state.get(
    "mensagem_sucesso"
):

    st.success(
        st.session_state["mensagem_sucesso"]
    )

    del st.session_state[
        "mensagem_sucesso"
    ]


# ============================================================
# FILTROS LATERAIS
# ============================================================

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Filtros")


def criar_filtro(df_base, coluna, label):

    if coluna not in df_base.columns:
        return []

    valores = sorted(
        [
            valor_para_filtro(x)
            for x in df_base[coluna].unique()
            if valor_para_filtro(x)
        ]
    )

    return st.sidebar.multiselect(
        label,
        valores,
        default=[],
        key=f"filtro_{coluna}"
    )


# Busca geral
busca = st.sidebar.text_input(
    "🔎 Buscar militar",
    placeholder="Nome, matrícula, CPF..."
)


filtro_posto = criar_filtro(
    df,
    "Posto/ Grad",
    "Posto/ Grad"
)

filtro_ome = criar_filtro(
    df,
    "OME",
    "OME"
)

filtro_atividade = criar_filtro(
    df,
    "Atividade",
    "Atividade"
)

filtro_municipio = criar_filtro(
    df,
    "Município",
    "Município"
)

filtro_regiao = criar_filtro(
    df,
    "Região",
    "Região"
)

filtro_sexo = criar_filtro(
    df,
    "SEXO",
    "SEXO"
)

filtro_raca = criar_filtro(
    df,
    "Raça/Cor",
    "Raça/Cor"
)

filtro_orgao = criar_filtro(
    df,
    "ÓRGÃO",
    "ÓRGÃO"
)

filtro_poder = criar_filtro(
    df,
    "Poder",
    "Poder"
)


if st.sidebar.button(
    "🧹 Limpar filtros"
):

    chaves = [
        "filtro_Posto/ Grad",
        "filtro_OME",
        "filtro_Atividade",
        "filtro_Município",
        "filtro_Região",
        "filtro_SEXO",
        "filtro_Raça/Cor",
        "filtro_ÓRGÃO",
        "filtro_Poder",
    ]

    for chave in chaves:
        if chave in st.session_state:
            st.session_state[chave] = []

    st.session_state["busca"] = ""

    st.rerun()


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df.copy()


if busca:

    texto_busca = busca.strip().lower()

    colunas_busca = [
        "Matrícula",
        "Nome",
        "Nome de Guerra",
        "CPF",
        "Nº IDENT.",
        "nº Funcional",
        "Fones",
    ]

    mascaras = []

    for coluna in colunas_busca:

        if coluna in df_filtrado.columns:

            mascaras.append(
                df_filtrado[coluna]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    texto_busca,
                    regex=False
                )
            )

    if mascaras:

        mascara_final = mascaras[0]

        for mascara in mascaras[1:]:
            mascara_final = (
                mascara_final
                | mascara
            )

        df_filtrado = df_filtrado[
            mascara_final
        ]


def aplicar_filtro(
    dataframe,
    coluna,
    valores
):

    if (
        valores
        and coluna in dataframe.columns
    ):

        return dataframe[
            dataframe[coluna]
            .fillna("")
            .astype(str)
            .str.strip()
            .isin(valores)
        ]

    return dataframe


df_filtrado = aplicar_filtro(
    df_filtrado,
    "Posto/ Grad",
    filtro_posto
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "OME",
    filtro_ome
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "Atividade",
    filtro_atividade
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "Município",
    filtro_municipio
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "Região",
    filtro_regiao
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "SEXO",
    filtro_sexo
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "Raça/Cor",
    filtro_raca
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "ÓRGÃO",
    filtro_orgao
)

df_filtrado = aplicar_filtro(
    df_filtrado,
    "Poder",
    filtro_poder
)


# ============================================================
# INDICADORES
# ============================================================

st.subheader("📊 Resumo do Efetivo")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Total na Página1",
        len(df)
    )

with m2:
    st.metric(
        "Registros filtrados",
        len(df_filtrado)
    )

with m3:

    if "OME" in df_filtrado.columns:
        total_omes = (
            df_filtrado["OME"]
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )
    else:
        total_omes = 0

    st.metric(
        "OMEs",
        total_omes
    )

with m4:

    if "Posto/ Grad" in df_filtrado.columns:
        total_postos = (
            df_filtrado["Posto/ Grad"]
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )
    else:
        total_postos = 0

    st.metric(
        "Postos/Grad.",
        total_postos
    )


# ============================================================
# GRÁFICOS
# ============================================================

st.markdown("---")

st.subheader("📈 Gráficos")


def tabela_contagem(dataframe, coluna):

    if coluna not in dataframe.columns:
        return pd.DataFrame()

    resultado = (
        dataframe[coluna]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    resultado = resultado[
        resultado != ""
    ]

    if resultado.empty:
        return pd.DataFrame()

    contagem = (
        resultado
        .value_counts()
        .rename_axis(coluna)
        .reset_index(name="Quantidade")
    )

    return contagem


g1, g2 = st.columns(2)


with g1:

    dados_grafico = tabela_contagem(
        df_filtrado,
        "Posto/ Grad"
    )

    if not dados_grafico.empty:

        st.markdown("### 👮 Efetivo por Posto/Grad.")

        st.bar_chart(
            dados_grafico.set_index(
                "Posto/ Grad"
            )["Quantidade"]
        )

    else:
        st.info(
            "Não há dados para o gráfico de Posto/Grad."
        )


with g2:

    dados_grafico = tabela_contagem(
        df_filtrado,
        "OME"
    )

    if not dados_grafico.empty:

        st.markdown("### 🏢 Efetivo por OME")

        st.bar_chart(
            dados_grafico.set_index(
                "OME"
            )["Quantidade"]
        )

    else:
        st.info(
            "Não há dados para o gráfico de OME."
        )


g3, g4 = st.columns(2)


with g3:

    dados_grafico = tabela_contagem(
        df_filtrado,
        "Município"
    )

    if not dados_grafico.empty:

        st.markdown("### 📍 Efetivo por Município")

        st.bar_chart(
            dados_grafico.set_index(
                "Município"
            )["Quantidade"]
        )

    else:
        st.info(
            "Não há dados para o gráfico de Município."
        )


with g4:

    dados_grafico = tabela_contagem(
        df_filtrado,
        "Atividade"
    )

    if not dados_grafico.empty:

        st.markdown("### 🧑‍💼 Efetivo por Atividade")

        st.bar_chart(
            dados_grafico.set_index(
                "Atividade"
            )["Quantidade"]
        )

    else:
        st.info(
            "Não há dados para o gráfico de Atividade."
        )


g5, g6 = st.columns(2)


with g5:

    dados_grafico = tabela_contagem(
        df_filtrado,
        "SEXO"
    )

    if not dados_grafico.empty:

        st.markdown("### 👥 Distribuição por Sexo")

        st.bar_chart(
            dados_grafico.set_index(
                "SEXO"
            )["Quantidade"]
        )

    else:
        st.info(
            "Não há dados para o gráfico de Sexo."
        )


with g6:

    dados_grafico = tabela_contagem(
        df_filtrado,
        "Região"
    )

    if not dados_grafico.empty:

        st.markdown("### 🗺️ Efetivo por Região")

        st.bar_chart(
            dados_grafico.set_index(
                "Região"
            )["Quantidade"]
        )

    else:
        st.info(
            "Não há dados para o gráfico de Região."
        )


# ============================================================
# VISUALIZAÇÃO DOS REGISTROS
# ============================================================

st.markdown("---")

st.subheader("📋 Visualização dos Registros")

st.caption(
    f"Página1 • {len(df_filtrado)} registros exibidos "
    f"de {len(df)} totais • {len(headers)} colunas"
)

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# NOVO CADASTRO
# ============================================================

st.markdown("---")

with st.expander(
    "➕ **Novo Cadastro de Militar**",
    expanded=False
):

    st.info(
        "Preencha os dados e clique em "
        "**💾 SALVAR NOVO CADASTRO**."
    )

    with st.form(
        "form_novo_cadastro",
        clear_on_submit=False
    ):

        dados_novos = criar_formulario(
            {},
            "novo"
        )

        st.markdown("---")

        salvar = st.form_submit_button(
            "💾 SALVAR NOVO CADASTRO",
            type="primary",
            use_container_width=True
        )

    if salvar:

        try:

            matricula = normalizar_matricula(
                dados_novos.get(
                    "Matrícula",
                    ""
                )
            )

            nome = texto(
                dados_novos.get(
                    "Nome",
                    ""
                )
            ).strip()

            if not matricula:
                st.error(
                    "❌ Informe a Matrícula."
                )
                st.stop()

            if not nome:
                st.error(
                    "❌ Informe o Nome."
                )
                st.stop()

            linha_existente = (
                localizar_linha_por_matricula(
                    worksheet,
                    matricula
                )
            )

            if linha_existente:

                st.error(
                    f"❌ A matrícula **{matricula}** "
                    f"já existe na linha "
                    f"{linha_existente}."
                )

                st.stop()

            nova_linha = montar_linha(
                headers,
                dados_novos
            )

            if len(nova_linha) != len(headers):

                st.error(
                    "❌ Quantidade de dados diferente "
                    "da quantidade de colunas."
                )

                st.stop()

            worksheet.append_row(
                nova_linha,
                value_input_option="USER_ENTERED"
            )

            st.cache_data.clear()

            st.session_state[
                "mensagem_sucesso"
            ] = (
                "🎉 Cadastro salvo com sucesso! "
                f"Matrícula: {matricula} | "
                f"Nome: {nome}"
            )

            st.rerun()

        except Exception as erro:

            st.error(
                "❌ Erro ao salvar o cadastro."
            )

            st.exception(erro)


# ============================================================
# EDIÇÃO
# ============================================================

with st.expander(
    "✏️ **Editar Registro Existente**",
    expanded=False
):

    if df.empty:

        st.info(
            "Não existem registros para editar."
        )

    else:

        opcoes = []

        for _, linha in df.iterrows():

            matricula = texto(
                linha.get(
                    "Matrícula",
                    ""
                )
            ).strip()

            nome = texto(
                linha.get(
                    "Nome",
                    ""
                )
            ).strip()

            if matricula:

                opcoes.append(
                    f"{matricula} - {nome}"
                )

        selecionado = st.selectbox(
            "Selecione o militar:",
            [""] + opcoes,
            key="militar_edicao"
        )

        if selecionado:

            matricula_editar = (
                selecionado
                .split(" - ", 1)[0]
                .strip()
            )

            registros = df[
                df["Matrícula"]
                .astype(str)
                .str.strip()
                == matricula_editar
            ]

            if registros.empty:

                st.error(
                    "❌ Registro não localizado."
                )

            else:

                dados_atual = (
                    registros
                    .iloc[0]
                    .to_dict()
                )

                st.info(
                    "Editando: "
                    f"**{dados_atual.get('Nome', '')}** "
                    f"| Matrícula: "
                    f"**{matricula_editar}**"
                )

                with st.form(
                    "form_edicao",
                    clear_on_submit=False
                ):

                    dados_editados = criar_formulario(
                        dados_atual,
                        "edicao"
                    )

                    # Matrícula é a chave
                    dados_editados[
                        "Matrícula"
                    ] = matricula_editar

                    atualizar = st.form_submit_button(
                        "🔄 ATUALIZAR REGISTRO",
                        type="primary",
                        use_container_width=True
                    )

                if atualizar:

                    try:

                        row_idx = (
                            localizar_linha_por_matricula(
                                worksheet,
                                matricula_editar
                            )
                        )

                        if not row_idx:

                            st.error(
                                "❌ A matrícula não foi encontrada "
                                "diretamente na Página1."
                            )

                            st.stop()

                        nome_anterior = texto(
                            dados_atual.get(
                                "Nome",
                                ""
                            )
                        ).strip()

                        nome_novo = texto(
                            dados_editados.get(
                                "Nome",
                                ""
                            )
                        ).strip()

                        # Proteção fundamental
                        if not nome_novo:

                            st.error(
                                "❌ O campo Nome ficou vazio. "
                                "A atualização foi CANCELADA "
                                "para evitar apagar o cadastro."
                            )

                            st.stop()

                        linha_atualizada = montar_linha(
                            headers,
                            dados_editados
                        )

                        if (
                            len(linha_atualizada)
                            != len(headers)
                        ):

                            st.error(
                                "❌ Quantidade de campos incompatível. "
                                "Atualização cancelada."
                            )

                            st.stop()

                        # ====================================================
                        # CORREÇÃO DO ERRO DO F-STRING
                        # ====================================================

                        ultima_coluna_a1 = (
                            gspread.utils.rowcol_to_a1(
                                row_idx,
                                len(headers)
                            )
                        )

                        intervalo = (
                            f"A{row_idx}:{ultima_coluna_a1}"
                        )

                        # ====================================================
                        # ATUALIZA SOMENTE A LINHA CORRETA
                        # ====================================================

                        worksheet.update(
                            intervalo,
                            [linha_atualizada],
                            value_input_option="USER_ENTERED"
                        )

                        st.cache_data.clear()

                        st.session_state[
                            "mensagem_sucesso"
                        ] = (
                            "✅ Registro atualizado com sucesso! "
                            f"Matrícula: {matricula_editar} | "
                            f"Nome: {nome_novo}"
                        )

                        st.rerun()

                    except Exception as erro:

                        st.error(
                            "❌ Erro ao atualizar o registro."
                        )

                        st.exception(erro)


# ============================================================
# EXCLUSÃO
# ============================================================

with st.expander(
    "🗑️ **Excluir Registro**",
    expanded=False
):

    st.warning(
        "⚠️ A exclusão é permanente."
    )

    if df.empty:

        st.info(
            "Não existem registros."
        )

    else:

        opcoes_exclusao = []

        for _, linha in df.iterrows():

            matricula = texto(
                linha.get(
                    "Matrícula",
                    ""
                )
            ).strip()

            nome = texto(
                linha.get(
                    "Nome",
                    ""
                )
            ).strip()

            if matricula:

                opcoes_exclusao.append(
                    f"{matricula} - {nome}"
                )

        selecionado_excluir = st.selectbox(
            "Selecione o militar:",
            [""] + opcoes_exclusao,
            key="militar_exclusao"
        )

        if selecionado_excluir:

            matricula_excluir = (
                selecionado_excluir
                .split(" - ", 1)[0]
                .strip()
            )

            registro = df[
                df["Matrícula"]
                .astype(str)
                .str.strip()
                == matricula_excluir
            ]

            st.dataframe(
                registro,
                use_container_width=True,
                hide_index=True
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir "
                "permanentemente este registro.",
                key="confirmar_exclusao"
            )

            excluir = st.button(
                "🔴 EXCLUIR REGISTRO",
                type="primary",
                disabled=not confirmar,
                key="botao_excluir"
            )

            if excluir:

                try:

                    row_idx = (
                        localizar_linha_por_matricula(
                            worksheet,
                            matricula_excluir
                        )
                    )

                    if not row_idx:

                        st.error(
                            "❌ Matrícula não encontrada."
                        )

                        st.stop()

                    worksheet.delete_rows(
                        row_idx
                    )

                    st.cache_data.clear()

                    st.session_state[
                        "mensagem_sucesso"
                    ] = (
                        "🗑️ Registro excluído com sucesso. "
                        f"Matrícula: {matricula_excluir}"
                    )

                    st.rerun()

                except Exception as erro:

                    st.error(
                        "❌ Erro ao excluir registro."
                    )

                    st.exception(erro)


# ============================================================
# DIAGNÓSTICO
# ============================================================

with st.expander(
    "🔧 **Diagnóstico da Conexão**",
    expanded=False
):

    st.write(
        "Planilha:",
        st.secrets["SHEET_ID"]
    )

    st.write(
        "Aba:",
        "Página1"
    )

    st.write(
        "Colunas encontradas:",
        len(headers)
    )

    st.write(
        "Registros encontrados:",
        len(df)
    )

    st.write(
        "Registros após filtros:",
        len(df_filtrado)
    )

    if headers == HEADERS_ESPERADOS:

        st.success(
            "✅ A estrutura da Página1 está "
            "exatamente de acordo com o sistema."
        )

    else:

        st.warning(
            "⚠️ A ordem dos cabeçalhos é diferente "
            "da lista original. Isso não impede o "
            "funcionamento, pois os dados são "
            "gravados pelo nome do cabeçalho."
        )

        st.write(
            "Cabeçalhos encontrados:"
        )

        for i, header in enumerate(
            headers,
            start=1
        ):

            st.write(
                f"{i}. {header}"
            )
