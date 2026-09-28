import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="DGP - Dados dos Militares",
    layout="wide"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

NOME_ABA = "Página1"


# ============================================================
# AUTENTICAÇÃO DO USUÁRIO
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
                "username",
                None
            )

            st.session_state.pop(
                "password",
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
            on_click=password_entered
        )

        if (
            "password_correct"
            in st.session_state
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
# CONEXÃO COM GOOGLE SHEETS
# ============================================================

def get_gspread_client():

    credentials = (
        Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
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

    sheet = spreadsheet.worksheet(
        NOME_ABA
    )

    return sheet


# ============================================================
# LEITURA DOS DADOS
# ============================================================

@st.cache_data(ttl=5)
def carregar_dados():

    sheet = get_sheet()

    valores = sheet.get_all_values()

    if not valores:

        return pd.DataFrame()

    cabecalhos = [
        str(x).strip()
        for x in valores[0]
    ]

    linhas = valores[1:]

    # Garante que todas as linhas tenham
    # exatamente a mesma quantidade de colunas.
    linhas_corrigidas = []

    for linha in linhas:

        linha = list(linha)

        if len(linha) < len(cabecalhos):

            linha.extend(
                [""] *
                (
                    len(cabecalhos)
                    - len(linha)
                )
            )

        elif len(linha) > len(cabecalhos):

            linha = linha[
                :len(cabecalhos)
            ]

        linhas_corrigidas.append(
            linha
        )

    return pd.DataFrame(
        linhas_corrigidas,
        columns=cabecalhos
    )


# ============================================================
# FUNÇÕES AUXILIARES
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


def valor_existente(dados, coluna):

    if dados is None:
        return ""

    return texto(
        dados.get(
            coluna,
            ""
        )
    )


def limpar_cache():

    st.cache_data.clear()


# ============================================================
# FUNÇÃO PARA MONTAR FORMULÁRIO
# ============================================================

def formulario_militar(
    dados=None,
    prefixo="novo"
):

    if dados is None:
        dados = {}

    def v(coluna):

        return valor_existente(
            dados,
            coluna
        )

    # ========================================================
    # ABA 1
    # ========================================================

    tab_pessoal, tab_lotacao, tab_cessao, tab_ltip, tab_outros = st.tabs(
        [
            "👤 Identificação & Pessoal",
            "🏢 Lotação & Promoção",
            "🔄 Cessão & Movimentação",
            "⏳ LTIP & Afastamentos",
            "📝 Documentos & Observações",
        ]
    )

    # ========================================================
    # PESSOAL
    # ========================================================

    with tab_pessoal:

        c1, c2, c3 = st.columns(3)

        with c1:

            num_funcional = st.text_input(
                "nº Funcional:",
                value=v("nº Funcional"),
                key=f"{prefixo}_num_funcional"
            )

            matricula = st.text_input(
                "Matrícula:",
                value=v("Matrícula"),
                key=f"{prefixo}_matricula"
            )

            cpf_ponto = st.text_input(
                "CPF.:",
                value=v("CPF."),
                key=f"{prefixo}_cpf_ponto"
            )

            cpf = st.text_input(
                "CPF:",
                value=v("CPF"),
                key=f"{prefixo}_cpf"
            )

            num_ident = st.text_input(
                "Nº IDENT.:",
                value=v("Nº IDENT."),
                key=f"{prefixo}_num_ident"
            )

        with c2:

            nome = st.text_input(
                "Nome:",
                value=v("Nome"),
                key=f"{prefixo}_nome"
            )

            nome_guerra = st.text_input(
                "Nome de Guerra:",
                value=v("Nome de Guerra"),
                key=f"{prefixo}_nome_guerra"
            )

            sexo_atual = v("SEXO").upper()

            opcoes_sexo = [
                "",
                "MASCULINO",
                "FEMININO"
            ]

            idx_sexo = (
                opcoes_sexo.index(
                    sexo_atual
                )
                if sexo_atual
                in opcoes_sexo
                else 0
            )

            sexo = st.selectbox(
                "SEXO:",
                opcoes_sexo,
                index=idx_sexo,
                key=f"{prefixo}_sexo"
            )

            raca_atual = v(
                "Raça/Cor"
            ).upper()

            opcoes_raca = [
                "",
                "BRANCA",
                "PRETA",
                "PARDA",
                "AMARELA",
                "INDÍGENA"
            ]

            idx_raca = (
                opcoes_raca.index(
                    raca_atual
                )
                if raca_atual
                in opcoes_raca
                else 0
            )

            raca_cor = st.selectbox(
                "Raça/Cor:",
                opcoes_raca,
                index=idx_raca,
                key=f"{prefixo}_raca"
            )

        with c3:

            posto_grad = st.text_input(
                "Posto/ Grad:",
                value=v("Posto/ Grad"),
                key=f"{prefixo}_posto_grad"
            )

            fones = st.text_input(
                "Fones:",
                value=v("Fones"),
                key=f"{prefixo}_fones"
            )

            ano_ingresso = st.text_input(
                "Ano de ingresso:",
                value=v("Ano de ingresso"),
                key=f"{prefixo}_ano_ingresso"
            )

            data_praca = st.text_input(
                "Data de praça:",
                value=v("Data de praça"),
                key=f"{prefixo}_data_praca"
            )

    # ========================================================
    # LOTAÇÃO
    # ========================================================

    with tab_lotacao:

        c1, c2, c3 = st.columns(3)

        with c1:

            ome = st.text_input(
                "OME:",
                value=v("OME"),
                key=f"{prefixo}_ome"
            )

            ome_qod = st.text_input(
                "OME QOD:",
                value=v("OME QOD"),
                key=f"{prefixo}_ome_qod"
            )

            atividade = st.text_input(
                "Atividade:",
                value=v("Atividade"),
                key=f"{prefixo}_atividade"
            )

            municipio = st.text_input(
                "Município:",
                value=v("Município"),
                key=f"{prefixo}_municipio"
            )

            regiao = st.text_input(
                "Região:",
                value=v("Região"),
                key=f"{prefixo}_regiao"
            )

        with c2:

            tempo_servico_anos = st.text_input(
                "Tempo de serviço (anos):",
                value=v(
                    "Tempo de serviço (anos)"
                ),
                key=f"{prefixo}_tempo_anos"
            )

            tempo_servico_amd = st.text_input(
                "Tempo de serviço (ano, mês, dias):",
                value=v(
                    "Tempo de serviço (ano, mês, dias)"
                ),
                key=f"{prefixo}_tempo_amd"
            )

            tempo_servico_dias = st.text_input(
                "Tempo de serviço (dias):",
                value=v(
                    "Tempo de serviço (dias)"
                ),
                key=f"{prefixo}_tempo_dias"
            )

            tempo_obm_atual = st.text_input(
                "Tempo na OBM atual:",
                value=v(
                    "Tempo na OBM atual"
                ),
                key=f"{prefixo}_tempo_obm"
            )

        with c3:

            data_ult_promocao = st.text_input(
                "Data da última promoção ou Implant. PCNH:",
                value=v(
                    "Data da última promoção ou Implant. PCNH"
                ),
                key=f"{prefixo}_data_promocao"
            )

            principio_ult_promocao = st.text_input(
                "Princípio da última promoção:",
                value=v(
                    "Princípio da última promoção"
                ),
                key=f"{prefixo}_principio"
            )

            tempo_posto_atual_dias = st.text_input(
                "Tempo no Posto/Grad. atual EM DIAS:",
                value=v(
                    "Tempo no Posto/Grad. atual EM DIAS"
                ),
                key=f"{prefixo}_tempo_posto"
            )

    # ========================================================
    # CESSÃO
    # ========================================================

    with tab_cessao:

        c1, c2, c3 = st.columns(3)

        with c1:

            data_mov_sp = st.text_input(
                "Data da Movimentação em SP:",
                value=v(
                    "Data da Movimentação em SP"
                ),
                key=f"{prefixo}_data_mov_sp"
            )

            ome_anterior = st.text_input(
                "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:",
                value=v(
                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO"
                ),
                key=f"{prefixo}_ome_anterior"
            )

            data_chegada = st.text_input(
                "Data de chegada na OBM Anteior:",
                value=v(
                    "Data de chegada na OBM Anteior"
                ),
                key=f"{prefixo}_data_chegada"
            )

            movimentado = st.text_input(
                "Movimentado (apagar antes de atualizar o SP):",
                value=v(
                    "Movimentado (apagar antes de atualizar o SP)"
                ),
                key=f"{prefixo}_movimentado"
            )

        with c2:

            orgao = st.text_input(
                "ÓRGÃO:",
                value=v("ÓRGÃO"),
                key=f"{prefixo}_orgao"
            )

            poder = st.text_input(
                "Poder:",
                value=v("Poder"),
                key=f"{prefixo}_poder"
            )

            onus_atual = v(
                "Ônus para Origem"
            ).upper()

            opcoes_onus = [
                "",
                "SIM",
                "NÃO"
            ]

            idx_onus = (
                opcoes_onus.index(
                    onus_atual
                )
                if onus_atual
                in opcoes_onus
                else 0
            )

            onus_origem = st.selectbox(
                "Ônus para Origem:",
                opcoes_onus,
                index=idx_onus,
                key=f"{prefixo}_onus"
            )

            inicio_cessao = st.text_input(
                "Início da Cessão ou requisição:",
                value=v(
                    "Início da Cessão ou requisição"
                ),
                key=f"{prefixo}_inicio_cessao"
            )

        with c3:

            renovacao = st.text_input(
                "Renovação de cessão - Atos/Portarias/Documentos:",
                value=v(
                    "Renovação de cessão - Atos/Portarias/Documentos"
                ),
                key=f"{prefixo}_renovacao"
            )

            doe = st.text_input(
                "DOE/BGSDS de renovação:",
                value=v(
                    "DOE/BGSDS de renovação"
                ),
                key=f"{prefixo}_doe"
            )

            sei = st.text_input(
                "SEI deslig.:",
                value=v("SEI deslig."),
                key=f"{prefixo}_sei"
            )

    # ========================================================
    # LTIP
    # ========================================================

    with tab_ltip:

        c1, c2 = st.columns(2)

        with c1:

            afastamentos = st.text_area(
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
                "ININTERRUPTOS, PUBLICADOS EM SP:",
                value=v(
                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
                    "ININTERRUPTOS, PUBLICADOS EM SP"
                ),
                key=f"{prefixo}_afastamentos"
            )

            inicio_ltip = st.text_input(
                "INÍCIO DA LTIP:",
                value=v("INÍCIO DA LTIP"),
                key=f"{prefixo}_inicio_ltip"
            )

            termino_ltip = st.text_input(
                "TÉRMINO DA LTIP (inserir data de apresentação):",
                value=v(
                    "TÉRMINO DA LTIP (inserir data de apresentação)"
                ),
                key=f"{prefixo}_termino_ltip"
            )

        with c2:

            somatorio_anos = st.text_input(
                "Somatório LTIP gozada em anos:",
                value=v(
                    "Somatório LTIP gozada em anos"
                ),
                key=f"{prefixo}_somatorio_anos"
            )

            somatorio_amd = st.text_input(
                "Somatório LTIP gozada em anos/meses/dias:",
                value=v(
                    "Somatório LTIP gozada em anos/meses/dias"
                ),
                key=f"{prefixo}_somatorio_amd"
            )

            somatorio_dias = st.text_input(
                "Somatório de todas LTIP gozadas em dias:",
                value=v(
                    "Somatório de todas LTIP gozadas em dias"
                ),
                key=f"{prefixo}_somatorio_dias"
            )

            total_ltip = st.text_input(
                "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:",
                value=v(
                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad."
                ),
                key=f"{prefixo}_total_ltip"
            )

    # ========================================================
    # DOCUMENTOS
    # ========================================================

    with tab_outros:

        c1, c2 = st.columns(2)

        with c1:

            ato = st.text_input(
                "Ato:",
                value=v("Ato"),
                key=f"{prefixo}_ato"
            )

            doc_publicacao = st.text_input(
                "Doc. Publicação:",
                value=v("Doc. Publicação"),
                key=f"{prefixo}_doc_publicacao"
            )

            sp_adicao = st.text_input(
                "SP da Adição:",
                value=v("SP da Adição"),
                key=f"{prefixo}_sp_adicao"
            )

            processo_rr = st.text_input(
                "Processo RR:",
                value=v("Processo RR"),
                key=f"{prefixo}_processo_rr"
            )

        with c2:

            suplemento = st.text_input(
                "Suplemento de Pessoal nº/Ano:",
                value=v(
                    "Suplemento de Pessoal nº/Ano"
                ),
                key=f"{prefixo}_suplemento"
            )

            data_suplemento = st.text_input(
                "Data Suplemento de Pessoal:",
                value=v(
                    "Data Suplemento de Pessoal"
                ),
                key=f"{prefixo}_data_suplemento"
            )

            hoje = st.text_input(
                "Hoje:",
                value=v("Hoje"),
                key=f"{prefixo}_hoje"
            )

            obs = st.text_area(
                "OBS:",
                value=v("OBS"),
                key=f"{prefixo}_obs"
            )

    # ========================================================
    # RETORNO
    # ========================================================

    return {

        "nº Funcional": num_funcional,
        "Matrícula": matricula,
        "CPF.": cpf_ponto,
        "CPF": cpf,
        "Nº IDENT.": num_ident,
        "Nome": nome,
        "Nome de Guerra": nome_guerra,
        "SEXO": sexo,
        "Raça/Cor": raca_cor,
        "Posto/ Grad": posto_grad,
        "Fones": fones,
        "Ano de ingresso": ano_ingresso,
        "Data de praça": data_praca,

        "OME": ome,
        "OME QOD": ome_qod,
        "Atividade": atividade,
        "Município": municipio,
        "Região": regiao,

        "Tempo de serviço (anos)": tempo_servico_anos,
        "Tempo de serviço (ano, mês, dias)": tempo_servico_amd,
        "Tempo de serviço (dias)": tempo_servico_dias,
        "Tempo na OBM atual": tempo_obm_atual,

        "Data da última promoção ou Implant. PCNH":
            data_ult_promocao,

        "Princípio da última promoção":
            principio_ult_promocao,

        "Tempo no Posto/Grad. atual EM DIAS":
            tempo_posto_atual_dias,

        "Data da Movimentação em SP":
            data_mov_sp,

        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO":
            ome_anterior,

        "Data de chegada na OBM Anteior":
            data_chegada,

        "Movimentado (apagar antes de atualizar o SP)":
            movimentado,

        "ÓRGÃO": orgao,
        "Poder": poder,
        "Ônus para Origem": onus_origem,

        "Início da Cessão ou requisição":
            inicio_cessao,

        "Renovação de cessão - Atos/Portarias/Documentos":
            renovacao,

        "DOE/BGSDS de renovação":
            doe,

        "SEI deslig.": sei,

        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP":
            afastamentos,

        "INÍCIO DA LTIP":
            inicio_ltip,

        "TÉRMINO DA LTIP (inserir data de apresentação)":
            termino_ltip,

        "Somatório LTIP gozada em anos":
            somatorio_anos,

        "Somatório LTIP gozada em anos/meses/dias":
            somatorio_amd,

        "Somatório de todas LTIP gozadas em dias":
            somatorio_dias,

        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.":
            total_ltip,

        "Ato": ato,
        "Doc. Publicação": doc_publicacao,
        "SP da Adição": sp_adicao,
        "Processo RR": processo_rr,

        "Suplemento de Pessoal nº/Ano":
            suplemento,

        "Data Suplemento de Pessoal":
            data_suplemento,

        "Hoje": hoje,
        "OBS": obs,
    }


# ============================================================
# FUNÇÃO DE GRAVAÇÃO DE NOVO CADASTRO
# ============================================================

def salvar_novo_cadastro(dados):

    sheet = get_sheet()

    headers = sheet.row_values(1)

    if not headers:

        raise Exception(
            "A primeira linha da Página1 não possui cabeçalhos."
        )

    headers = [
        str(h).strip()
        for h in headers
    ]

    if "Matrícula" not in headers:

        raise Exception(
            "A coluna 'Matrícula' não existe na Página1."
        )

    if "Nome" not in headers:

        raise Exception(
            "A coluna 'Nome' não existe na Página1."
        )

    matricula = texto(
        dados.get("Matrícula")
    ).strip()

    nome = texto(
        dados.get("Nome")
    ).strip()

    if not matricula:

        raise Exception(
            "Informe a Matrícula."
        )

    if not nome:

        raise Exception(
            "Informe o Nome."
        )

    # --------------------------------------------------------
    # Verifica duplicidade
    # --------------------------------------------------------

    coluna_matricula = (
        headers.index("Matrícula")
        + 1
    )

    valores = sheet.col_values(
        coluna_matricula
    )

    matriculas = {
        texto(x).strip()
        for x in valores[1:]
        if texto(x).strip()
    }

    if matricula in matriculas:

        raise Exception(
            f"A matrícula {matricula} já existe."
        )

    # --------------------------------------------------------
    # Monta a linha EXATAMENTE na ordem dos cabeçalhos
    # --------------------------------------------------------

    nova_linha = []

    for header in headers:

        valor = dados.get(
            header,
            ""
        )

        nova_linha.append(
            texto(valor)
        )

    # --------------------------------------------------------
    # Grava
    # --------------------------------------------------------

    sheet.append_row(
        nova_linha,
        value_input_option="USER_ENTERED"
    )

    return True


# ============================================================
# FUNÇÃO DE ATUALIZAÇÃO
# ============================================================

def atualizar_cadastro(
    matricula_original,
    dados_novos
):

    sheet = get_sheet()

    headers = [
        str(h).strip()
        for h in sheet.row_values(1)
    ]

    if not headers:

        raise Exception(
            "A Página1 não possui cabeçalhos."
        )

    if "Matrícula" not in headers:

        raise Exception(
            "A coluna Matrícula não existe."
        )

    # --------------------------------------------------------
    # Localiza pela coluna Matrícula
    # --------------------------------------------------------

    coluna_matricula = (
        headers.index("Matrícula")
        + 1
    )

    valores = sheet.col_values(
        coluna_matricula
    )

    linha_planilha = None

    for numero_linha, valor in enumerate(
        valores,
        start=1
    ):

        if numero_linha == 1:
            continue

        if (
            texto(valor).strip()
            == texto(
                matricula_original
            ).strip()
        ):

            linha_planilha = numero_linha
            break

    if linha_planilha is None:

        raise Exception(
            f"A matrícula "
            f"{matricula_original} "
            f"não foi encontrada."
        )

    # --------------------------------------------------------
    # IMPORTANTE:
    # Lê a linha atual antes de alterar.
    # Isso impede apagar dados existentes.
    # --------------------------------------------------------

    linha_atual = sheet.row_values(
        linha_planilha
    )

    while len(linha_atual) < len(headers):

        linha_atual.append("")

    # --------------------------------------------------------
    # Altera SOMENTE as colunas presentes
    # no formulário.
    # --------------------------------------------------------

    for indice, header in enumerate(
        headers
    ):

        if header in dados_novos:

            valor = dados_novos[
                header
            ]

            linha_atual[
                indice
            ] = texto(valor)

    # Matrícula permanece a original
    linha_atual[
        coluna_matricula - 1
    ] = texto(
        matricula_original
    )

    # --------------------------------------------------------
    # Grava a linha completa já preservada
    # --------------------------------------------------------

    intervalo = (
        f"A{linha_planilha}:"
        f"{gspread.utils.rowcol_to_a1(
            linha_planilha,
            len(headers)
        ).replace(
            str(linha_planilha),
            ""
        )}{linha_planilha}"
    )

    # Forma mais segura para determinar
    # a última coluna.
    ultima_coluna = (
        gspread.utils.rowcol_to_a1(
            1,
            len(headers)
        ).replace("1", "")
    )

    intervalo = (
        f"A{linha_planilha}:"
        f"{ultima_coluna}{linha_planilha}"
    )

    sheet.update(
        intervalo,
        [linha_atual],
        value_input_option="USER_ENTERED"
    )

    return True


