import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="DGP - Dados dos Militares",
    layout="wide"
)


# ============================================================
# GOOGLE SHEETS
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_gspread_client():
    """
    Conecta ao Google Sheets utilizando a conta de serviço
    configurada no secrets.toml.
    """

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


def get_sheet():
    """
    Abre a planilha e retorna a primeira aba.
    """

    sheet_id = st.secrets["SHEET_ID"]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(sheet_id)

    worksheet = spreadsheet.sheet1

    return worksheet


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
            use_container_width=True
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
# SIDEBAR
# ============================================================

st.sidebar.success(
    "Autenticado com sucesso!"
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
    "🔄 Atualizar Dashboard",
    use_container_width=True
):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================

_, col1, col2, _ = st.columns(
    [2, 1, 1, 2]
)

with col1:

    try:
        st.image(
            "images.png",
            width=140
        )
    except:
        pass


with col2:

    try:
        st.image(
            "11679.png",
            width=140
        )
    except:
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
# CARREGAR DADOS
# ============================================================

@st.cache_data(ttl=5)
def load_data(sheet_id):

    url = (
        "https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv"
    )

    df = pd.read_csv(
        url,
        header=0,
        dtype=str
    )

    df.columns = [
        str(col)
        .strip()
        .replace(":", "-")
        for col in df.columns
    ]

    df = df.fillna("")

    return df


# ============================================================
# CAMPOS
# ============================================================

COLUNAS_PADRAO = [

    "nº Funcional",
    "Matrícula",
    "CPF.",
    "CPF",
    "Nº IDENT.",
    "Nome",
    "Nome de Guerra",
    "SEXO",
    "Raça/Cor",
    "Posto/ Grad",
    "Fones",
    "Ano de ingresso",
    "Data de praça",

    "OME",
    "OME QOD",
    "Atividade",
    "Município",
    "Região",

    "Tempo de serviço (anos)",
    "Tempo de serviço (ano, mês, dias)",
    "Tempo de serviço (dias)",
    "Tempo na OBM atual",

    "Data da última promoção ou Implant. PCNH",
    "Princípio da última promoção",
    "Tempo no Posto/Grad. atual EM DIAS",

    "Data da Movimentação em SP",
    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO",
    "Data de chegada na OBM Anteior",
    "Movimentado (apagar antes de atualizar o SP)",

    "ÓRGÃO",
    "Poder",
    "Ônus para Origem",
    "Início da Cessão ou requisição",

    "Renovação de cessão - Atos/Portarias/Documentos",
    "DOE/BGSDS de renovação",
    "SEI deslig.",

    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP",

    "INÍCIO DA LTIP",
    "TÉRMINO DA LTIP (inserir data de apresentação)",

    "Somatório LTIP gozada em anos",
    "Somatório LTIP gozada em anos/meses/dias",
    "Somatório de todas LTIP gozadas em dias",
    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.",

    "Ato",
    "Doc. Publicação",
    "SP da Adição",
    "Processo RR",
    "Suplemento de Pessoal nº/Ano",
    "Data Suplemento de Pessoal",
    "Hoje",
    "OBS",
]


# ============================================================
# FORMULÁRIO
# ============================================================

