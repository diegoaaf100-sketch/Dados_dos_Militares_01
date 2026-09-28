import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import re


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="DGP - Dados dos Militares",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ============================================================
# CABEÇALHOS ESPERADOS
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
# FUNÇÕES BÁSICAS
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


def normalizar(valor):
    return texto(valor).strip().upper()


def normalizar_matricula(valor):
    return normalizar(valor)


# ============================================================
# CABEÇALHOS DUPLICADOS
# ============================================================

def tornar_headers_unicos(headers):

    usados = {}
    resultado = []

    for header in headers:

        base = texto(header).strip()

        if not base:
            base = "COLUNA SEM NOME"

        if base not in usados:

            usados[base] = 1
            resultado.append(base)

        else:

            usados[base] += 1

            resultado.append(
                f"{base} [{usados[base]}]"
            )

    return resultado


def base_header(header):

    valor = texto(header).strip()

    match = re.match(
        r"^(.*) \[(\d+)\]$",
        valor
    )

    if match:
        return match.group(1)

    return valor


# ============================================================
# LOGIN
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

            st.session_state[
                "password_correct"
            ] = True

            st.session_state.pop(
                "password",
                None
            )

            st.session_state.pop(
                "username",
                None
            )

        else:

            st.session_state[
                "password_correct"
            ] = False

    if st.session_state.get(
        "password_correct",
        False
    ):
        return True

    st.title(
        "🔒 Acesso Restrito ao Dashboard"
    )

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

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
            on_click=password_entered,
            type="primary",
            use_container_width=True
        )

        if (
            "password_correct" in st.session_state
            and not st.session_state[
                "password_correct"
            ]
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

    credentials = (
        Credentials
        .from_service_account_info(
            st.secrets[
                "gcp_service_account"
            ],
            scopes=SCOPES
        )
    )

    return gspread.authorize(
        credentials
    )


def get_sheet():

    sheet_id = st.secrets["SHEET_ID"]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(
        sheet_id
    )

    return spreadsheet.worksheet(
        "Página1"
    )


# ============================================================
# LEITURA DA PLANILHA
# ============================================================

@st.cache_data(ttl=5)
def carregar_dados():

    worksheet = get_sheet()

    valores = worksheet.get_all_values()

    if not valores:

        return pd.DataFrame(
            columns=HEADERS_ESPERADOS
        )

    headers_originais = [
        texto(x).strip()
        for x in valores[0]
    ]

    headers_internos = tornar_headers_unicos(
        headers_originais
    )

    dados = valores[1:]

    quantidade = len(
        headers_originais
    )

    linhas_corrigidas = []

    for linha in dados:

        linha = list(linha)

        if len(linha) < quantidade:

            linha += [
                ""
            ] * (
                quantidade - len(linha)
            )

        elif len(linha) > quantidade:

            linha = linha[
                :quantidade
            ]

        linhas_corrigidas.append(
            linha
        )

    df = pd.DataFrame(
        linhas_corrigidas,
        columns=headers_internos
    )

    return df


# ============================================================
# ESTRUTURA DA PLANILHA
# ============================================================

def obter_headers_planilha(worksheet):

    headers = [
        texto(x).strip()
        for x in worksheet.row_values(1)
    ]

    if not headers:

        raise ValueError(
            "A primeira linha da Página1 "
            "está vazia."
        )

    return headers


def verificar_estrutura(worksheet):

    headers = obter_headers_planilha(
        worksheet
    )

    duplicados = []

    vistos = set()

    for header in headers:

        if header in vistos:

            if header not in duplicados:
                duplicados.append(header)

        vistos.add(header)

    faltantes = [
        x
        for x in HEADERS_ESPERADOS
        if x not in headers
    ]

    if faltantes:

        raise ValueError(
            "As seguintes colunas esperadas "
            "não foram encontradas na Página1:\n\n"
            + "\n".join(
                f"- {x}"
                for x in faltantes
            )
        )

    return headers, duplicados


# ============================================================
# LOCALIZAÇÃO DE COLUNAS
# ============================================================

def localizar_coluna(
    headers,
    nome,
    ocorrencia=1
):

    contador = 0

    for i, header in enumerate(headers):

        if texto(header).strip() == nome:

            contador += 1

            if contador == ocorrencia:
                return i + 1

    return None


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
            "A coluna Matrícula não foi "
            "encontrada na Página1."
        )

    indice = coluna - 1

    procurada = normalizar_matricula(
        matricula
    )

    for numero_linha, linha in enumerate(
        valores[1:],
        start=2
    ):

        if indice < len(linha):

            atual = normalizar_matricula(
                linha[indice]
            )

            if atual == procurada:

                return numero_linha

    return None