# ============================================================
# FUNÇÃO DE EXCLUSÃO
# ============================================================

def excluir_cadastro(
    matricula
):

    sheet = get_sheet()

    headers = [
        str(h).strip()
        for h in sheet.row_values(1)
    ]

    if "Matrícula" not in headers:

        raise Exception(
            "A coluna Matrícula não existe."
        )

    coluna = (
        headers.index("Matrícula")
        + 1
    )

    valores = sheet.col_values(
        coluna
    )

    for numero_linha, valor in enumerate(
        valores,
        start=1
    ):

        if numero_linha == 1:
            continue

        if (
            texto(valor).strip()
            == texto(matricula).strip()
        ):

            sheet.delete_rows(
                numero_linha
            )

            return True

    raise Exception(
        f"Matrícula {matricula} não encontrada."
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.success(
    "Autenticado com sucesso!"
)

if st.sidebar.button(
    "🚪 Sair / Logout"
):

    st.session_state[
        "password_correct"
    ] = False

    st.rerun()


if st.sidebar.button(
    "🔄 Atualizar Dashboard"
):

    limpar_cache()

    st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================

col1, col2, col3 = st.columns(
    [1, 2, 1]
)

with col1:

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
    "DGP - Dados dos Militares"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# CARREGA DADOS
# ============================================================

try:

    df = carregar_dados()

except Exception as erro:

    st.error(
        "❌ Erro ao carregar a Página1."
    )

    st.exception(
        erro
    )

    st.stop()


# ============================================================
# VISUALIZAÇÃO
# ============================================================

st.subheader(
    "📋 Visualização dos Registros"
)

if df.empty:

    st.warning(
        "A Página1 não possui registros."
    )

else:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# NOVO CADASTRO
# ============================================================

st.markdown("---")

with st.expander(
    "➕ Novo Cadastro de Militar",
    expanded=False
):

    st.info(
        "Preencha os dados e clique em "
        "**💾 SALVAR NOVO CADASTRO**."
    )

    novos_dados = formulario_militar(
        dados=None,
        prefixo="novo"
    )

    st.markdown("---")

    if st.button(
        "💾 SALVAR NOVO CADASTRO",
        type="primary",
        use_container_width=True,
        key="btn_salvar_novo"
    ):

        try:

            salvar_novo_cadastro(
                novos_dados
            )

            limpar_cache()

            st.success(
                "🎉 Novo cadastro salvo com sucesso!"
            )

            st.info(
                f"Matrícula: "
                f"**{novos_dados.get('Matrícula', '')}**"
                "\n\n"
                f"Nome: "
                f"**{novos_dados.get('Nome', '')}**"
            )

            st.balloons()

        except Exception as erro:

            st.error(
                "❌ Não foi possível salvar o cadastro."
            )

            st.exception(
                erro
            )


# ============================================================
# EDIÇÃO
# ============================================================

st.markdown("---")

with st.expander(
    "✏️ Editar Registro Existente",
    expanded=False
):

    if (
        df.empty
        or "Matrícula" not in df.columns
        or "Nome" not in df.columns
    ):

        st.warning(
            "As colunas Matrícula e Nome "
            "são necessárias."
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

            registro = df[
                df["Matrícula"].astype(str).str.strip()
                == matricula_editar
            ]

            if not registro.empty:

                dados_atual = (
                    registro.iloc[0]
                    .to_dict()
                )

                st.info(
                    f"Editando: "
                    f"**{dados_atual.get('Nome', '')}**"
                )

                with st.form(
                    "form_edicao",
                    clear_on_submit=False
                ):

                    dados_editados = (
                        formulario_militar(
                            dados=dados_atual,
                            prefixo="editar"
                        )
                    )

                    # Matrícula nunca muda
                    dados_editados[
                        "Matrícula"
                    ] = matricula_editar

                    salvar_edicao = (
                        st.form_submit_button(
                            "💾 SALVAR ALTERAÇÕES",
                            type="primary",
                            use_container_width=True
                        )
                    )

                if salvar_edicao:

                    try:

                        atualizar_cadastro(
                            matricula_editar,
                            dados_editados
                        )

                        limpar_cache()

                        st.success(
                            "✅ Alterações salvas "
                            "com sucesso na Página1!"
                        )

                        st.info(
                            f"Matrícula: "
                            f"**{matricula_editar}**"
                        )

                    except Exception as erro:

                        st.error(
                            "❌ Não foi possível "
                            "salvar as alterações."
                        )

                        st.exception(
                            erro
                        )


# ============================================================
# EXCLUSÃO
# ============================================================

st.markdown("---")

with st.expander(
    "🗑️ Excluir Registro",
    expanded=False
):

    if (
        df.empty
        or "Matrícula" not in df.columns
        or "Nome" not in df.columns
    ):

        st.warning(
            "As colunas Matrícula e Nome "
            "são necessárias."
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

        selecionado_exclusao = (
            st.selectbox(
                "Selecione o militar:",
                [""] + opcoes_exclusao,
                key="militar_exclusao"
            )
        )

        if selecionado_exclusao:

            matricula_exclusao = (
                selecionado_exclusao
                .split(" - ", 1)[0]
                .strip()
            )

            registro = df[
                df["Matrícula"].astype(str).str.strip()
                == matricula_exclusao
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

            if st.button(
                "🔴 EXCLUIR REGISTRO",
                type="primary",
                disabled=not confirmar,
                use_container_width=True,
                key="btn_excluir"
            ):

                try:

                    excluir_cadastro(
                        matricula_exclusao
                    )

                    limpar_cache()

                    st.success(
                        "✅ Registro excluído "
                        "com sucesso!"
                    )

                except Exception as erro:

                    st.error(
                        "❌ Não foi possível "
                        "excluir o registro."
                    )

                    st.exception(
                        erro
                    )


# ============================================================
# RODAPÉ / DIAGNÓSTICO
# ============================================================

st.markdown("---")

with st.expander(
    "🔧 Informações técnicas"
):

    st.write(
        "Planilha configurada:"
    )

    st.code(
        st.secrets["SHEET_ID"]
    )

    st.write(
        "Aba utilizada:"
    )

    st.code(
        NOME_ABA
    )

    st.write(
        "Quantidade de registros carregados:"
    )

    st.code(
        str(len(df))
    )