def formulario_militar(
    dados=None,
    prefixo="novo"
):

    if dados is None:
        dados = {}

    def valor(nome):

        v = dados.get(
            nome,
            ""
        )

        if v is None:
            return ""

        try:

            if pd.isna(v):
                return ""

        except:
            pass

        return str(v)

    # ========================================================
    # ABAS
    # ========================================================

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

            num_funcional = st.text_input(
                "nº Funcional:",
                value=valor(
                    "nº Funcional"
                ),
                key=f"{prefixo}_num_funcional"
            )

            matricula = st.text_input(
                "Matrícula:",
                value=valor(
                    "Matrícula"
                ),
                key=f"{prefixo}_matricula"
            )

            cpf_ponto = st.text_input(
                "CPF.:",
                value=valor(
                    "CPF."
                ),
                key=f"{prefixo}_cpf_ponto"
            )

            cpf = st.text_input(
                "CPF:",
                value=valor(
                    "CPF"
                ),
                key=f"{prefixo}_cpf"
            )

            num_ident = st.text_input(
                "Nº IDENT.:",
                value=valor(
                    "Nº IDENT."
                ),
                key=f"{prefixo}_num_ident"
            )

        with c2:

            nome = st.text_input(
                "Nome:",
                value=valor(
                    "Nome"
                ),
                key=f"{prefixo}_nome"
            )

            nome_guerra = st.text_input(
                "Nome de Guerra:",
                value=valor(
                    "Nome de Guerra"
                ),
                key=f"{prefixo}_nome_guerra"
            )

            sexo = st.selectbox(
                "SEXO:",
                [
                    "",
                    "MASCULINO",
                    "FEMININO"
                ],
                index=(
                    [
                        "",
                        "MASCULINO",
                        "FEMININO"
                    ].index(
                        valor("SEXO").upper()
                    )
                    if valor("SEXO").upper()
                    in [
                        "",
                        "MASCULINO",
                        "FEMININO"
                    ]
                    else 0
                ),
                key=f"{prefixo}_sexo"
            )

            racas = [
                "",
                "BRANCA",
                "PRETA",
                "PARDA",
                "AMARELA",
                "INDÍGENA"
            ]

            raca_atual = valor(
                "Raça/Cor"
            ).upper()

            raca = st.selectbox(
                "Raça/Cor:",
                racas,
                index=(
                    racas.index(raca_atual)
                    if raca_atual in racas
                    else 0
                ),
                key=f"{prefixo}_raca"
            )

        with c3:

            posto_grad = st.text_input(
                "Posto/ Grad:",
                value=valor(
                    "Posto/ Grad"
                ),
                key=f"{prefixo}_posto"
            )

            fones = st.text_input(
                "Fones:",
                value=valor(
                    "Fones"
                ),
                key=f"{prefixo}_fones"
            )

            ano_ingresso = st.text_input(
                "Ano de ingresso:",
                value=valor(
                    "Ano de ingresso"
                ),
                key=f"{prefixo}_ano"
            )

            data_praca = st.text_input(
                "Data de praça:",
                value=valor(
                    "Data de praça"
                ),
                key=f"{prefixo}_praca"
            )

    # ========================================================
    # ABA 2
    # ========================================================

    with tab2:

        c1, c2, c3 = st.columns(3)

        with c1:

            ome = st.text_input(
                "OME:",
                value=valor("OME"),
                key=f"{prefixo}_ome"
            )

            ome_qod = st.text_input(
                "OME QOD:",
                value=valor("OME QOD"),
                key=f"{prefixo}_ome_qod"
            )

            atividade = st.text_input(
                "Atividade:",
                value=valor("Atividade"),
                key=f"{prefixo}_atividade"
            )

            municipio = st.text_input(
                "Município:",
                value=valor("Município"),
                key=f"{prefixo}_municipio"
            )

            regiao = st.text_input(
                "Região:",
                value=valor("Região"),
                key=f"{prefixo}_regiao"
            )

        with c2:

            tempo_anos = st.text_input(
                "Tempo de serviço (anos):",
                value=valor(
                    "Tempo de serviço (anos)"
                ),
                key=f"{prefixo}_tempo_anos"
            )

            tempo_amd = st.text_input(
                "Tempo de serviço (ano, mês, dias):",
                value=valor(
                    "Tempo de serviço (ano, mês, dias)"
                ),
                key=f"{prefixo}_tempo_amd"
            )

            tempo_dias = st.text_input(
                "Tempo de serviço (dias):",
                value=valor(
                    "Tempo de serviço (dias)"
                ),
                key=f"{prefixo}_tempo_dias"
            )

            tempo_obm = st.text_input(
                "Tempo na OBM atual:",
                value=valor(
                    "Tempo na OBM atual"
                ),
                key=f"{prefixo}_tempo_obm"
            )

        with c3:

            data_promocao = st.text_input(
                "Data da última promoção ou Implant. PCNH:",
                value=valor(
                    "Data da última promoção ou Implant. PCNH"
                ),
                key=f"{prefixo}_data_promocao"
            )

            principio = st.text_input(
                "Princípio da última promoção:",
                value=valor(
                    "Princípio da última promoção"
                ),
                key=f"{prefixo}_principio"
            )

            tempo_posto = st.text_input(
                "Tempo no Posto/Grad. atual EM DIAS:",
                value=valor(
                    "Tempo no Posto/Grad. atual EM DIAS"
                ),
                key=f"{prefixo}_tempo_posto"
            )

    # ========================================================
    # ABA 3
    # ========================================================

    with tab3:

        c1, c2, c3 = st.columns(3)

        with c1:

            data_mov = st.text_input(
                "Data da Movimentação em SP:",
                value=valor(
                    "Data da Movimentação em SP"
                ),
                key=f"{prefixo}_data_mov"
            )

            ome_anterior = st.text_input(
                "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:",
                value=valor(
                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO"
                ),
                key=f"{prefixo}_ome_anterior"
            )

            data_chegada = st.text_input(
                "Data de chegada na OBM Anteior:",
                value=valor(
                    "Data de chegada na OBM Anteior"
                ),
                key=f"{prefixo}_data_chegada"
            )

            movimentado = st.text_input(
                "Movimentado:",
                value=valor(
                    "Movimentado (apagar antes de atualizar o SP)"
                ),
                key=f"{prefixo}_movimentado"
            )

        with c2:

            orgao = st.text_input(
                "ÓRGÃO:",
                value=valor("ÓRGÃO"),
                key=f"{prefixo}_orgao"
            )

            poder = st.text_input(
                "Poder:",
                value=valor("Poder"),
                key=f"{prefixo}_poder"
            )

            onus_opcoes = [
                "",
                "SIM",
                "NÃO"
            ]

            onus_atual = valor(
                "Ônus para Origem"
            ).upper()

            onus = st.selectbox(
                "Ônus para Origem:",
                onus_opcoes,
                index=(
                    onus_opcoes.index(
                        onus_atual
                    )
                    if onus_atual in onus_opcoes
                    else 0
                ),
                key=f"{prefixo}_onus"
            )

            inicio_cessao = st.text_input(
                "Início da Cessão ou requisição:",
                value=valor(
                    "Início da Cessão ou requisição"
                ),
                key=f"{prefixo}_inicio_cessao"
            )

        with c3:

            renovacao = st.text_input(
                "Renovação de cessão - Atos/Portarias/Documentos:",
                value=valor(
                    "Renovação de cessão - Atos/Portarias/Documentos"
                ),
                key=f"{prefixo}_renovacao"
            )

            doe = st.text_input(
                "DOE/BGSDS de renovação:",
                value=valor(
                    "DOE/BGSDS de renovação"
                ),
                key=f"{prefixo}_doe"
            )

            sei = st.text_input(
                "SEI deslig.:",
                value=valor(
                    "SEI deslig."
                ),
                key=f"{prefixo}_sei"
            )

    # ========================================================
    # ABA 4
    # ========================================================

    with tab4:

        c1, c2 = st.columns(2)

        with c1:

            afastamentos = st.text_area(
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP:",
                value=valor(
                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP"
                ),
                key=f"{prefixo}_afastamentos"
            )

            inicio_ltip = st.text_input(
                "INÍCIO DA LTIP:",
                value=valor(
                    "INÍCIO DA LTIP"
                ),
                key=f"{prefixo}_inicio_ltip"
            )

            termino_ltip = st.text_input(
                "TÉRMINO DA LTIP:",
                value=valor(
                    "TÉRMINO DA LTIP (inserir data de apresentação)"
                ),
                key=f"{prefixo}_termino_ltip"
            )

        with c2:

            somatorio_anos = st.text_input(
                "Somatório LTIP gozada em anos:",
                value=valor(
                    "Somatório LTIP gozada em anos"
                ),
                key=f"{prefixo}_somatorio_anos"
            )

            somatorio_amd = st.text_input(
                "Somatório LTIP gozada em anos/meses/dias:",
                value=valor(
                    "Somatório LTIP gozada em anos/meses/dias"
                ),
                key=f"{prefixo}_somatorio_amd"
            )

            somatorio_dias = st.text_input(
                "Somatório de todas LTIP gozadas em dias:",
                value=valor(
                    "Somatório de todas LTIP gozadas em dias"
                ),
                key=f"{prefixo}_somatorio_dias"
            )

            total_ltip = st.text_input(
                "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:",
                value=valor(
                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad."
                ),
                key=f"{prefixo}_total_ltip"
            )

    # ========================================================
    # ABA 5
    # ========================================================

    with tab5:

        c1, c2 = st.columns(2)

        with c1:

            ato = st.text_input(
                "Ato:",
                value=valor("Ato"),
                key=f"{prefixo}_ato"
            )

            doc_publicacao = st.text_input(
                "Doc. Publicação:",
                value=valor(
                    "Doc. Publicação"
                ),
                key=f"{prefixo}_doc"
            )

            sp_adicao = st.text_input(
                "SP da Adição:",
                value=valor(
                    "SP da Adição"
                ),
                key=f"{prefixo}_sp"
            )

            processo_rr = st.text_input(
                "Processo RR:",
                value=valor(
                    "Processo RR"
                ),
                key=f"{prefixo}_processo"
            )

        with c2:

            suplemento = st.text_input(
                "Suplemento de Pessoal nº/Ano:",
                value=valor(
                    "Suplemento de Pessoal nº/Ano"
                ),
                key=f"{prefixo}_suplemento"
            )

            data_suplemento = st.text_input(
                "Data Suplemento de Pessoal:",
                value=valor(
                    "Data Suplemento de Pessoal"
                ),
                key=f"{prefixo}_data_suplemento"
            )

            hoje = st.text_input(
                "Hoje:",
                value=valor("Hoje"),
                key=f"{prefixo}_hoje"
            )

            obs = st.text_area(
                "OBS:",
                value=valor("OBS"),
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
        "Raça/Cor": raca,
        "Posto/ Grad": posto_grad,
        "Fones": fones,
        "Ano de ingresso": ano_ingresso,
        "Data de praça": data_praca,

        "OME": ome,
        "OME QOD": ome_qod,
        "Atividade": atividade,
        "Município": municipio,
        "Região": regiao,

        "Tempo de serviço (anos)": tempo_anos,
        "Tempo de serviço (ano, mês, dias)": tempo_amd,
        "Tempo de serviço (dias)": tempo_dias,
        "Tempo na OBM atual": tempo_obm,

        "Data da última promoção ou Implant. PCNH": data_promocao,
        "Princípio da última promoção": principio,
        "Tempo no Posto/Grad. atual EM DIAS": tempo_posto,

        "Data da Movimentação em SP": data_mov,
        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO": ome_anterior,
        "Data de chegada na OBM Anteior": data_chegada,
        "Movimentado (apagar antes de atualizar o SP)": movimentado,

        "ÓRGÃO": orgao,
        "Poder": poder,
        "Ônus para Origem": onus,
        "Início da Cessão ou requisição": inicio_cessao,

        "Renovação de cessão - Atos/Portarias/Documentos": renovacao,
        "DOE/BGSDS de renovação": doe,
        "SEI deslig.": sei,

        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP": afastamentos,

        "INÍCIO DA LTIP": inicio_ltip,
        "TÉRMINO DA LTIP (inserir data de apresentação)": termino_ltip,

        "Somatório LTIP gozada em anos": somatorio_anos,
        "Somatório LTIP gozada em anos/meses/dias": somatorio_amd,
        "Somatório de todas LTIP gozadas em dias": somatorio_dias,
        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.": total_ltip,

        "Ato": ato,
        "Doc. Publicação": doc_publicacao,
        "SP da Adição": sp_adicao,
        "Processo RR": processo_rr,
        "Suplemento de Pessoal nº/Ano": suplemento,
        "Data Suplemento de Pessoal": data_suplemento,
        "Hoje": hoje,
        "OBS": obs,
    }