# ============================================================
# DADOS DA LINHA ORIGINAL
# ============================================================

def obter_linha_planilha(
    worksheet,
    numero_linha
):

    valores = worksheet.get_all_values()

    if numero_linha <= 0:
        return []

    if numero_linha > len(valores):
        return []

    headers = valores[0]

    linha = list(
        valores[numero_linha - 1]
    )

    if len(linha) < len(headers):

        linha += [
            ""
        ] * (
            len(headers) - len(linha)
        )

    elif len(linha) > len(headers):

        linha = linha[
            :len(headers)
        ]

    return linha


# ============================================================
# NOVO CADASTRO
# ============================================================

def montar_linha_nova(
    headers,
    dados
):

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
# ATUALIZAÇÃO SEGURA
# ============================================================

def atualizar_linha_com_seguranca(
    headers,
    linha_original,
    dados_editados
):

    nova_linha = list(
        linha_original
    )

    if len(nova_linha) < len(headers):

        nova_linha += [
            ""
        ] * (
            len(headers) - len(nova_linha)
        )

    for campo, valor in dados_editados.items():

        posicao = localizar_coluna(
            headers,
            campo,
            ocorrencia=1
        )

        if posicao is None:
            continue

        indice = posicao - 1

        nova_linha[indice] = texto(
            valor
        )

    return nova_linha