# ============================================================
# EXECUÇÃO
# ============================================================

try:

    SHEET_ID = st.secrets["SHEET_ID"]

    df = load_data(
        SHEET_ID
    )

    # ========================================================
    # VISUALIZAÇÃO
    # ========================================================

    st.subheader(
        "📋 Visualização dos Registros"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ========================================================
    # NOVO CADASTRO
    # ========================================================

    with st.expander(
        "➕ Novo Cadastro de Militar",
        expanded=False
    ):

        st.info(
            "Preencha os dados e clique em "
            "**SALVAR NOVO CADASTRO**."
        )

        # IMPORTANTE:
        # O formulário engloba todos os campos e o botão.
        # Assim o Streamlit entrega todos os valores juntos.

        with st.form(
            "form_novo_cadastro",
            clear_on_submit=False
        ):

            novos_dados = formulario_militar(
                dados=None,
                prefixo="novo"
            )

            st.markdown("---")

            salvar = st.form_submit_button(
                "💾 SALVAR NOVO CADASTRO",
                type="primary",
                use_container_width=True
            )

        # ====================================================
        # SALVAMENTO
        # ====================================================

        if salvar:

            matricula = str(
                novos_dados.get(
                    "Matrícula",
                    ""
                )
            ).strip()

            nome = str(
                novos_dados.get(
                    "Nome",
                    ""
                )
            ).strip()

            # -----------------------------------------------
            # VALIDAÇÕES
            # -----------------------------------------------

            if not matricula:

                st.error(
                    "❌ A Matrícula é obrigatória."
                )

                st.stop()

            if not nome:

                st.error(
                    "❌ O Nome é obrigatório."
                )

                st.stop()

            st.info(
                f"⏳ Salvando matrícula **{matricula}**..."
            )

            try:

                # -------------------------------------------
                # CONECTA
                # -------------------------------------------

                worksheet = get_sheet()

                # -------------------------------------------
                # CABEÇALHOS REAIS DA PLANILHA
                # -------------------------------------------

                headers = worksheet.row_values(1)

                if not headers:

                    st.error(
                        "❌ A planilha não possui cabeçalhos "
                        "na primeira linha."
                    )

                    st.stop()

                # -------------------------------------------
                # LIMPA CABEÇALHOS
                # -------------------------------------------

                headers = [
                    str(h).strip()
                    for h in headers
                ]

                # -------------------------------------------
                # CONFERE MATRÍCULA
                # -------------------------------------------

                if "Matrícula" not in headers:

                    st.error(
                        "❌ Não encontrei a coluna "
                        "'Matrícula' na planilha."
                    )

                    st.write(
                        "Cabeçalhos encontrados:"
                    )

                    st.code(
                        "\n".join(headers)
                    )

                    st.stop()

                coluna_matricula = (
                    headers.index(
                        "Matrícula"
                    ) + 1
                )

                valores = worksheet.col_values(
                    coluna_matricula
                )

                matriculas = [
                    str(x).strip()
                    for x in valores[1:]
                    if str(x).strip()
                ]

                if matricula in matriculas:

                    st.error(
                        f"❌ A matrícula "
                        f"**{matricula}** "
                        f"já existe."
                    )

                    st.stop()

                # -------------------------------------------
                # MONTA LINHA EXATAMENTE NA ORDEM DA PLANILHA
                # -------------------------------------------

                nova_linha = []

                for coluna in headers:

                    valor = novos_dados.get(
                        coluna,
                        ""
                    )

                    if valor is None:
                        valor = ""

                    nova_linha.append(
                        str(valor)
                    )

                # -------------------------------------------
                # GARANTE TAMANHO
                # -------------------------------------------

                if len(nova_linha) != len(headers):

                    st.error(
                        "❌ Erro interno: quantidade "
                        "de colunas diferente."
                    )

                    st.write(
                        "Cabeçalhos:",
                        len(headers)
                    )

                    st.write(
                        "Dados:",
                        len(nova_linha)
                    )

                    st.stop()

                # -------------------------------------------
                # MOSTRA O QUE SERÁ GRAVADO
                # -------------------------------------------

                st.write(
                    f"📝 Gravando **{len(nova_linha)} "
                    f"campos** na planilha..."
                )

                # -------------------------------------------
                # GRAVAÇÃO
                # -------------------------------------------

                worksheet.append_row(
                    nova_linha,
                    value_input_option="USER_ENTERED"
                )

                # -------------------------------------------
                # VERIFICAÇÃO REAL
                # -------------------------------------------

                st.write(
                    "🔎 Confirmando gravação..."
                )

                valores_depois = worksheet.col_values(
                    coluna_matricula
                )

                encontrou = (
                    matricula
                    in [
                        str(x).strip()
                        for x in valores_depois
                    ]
                )

                if not encontrou:

                    st.error(
                        "⚠️ O Google não confirmou a "
                        "gravação da matrícula."
                    )

                    st.warning(
                        "A aplicação conseguiu executar "
                        "a operação, mas a matrícula não "
                        "foi encontrada novamente na "
                        "planilha."
                    )

                    st.stop()

                # -------------------------------------------
                # SUCESSO
                # -------------------------------------------

                st.success(
                    f"✅ CADASTRO SALVO COM SUCESSO!\n\n"
                    f"**Matrícula:** {matricula}\n\n"
                    f"**Nome:** {nome}"
                )

                st.balloons()

                # -------------------------------------------
                # LIMPA CACHE
                # -------------------------------------------

                st.cache_data.clear()

                # -------------------------------------------
                # RECARREGA DADOS
                # -------------------------------------------

                st.rerun()

            except Exception as erro:

                st.error(
                    "❌ NÃO FOI POSSÍVEL GRAVAR "
                    "NA PLANILHA."
                )

                st.exception(erro)

                st.warning(
                    "Se aparecer 'Permission denied', "
                    "'403' ou 'The caller does not have "
                    "permission', a conta de serviço "
                    "precisa ter acesso de EDITOR à "
                    "planilha."
                )

    # ========================================================
    # EDIÇÃO
    # ========================================================

    with st.expander(
        "✏️ Editar Registro Existente",
        expanded=False
    ):

        if (
            "Matrícula" not in df.columns
            or "Nome" not in df.columns
        ):

            st.warning(
                "As colunas Matrícula e Nome "
                "não foram encontradas."
            )

        else:

            opcoes = df.apply(
                lambda r:
                f"{r['Matrícula']} - {r['Nome']}",
                axis=1
            ).tolist()

            selecionado = st.selectbox(
                "Selecione o militar:",
                [""] + opcoes,
                key="editar_selecionado"
            )

            if selecionado:

                matricula_editar = (
                    selecionado
                    .split(" - ")[0]
                    .strip()
                )

                registro = df[
                    df["Matrícula"].astype(str).str.strip()
                    == matricula_editar
                ]

                if not registro.empty:

                    dados = registro.iloc[
                        0
                    ].to_dict()

                    st.info(
                        f"Editando: **"
                        f"{dados.get('Nome', '')}"
                        f"**"
                    )

                    with st.form(
                        "form_edicao",
                        clear_on_submit=False
                    ):

                        dados_editados = formulario_militar(
                            dados=dados,
                            prefixo="edicao"
                        )

                        atualizar = (
                            st.form_submit_button(
                                "🔄 ATUALIZAR REGISTRO",
                                type="primary",
                                use_container_width=True
                            )
                        )

                    if atualizar:

                        try:

                            worksheet = get_sheet()

                            headers = [
                                str(h).strip()
                                for h in worksheet.row_values(1)
                            ]

                            celula = worksheet.find(
                                matricula_editar
                            )

                            if not celula:

                                st.error(
                                    "❌ Matrícula não encontrada."
                                )

                            else:

                                linha = [
                                    str(
                                        dados_editados.get(
                                            coluna,
                                            ""
                                        )
                                    )
                                    for coluna in headers
                                ]

                                worksheet.update(
                                    f"A{celula.row}",
                                    [linha],
                                    value_input_option="USER_ENTERED"
                                )

                                st.success(
                                    f"✅ Matrícula "
                                    f"**{matricula_editar}** "
                                    f"atualizada."
                                )

                                st.cache_data.clear()

                                st.rerun()

                        except Exception as erro:

                            st.error(
                                "❌ Erro ao atualizar:"
                            )

                            st.exception(
                                erro
                            )

    # ========================================================
    # EXCLUSÃO
    # ========================================================

    with st.expander(
        "🗑️ Excluir Registro",
        expanded=False
    ):

        if (
            "Matrícula" not in df.columns
            or "Nome" not in df.columns
        ):

            st.warning(
                "As colunas Matrícula e Nome "
                "não foram encontradas."
            )

        else:

            opcoes_exclusao = df.apply(
                lambda r:
                f"{r['Matrícula']} - {r['Nome']}",
                axis=1
            ).tolist()

            selecionado_exclusao = st.selectbox(
                "Selecione o militar:",
                [""] + opcoes_exclusao,
                key="excluir_selecionado"
            )

            if selecionado_exclusao:

                matricula = (
                    selecionado_exclusao
                    .split(" - ")[0]
                    .strip()
                )

                confirmar = st.checkbox(
                    "Confirmo a exclusão permanente.",
                    key="confirmar_exclusao"
                )

                excluir = st.button(
                    "🔴 EXCLUIR REGISTRO",
                    type="primary",
                    disabled=not confirmar,
                    use_container_width=True
                )

                if excluir:

                    try:

                        worksheet = get_sheet()

                        celula = worksheet.find(
                            matricula
                        )

                        if not celula:

                            st.error(
                                "❌ Matrícula não encontrada."
                            )

                        else:

                            worksheet.delete_rows(
                                celula.row
                            )

                            st.success(
                                f"✅ Registro "
                                f"**{matricula}** "
                                f"excluído."
                            )

                            st.cache_data.clear()

                            st.rerun()

                    except Exception as erro:

                        st.error(
                            "❌ Erro ao excluir:"
                        )

                        st.exception(
                            erro
                        )


# ============================================================
# ERROS GERAIS
# ============================================================

except KeyError as erro:

    st.error(
        f"❌ Configuração ausente no Secrets: {erro}"
    )

except Exception as erro:

    st.error(
        "❌ Erro geral da aplicação."
    )

    st.exception(erro)