# ============================================================
# CAMPOS DO FORMULÁRIO
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
    # ABA 1
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

            sexo_atual = normalizar(
                dados.get(
                    "SEXO",
                    ""
                )
            )

            opcoes_sexo = [
                "",
                "MASCULINO",
                "FEMININO"
            ]

            resultado["SEXO"] = st.selectbox(
                "SEXO",
                opcoes_sexo,
                index=(
                    opcoes_sexo.index(
                        sexo_atual
                    )
                    if sexo_atual in opcoes_sexo
                    else 0
                ),
                key=f"{prefixo}_sexo"
            )

            raca_atual = normalizar(
                dados.get(
                    "Raça/Cor",
                    ""
                )
            )

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
                    opcoes_raca.index(
                        raca_atual
                    )
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
    # ABA 2
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

            resultado["Tempo de serviço (anos)"] = campo_texto(
                "Tempo de serviço (anos)",
                dados,
                f"{prefixo}_tempo_anos",
                "Tempo de serviço (anos)"
            )

            resultado["Tempo de serviço (ano, mês, dias)"] = campo_texto(
                "Tempo de serviço (ano, mês, dias)",
                dados,
                f"{prefixo}_tempo_amd",
                "Tempo de serviço (ano, mês, dias)"
            )

            resultado["Tempo de serviço (dias)"] = campo_texto(
                "Tempo de serviço (dias)",
                dados,
                f"{prefixo}_tempo_dias",
                "Tempo de serviço (dias)"
            )

            resultado["Tempo na OBM atual"] = campo_texto(
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
    # ABA 3
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

            onus_atual = normalizar(
                dados.get(
                    "Ônus para Origem",
                    ""
                )
            )

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
                    opcoes_onus.index(
                        onus_atual
                    )
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
    # ABA 4
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

            resultado[
                "INÍCIO DA LTIP"
            ] = campo_texto(
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
    # ABA 5
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
# SIDEBAR - CONTROLES
# ============================================================

st.sidebar.success(
    "✅ Autenticado com sucesso!"
)

if st.sidebar.button(
    "🚪 Sair / Logout",
    use_container_width=True
):

    st.session_state[
        "password_correct"
    ] = False

    st.rerun()


if st.sidebar.button(
    "🔄 Atualizar dados agora",
    use_container_width=True
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
    """
    <h1 style="text-align:center;">
        DGP - Dados dos Militares
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# CARREGA PLANILHA
# ============================================================

try:

    worksheet = get_sheet()

    headers, duplicados = verificar_estrutura(
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
# AVISO DE DUPLICADOS
# ============================================================

if duplicados:

    st.warning(
        "⚠️ A Página1 possui cabeçalhos duplicados. "
        "O Dashboard tratará essas colunas internamente "
        "sem alterar a planilha."
    )

    with st.expander(
        "Ver cabeçalhos duplicados"
    ):

        for item in duplicados:

            st.write(
                f"- `{item}`"
            )


# ============================================================
# MENSAGEM DE SUCESSO
# ============================================================

if st.session_state.get(
    "mensagem_sucesso"
):

    st.success(
        st.session_state[
            "mensagem_sucesso"
        ]
    )

    del st.session_state[
        "mensagem_sucesso"
    ]


# ============================================================
# FILTROS LATERAIS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.header(
    "🔎 Filtros"
)

st.sidebar.caption(
    "Use os filtros abaixo para refinar "
    "os registros e atualizar os gráficos."
)


# ============================================================
# BUSCA GERAL
# ============================================================

busca = st.sidebar.text_input(
    "🔍 Busca geral",
    placeholder="Nome, matrícula, OME..."
)


# ============================================================
# FUNÇÃO PARA OBTER VALORES
# ============================================================

def valores_coluna(
    df,
    coluna
):

    if coluna not in df.columns:
        return []

    valores = (
        df[coluna]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    valores = [
        x
        for x in valores.unique()
        if x
    ]

    return sorted(
        valores,
        key=lambda x: x.upper()
    )


# ============================================================
# FILTRO INDIVIDUAL PARA CADA COLUNA
# ============================================================

filtros_colunas = {}


with st.sidebar.expander(
    "📋 Filtros por coluna",
    expanded=True
):

    for indice, coluna in enumerate(
        df.columns
    ):

        valores = valores_coluna(
            df,
            coluna
        )

        if not valores:
            continue

        # ----------------------------------------------------
        # Chave interna segura
        # ----------------------------------------------------

        chave = (
            "filtro_coluna_"
            + str(indice)
        )

        # ----------------------------------------------------
        # Para colunas com poucos valores:
        # MULTISELECT
        # ----------------------------------------------------

        if len(valores) <= 100:

            selecionados = st.multiselect(
                coluna,
                valores,
                key=chave,
                placeholder="Todos"
            )

            filtros_colunas[coluna] = (
                selecionados
            )

        # ----------------------------------------------------
        # Para colunas com muitos valores:
        # BUSCA POR TEXTO
        # ----------------------------------------------------

        else:

            texto_filtro = st.text_input(
                coluna,
                key=chave,
                placeholder="Digite para filtrar..."
            )

            filtros_colunas[coluna] = (
                texto_filtro
            )


# ============================================================
# LIMPAR FILTROS
# ============================================================

if st.sidebar.button(
    "🧹 LIMPAR TODOS OS FILTROS",
    use_container_width=True
):

    # Remove somente as chaves de filtros
    # para não interferir no restante do sistema.

    chaves_remover = []

    for chave in st.session_state.keys():

        if chave.startswith(
            "filtro_coluna_"
        ):

            chaves_remover.append(
                chave
            )

    for chave in chaves_remover:

        del st.session_state[
            chave
        ]

    # Limpa a busca geral.

    if "busca_geral" in st.session_state:

        del st.session_state[
            "busca_geral"
        ]

    st.rerun()


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df.copy()


for coluna, filtro in filtros_colunas.items():

    if coluna not in df_filtrado.columns:
        continue

    # --------------------------------------------------------
    # MULTISELECT
    # --------------------------------------------------------

    if isinstance(filtro, list):

        if filtro:

            df_filtrado = df_filtrado[
                df_filtrado[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
                .isin(filtro)
            ]

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    elif isinstance(filtro, str):

        termo_coluna = filtro.strip()

        if termo_coluna:

            df_filtrado = df_filtrado[
                df_filtrado[coluna]
                .fillna("")
                .astype(str)
                .str.contains(
                    termo_coluna,
                    case=False,
                    regex=False
                )
            ]


# ============================================================
# BUSCA GERAL
# ============================================================

if busca.strip():

    termo = busca.strip().lower()

    mascara = pd.Series(
        False,
        index=df_filtrado.index
    )

    for coluna in df_filtrado.columns:

        mascara = (
            mascara
            |
            df_filtrado[coluna]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(
                termo,
                regex=False
            )
        )

    df_filtrado = df_filtrado[
        mascara
    ]


# ============================================================
# INDICADORES
# ============================================================

st.subheader(
    "📊 Resumo"
)

m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "👥 Total de registros",
        len(df)
    )

with m2:

    st.metric(
        "🔎 Registros filtrados",
        len(df_filtrado)
    )

with m3:

    if "OME" in df.columns:

        st.metric(
            "🏢 OME",
            df_filtrado["OME"]
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

    else:

        st.metric(
            "🏢 OME",
            0
        )

with m4:

    if "Posto/ Grad" in df.columns:

        st.metric(
            "🎖️ Postos/Grad.",
            df_filtrado["Posto/ Grad"]
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

    else:

        st.metric(
            "🎖️ Postos/Grad.",
            0
        )


# ============================================================
# GRÁFICOS
# ============================================================

st.subheader(
    "📈 Gráficos"
)

graf1, graf2 = st.columns(2)


# ============================================================
# GRÁFICO 1 - POSTO/GRAD
# ============================================================

with graf1:

    if (
        "Posto/ Grad" in df_filtrado.columns
        and not df_filtrado.empty
    ):

        contagem_posto = (
            df_filtrado[
                "Posto/ Grad"
            ]
            .replace(
                "",
                "Não informado"
            )
            .value_counts()
            .head(20)
        )

        st.markdown(
            "### 🎖️ Militares por Posto/Grad."
        )

        st.bar_chart(
            contagem_posto,
            use_container_width=True
        )

    else:

        st.info(
            "Não há dados suficientes "
            "para o gráfico de Posto/Grad."
        )


# ============================================================
# GRÁFICO 2 - OME
# ============================================================

with graf2:

    if (
        "OME" in df_filtrado.columns
        and not df_filtrado.empty
    ):

        contagem_ome = (
            df_filtrado[
                "OME"
            ]
            .replace(
                "",
                "Não informado"
            )
            .value_counts()
            .head(20)
        )

        st.markdown(
            "### 🏢 Militares por OME"
        )

        st.bar_chart(
            contagem_ome,
            use_container_width=True
        )

    else:

        st.info(
            "Não há dados suficientes "
            "para o gráfico de OME."
        )


# ============================================================
# VISUALIZAÇÃO
# ============================================================

st.markdown("---")

st.subheader(
    "📋 Visualização dos Registros"
)

st.caption(
    f"Conectado diretamente à aba Página1 • "
    f"{len(df_filtrado)} registros exibidos • "
    f"{len(headers)} colunas"
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

            existente = (
                localizar_linha_por_matricula(
                    worksheet,
                    matricula
                )
            )

            if existente:

                st.error(
                    f"❌ A matrícula "
                    f"**{matricula}** já existe "
                    f"na linha {existente}."
                )

                st.stop()

            nova_linha = montar_linha_nova(
                headers,
                dados_novos
            )

            if len(nova_linha) != len(headers):

                st.error(
                    "❌ Quantidade de campos "
                    "incompatível."
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

        if (
            "Matrícula" not in df.columns
            or "Nome" not in df.columns
        ):

            st.error(
                "A planilha precisa possuir "
                "as colunas Matrícula e Nome."
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

                        dados_editados = (
                            criar_formulario(
                                dados_atual,
                                "edicao"
                            )
                        )

                        dados_editados[
                            "Matrícula"
                        ] = matricula_editar

                        atualizar = (
                            st.form_submit_button(
                                "🔄 ATUALIZAR REGISTRO",
                                type="primary",
                                use_container_width=True
                            )
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
                                    "❌ A matrícula não foi "
                                    "encontrada na Página1."
                                )

                                st.stop()

                            nome_novo = texto(
                                dados_editados.get(
                                    "Nome",
                                    ""
                                )
                            ).strip()

                            if not nome_novo:

                                st.error(
                                    "❌ O campo Nome ficou vazio. "
                                    "A atualização foi cancelada "
                                    "para proteger o cadastro."
                                )

                                st.stop()

                            linha_original = (
                                obter_linha_planilha(
                                    worksheet,
                                    row_idx
                                )
                            )

                            linha_atualizada = (
                                atualizar_linha_com_seguranca(
                                    headers,
                                    linha_original,
                                    dados_editados
                                )
                            )

                            if (
                                len(linha_atualizada)
                                != len(headers)
                            ):

                                st.error(
                                    "❌ Quantidade de colunas "
                                    "incompatível. Atualização "
                                    "cancelada."
                                )

                                st.stop()

                            coluna_nome = localizar_coluna(
                                headers,
                                "Nome"
                            )

                            if coluna_nome is None:

                                st.error(
                                    "❌ Coluna Nome não encontrada."
                                )

                                st.stop()

                            nome_gravado = texto(
                                linha_atualizada[
                                    coluna_nome - 1
                                ]
                            ).strip()

                            if not nome_gravado:

                                st.error(
                                    "❌ PROTEÇÃO ATIVADA: "
                                    "o Nome ficaria vazio. "
                                    "A atualização foi cancelada."
                                )

                                st.stop()

                            primeira_celula = (
                                gspread.utils.rowcol_to_a1(
                                    row_idx,
                                    1
                                )
                            )

                            ultima_celula = (
                                gspread.utils.rowcol_to_a1(
                                    row_idx,
                                    len(headers)
                                )
                            )

                            intervalo = (
                                f"{primeira_celula}:"
                                f"{ultima_celula}"
                            )

                            worksheet.update(
                                intervalo,
                                [linha_atualizada],
                                value_input_option="USER_ENTERED"
                            )

                            st.cache_data.clear()

                            st.session_state[
                                "mensagem_sucesso"
                            ] = (
                                "✅ Registro atualizado "
                                "com sucesso! "
                                f"Matrícula: "
                                f"{matricula_editar} | "
                                f"Nome: {nome_novo}"
                            )

                            st.rerun()

                        except Exception as erro:

                            st.error(
                                "❌ Erro ao atualizar "
                                "o registro."
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

    if duplicados:

        st.warning(
            "⚠️ Existem cabeçalhos duplicados."
        )

        st.write(
            "Cabeçalhos duplicados:"
        )

        for item in duplicados:

            st.write(
                f"- {item}"
            )

        st.info(
            "O sistema trata os nomes duplicados "
            "internamente sem alterar a Página1."
        )

    else:

        st.success(
            "✅ Não existem cabeçalhos duplicados."
        )

    faltantes = [
        x
        for x in HEADERS_ESPERADOS
        if x not in headers
    ]

    if not faltantes:

        st.success(
            "✅ Todas as colunas esperadas "
            "foram encontradas."
        )

    else:

        st.error(
            "❌ Existem colunas esperadas "
            "que não foram encontradas."
        )

        for item in faltantes:

            st.write(
                f"- {item}"
            )

    st.markdown("---")

    st.write(
        "### Cabeçalhos encontrados na Página1"
    )

    for i, header in enumerate(
        headers,
        start=1
    ):

        st.write(
            f"{i}. {header}"
        )
