import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import time

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


# ============================================================
# AUTENTICAÇÃO DO USUÁRIO
# ============================================================

def check_password():

    def password_entered():

        user = st.session_state.get("username", "").strip()
        pwd = st.session_state.get("password", "").strip()

        passwords_dict = st.secrets.get("passwords", {})

        if user in passwords_dict and str(passwords_dict[user]) == pwd:

            st.session_state["password_correct"] = True

            st.session_state.pop("password", None)
            st.session_state.pop("username", None)

        else:

            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
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
            st.error("😕 Usuário ou senha incorretos.")

    return False


if not check_password():
    st.stop()


# ============================================================
# CONEXÃO COM GOOGLE SHEETS
# ============================================================

def get_gspread_client():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


def get_sheet():

    client = get_gspread_client()

    spreadsheet = client.open_by_key(
        st.secrets["SHEET_ID"]
    )

    sheet = spreadsheet.sheet1

    return spreadsheet, sheet


# ============================================================
# LEITURA DOS DADOS
# ============================================================

@st.cache_data(ttl=5)
def load_data(sheet_id):

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv"
    )

    df = pd.read_csv(
        url,
        dtype=str,
        keep_default_na=False
    )

    df.columns = [
        str(col).strip().replace(":", "-")
        for col in df.columns
    ]

    return df


# ============================================================
# LIMPEZA DE VALORES
# ============================================================

def limpar_valor(valor):

    if valor is None:
        return ""

    if pd.isna(valor):
        return ""

    texto = str(valor)

    if texto.lower() in ["nan", "none", "nat"]:
        return ""

    return texto.strip()


# ============================================================
# NORMALIZAÇÃO DE CABEÇALHO
# ============================================================

def normalizar_cabecalho(texto):

    if texto is None:
        return ""

    return (
        str(texto)
        .strip()
        .replace(":", "-")
    )


# ============================================================
# LOCALIZAR COLUNA
# ============================================================

def localizar_coluna(headers, nome):

    nome_normalizado = normalizar_cabecalho(nome)

    for i, header in enumerate(headers):

        if normalizar_cabecalho(header) == nome_normalizado:
            return i

    return None


# ============================================================
# VERIFICAR SE A MATRÍCULA EXISTE
# ============================================================

def localizar_matricula(sheet, matricula):

    matricula = limpar_valor(matricula)

    headers = sheet.row_values(1)

    indice = localizar_coluna(
        headers,
        "Matrícula"
    )

    if indice is None:
        raise Exception(
            "A coluna 'Matrícula' não foi encontrada "
            "na primeira linha da planilha."
        )

    coluna = indice + 1

    valores = sheet.col_values(coluna)

    for numero_linha, valor in enumerate(valores, start=1):

        if numero_linha == 1:
            continue

        if limpar_valor(valor) == matricula:

            return numero_linha

    return None


# ============================================================
# MONTAR LINHA CONFORME OS CABEÇALHOS
# ============================================================

def montar_linha(headers, dados):

    linha = []

    for header in headers:

        header_limpo = normalizar_cabecalho(header)

        valor = ""

        for chave, valor_dado in dados.items():

            if normalizar_cabecalho(chave) == header_limpo:

                valor = valor_dado
                break

        linha.append(
            limpar_valor(valor)
        )

    return linha


# ============================================================
# CONFIRMAR GRAVAÇÃO
# ============================================================

def confirmar_gravacao(sheet, numero_linha, linha_esperada):

    time.sleep(1)

    linha_lida = sheet.row_values(numero_linha)

    linha_lida = [
        limpar_valor(v)
        for v in linha_lida
    ]

    linha_esperada = [
        limpar_valor(v)
        for v in linha_esperada
    ]

    tamanho = max(
        len(linha_lida),
        len(linha_esperada)
    )

    linha_lida += [""] * (
        tamanho - len(linha_lida)
    )

    linha_esperada += [""] * (
        tamanho - len(linha_esperada)
    )

    return linha_lida == linha_esperada


# ============================================================
# SALVAR NOVO CADASTRO
# ============================================================

def salvar_novo_cadastro(dados):

    spreadsheet, sheet = get_sheet()

    headers = sheet.row_values(1)

    if not headers:

        raise Exception(
            "A planilha não possui cabeçalhos."
        )

    headers = [
        normalizar_cabecalho(h)
        for h in headers
    ]

    if "Matrícula" not in headers:

        raise Exception(
            "A coluna 'Matrícula' não existe na planilha."
        )

    matricula = limpar_valor(
        dados.get("Matrícula")
    )

    nome = limpar_valor(
        dados.get("Nome")
    )

    if not matricula:

        raise Exception(
            "Informe a Matrícula."
        )

    if not nome:

        raise Exception(
            "Informe o Nome."
        )

    linha_existente = localizar_matricula(
        sheet,
        matricula
    )

    if linha_existente:

        raise Exception(
            f"A matrícula {matricula} já existe "
            f"na linha {linha_existente}."
        )

    nova_linha = montar_linha(
        headers,
        dados
    )

    if len(nova_linha) != len(headers):

        raise Exception(
            f"Erro interno: a planilha possui "
            f"{len(headers)} colunas, mas foram "
            f"montados {len(nova_linha)} valores."
        )

    # Descobre a próxima linha real
    valores_coluna_a = sheet.col_values(1)

    proxima_linha = len(
        valores_coluna_a
    ) + 1

    # ========================================================
    # GRAVAÇÃO DIRETA
    # ========================================================

    sheet.update(
        f"A{proxima_linha}",
        [nova_linha],
        value_input_option="USER_ENTERED"
    )

    # ========================================================
    # CONFIRMAÇÃO REAL
    # ========================================================

    confirmado = confirmar_gravacao(
        sheet,
        proxima_linha,
        nova_linha
    )

    if not confirmado:

        raise Exception(
            "O Google Sheets não confirmou os dados "
            "gravados. O cadastro NÃO será considerado "
            "salvo pelo sistema."
        )

    return proxima_linha


# ============================================================
# ATUALIZAR REGISTRO
# ============================================================

def atualizar_cadastro(matricula, dados):

    spreadsheet, sheet = get_sheet()

    headers = sheet.row_values(1)

    headers = [
        normalizar_cabecalho(h)
        for h in headers
    ]

    numero_linha = localizar_matricula(
        sheet,
        matricula
    )

    if not numero_linha:

        raise Exception(
            f"A matrícula {matricula} não foi encontrada."
        )

    dados["Matrícula"] = matricula

    nova_linha = montar_linha(
        headers,
        dados
    )

    sheet.update(
        f"A{numero_linha}",
        [nova_linha],
        value_input_option="USER_ENTERED"
    )

    confirmado = confirmar_gravacao(
        sheet,
        numero_linha,
        nova_linha
    )

    if not confirmado:

        raise Exception(
            "O Google Sheets não confirmou "
            "a atualização."
        )

    return numero_linha


# ============================================================
# EXCLUIR REGISTRO
# ============================================================

def excluir_cadastro(matricula):

    spreadsheet, sheet = get_sheet()

    numero_linha = localizar_matricula(
        sheet,
        matricula
    )

    if not numero_linha:

        raise Exception(
            f"A matrícula {matricula} não foi encontrada."
        )

    sheet.delete_rows(
        numero_linha
    )

    return numero_linha


# ============================================================
# BARRA LATERAL
# ============================================================

st.sidebar.success(
    "Autenticado com sucesso!"
)

if st.sidebar.button(
    "🚪 Sair / Logout"
):

    st.session_state["password_correct"] = False
    st.rerun()


if st.sidebar.button(
    "🔄 Forçar Atualização"
):

    st.cache_data.clear()
    st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================

_, col_img1, col_img2, _ = st.columns(
    [2, 1, 1, 2]
)

with col_img1:

    try:
        st.image(
            "images.png",
            width=140
        )
    except:
        pass


with col_img2:

    try:
        st.image(
            "11679.png",
            width=140
        )
    except:
        pass


st.markdown(
    "<h1 style='text-align:center;'>"
    "DGP - Dados dos Militares"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# EXECUÇÃO
# ============================================================

try:

    SHEET_ID = st.secrets["SHEET_ID"]

    # ========================================================
    # CARREGA DADOS
    # ========================================================

    df = load_data(
        SHEET_ID
    )

    st.subheader(
        "📋 Visualização dos Registros"
    )

    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )

    st.markdown("---")


    # ========================================================
    # NOVO CADASTRO
    # ========================================================

    with st.expander(
        "➕ Novo Cadastro de Militar",
        expanded=True
    ):

        st.info(
            "Preencha os dados e clique em "
            "**💾 SALVAR NOVO CADASTRO**."
        )

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "👤 Identificação & Pessoal",
                "🏢 Lotação & Promoção",
                "🔄 Cessão & Movimentação",
                "⏳ LTIP & Afastamentos",
                "📝 Documentos & Observações",
            ]
        )

        # ====================================================
        # ABA 1
        # ====================================================

        with tab1:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_num_funcional = st.text_input(
                    "nº Funcional",
                    key="novo_num_funcional"
                )

                novo_matricula = st.text_input(
                    "Matrícula",
                    key="novo_matricula"
                )

                novo_cpf_ponto = st.text_input(
                    "CPF.",
                    key="novo_cpf_ponto"
                )

                novo_cpf = st.text_input(
                    "CPF",
                    key="novo_cpf"
                )

                novo_num_ident = st.text_input(
                    "Nº IDENT.",
                    key="novo_num_ident"
                )

            with c2:

                novo_nome = st.text_input(
                    "Nome",
                    key="novo_nome"
                )

                novo_nome_guerra = st.text_input(
                    "Nome de Guerra",
                    key="novo_nome_guerra"
                )

                novo_sexo = st.selectbox(
                    "SEXO",
                    [
                        "",
                        "MASCULINO",
                        "FEMININO"
                    ],
                    key="novo_sexo"
                )

                novo_raca = st.selectbox(
                    "Raça/Cor",
                    [
                        "",
                        "BRANCA",
                        "PRETA",
                        "PARDA",
                        "AMARELA",
                        "INDÍGENA"
                    ],
                    key="novo_raca"
                )

            with c3:

                novo_posto_grad = st.text_input(
                    "Posto/ Grad",
                    key="novo_posto_grad"
                )

                novo_fones = st.text_input(
                    "Fones",
                    key="novo_fones"
                )

                novo_ano_ingresso = st.text_input(
                    "Ano de ingresso",
                    key="novo_ano_ingresso"
                )

                novo_data_praca = st.text_input(
                    "Data de praça",
                    key="novo_data_praca"
                )


        # ====================================================
        # ABA 2
        # ====================================================

        with tab2:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_ome = st.text_input(
                    "OME",
                    key="novo_ome"
                )

                novo_ome_qod = st.text_input(
                    "OME QOD",
                    key="novo_ome_qod"
                )

                novo_atividade = st.text_input(
                    "Atividade",
                    key="novo_atividade"
                )

                novo_municipio = st.text_input(
                    "Município",
                    key="novo_municipio"
                )

                novo_regiao = st.text_input(
                    "Região",
                    key="novo_regiao"
                )

            with c2:

                novo_tempo_servico_anos = st.text_input(
                    "Tempo de serviço (anos)",
                    key="novo_tempo_servico_anos"
                )

                novo_tempo_servico_amd = st.text_input(
                    "Tempo de serviço (ano, mês, dias)",
                    key="novo_tempo_servico_amd"
                )

                novo_tempo_servico_dias = st.text_input(
                    "Tempo de serviço (dias)",
                    key="novo_tempo_servico_dias"
                )

                novo_tempo_obm_atual = st.text_input(
                    "Tempo na OBM atual",
                    key="novo_tempo_obm_atual"
                )

            with c3:

                novo_data_ult_promocao = st.text_input(
                    "Data da última promoção ou Implant. PCNH",
                    key="novo_data_ult_promocao"
                )

                novo_principio_ult_promocao = st.text_input(
                    "Princípio da última promoção",
                    key="novo_principio_ult_promocao"
                )

                novo_tempo_posto_atual_dias = st.text_input(
                    "Tempo no Posto/Grad. atual EM DIAS",
                    key="novo_tempo_posto_atual_dias"
                )


        # ====================================================
        # ABA 3
        # ====================================================

        with tab3:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_data_mov_sp = st.text_input(
                    "Data da Movimentação em SP",
                    key="novo_data_mov_sp"
                )

                novo_ome_anterior = st.text_input(
                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO",
                    key="novo_ome_anterior"
                )

                novo_data_chegada = st.text_input(
                    "Data de chegada na OBM Anteior",
                    key="novo_data_chegada"
                )

                novo_movimentado = st.text_input(
                    "Movimentado (apagar antes de atualizar o SP)",
                    key="novo_movimentado"
                )

            with c2:

                novo_orgao = st.text_input(
                    "ÓRGÃO",
                    key="novo_orgao"
                )

                novo_poder = st.text_input(
                    "Poder",
                    key="novo_poder"
                )

                novo_onus = st.selectbox(
                    "Ônus para Origem",
                    [
                        "",
                        "SIM",
                        "NÃO"
                    ],
                    key="novo_onus"
                )

                novo_inicio_cessao = st.text_input(
                    "Início da Cessão ou requisição",
                    key="novo_inicio_cessao"
                )

            with c3:

                novo_renovacao = st.text_input(
                    "Renovação de cessão - Atos/Portarias/Documentos",
                    key="novo_renovacao"
                )

                novo_doe = st.text_input(
                    "DOE/BGSDS de renovação",
                    key="novo_doe"
                )

                novo_sei = st.text_input(
                    "SEI deslig.",
                    key="novo_sei"
                )


        # ====================================================
        # ABA 4
        # ====================================================

        with tab4:

            c1, c2 = st.columns(2)

            with c1:

                novo_afastamentos = st.text_area(
                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP",
                    key="novo_afastamentos"
                )

                novo_inicio_ltip = st.text_input(
                    "INÍCIO DA LTIP",
                    key="novo_inicio_ltip"
                )

                novo_termino_ltip = st.text_input(
                    "TÉRMINO DA LTIP (inserir data de apresentação)",
                    key="novo_termino_ltip"
                )

            with c2:

                novo_somatorio_anos = st.text_input(
                    "Somatório LTIP gozada em anos",
                    key="novo_somatorio_anos"
                )

                novo_somatorio_amd = st.text_input(
                    "Somatório LTIP gozada em anos/meses/dias",
                    key="novo_somatorio_amd"
                )

                novo_somatorio_dias = st.text_input(
                    "Somatório de todas LTIP gozadas em dias",
                    key="novo_somatorio_dias"
                )

                novo_total_ltip = st.text_input(
                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.",
                    key="novo_total_ltip"
                )


        # ====================================================
        # ABA 5
        # ====================================================

        with tab5:

            c1, c2 = st.columns(2)

            with c1:

                novo_ato = st.text_input(
                    "Ato",
                    key="novo_ato"
                )

                novo_doc_publicacao = st.text_input(
                    "Doc. Publicação",
                    key="novo_doc_publicacao"
                )

                novo_sp_adicao = st.text_input(
                    "SP da Adição",
                    key="novo_sp_adicao"
                )

                novo_processo_rr = st.text_input(
                    "Processo RR",
                    key="novo_processo_rr"
                )

            with c2:

                novo_suplemento = st.text_input(
                    "Suplemento de Pessoal nº/Ano",
                    key="novo_suplemento"
                )

                novo_data_suplemento = st.text_input(
                    "Data Suplemento de Pessoal",
                    key="novo_data_suplemento"
                )

                novo_hoje = st.text_input(
                    "Hoje",
                    key="novo_hoje"
                )

                novo_obs = st.text_area(
                    "OBS",
                    key="novo_obs"
                )


        # ====================================================
        # DADOS
        # ====================================================

        novos_dados = {

            "nº Funcional": novo_num_funcional,
            "Matrícula": novo_matricula,
            "CPF.": novo_cpf_ponto,
            "CPF": novo_cpf,
            "Nº IDENT.": novo_num_ident,
            "Nome": novo_nome,
            "Nome de Guerra": novo_nome_guerra,
            "SEXO": novo_sexo,
            "Raça/Cor": novo_raca,
            "Posto/ Grad": novo_posto_grad,
            "Fones": novo_fones,
            "Ano de ingresso": novo_ano_ingresso,
            "Data de praça": novo_data_praca,

            "OME": novo_ome,
            "OME QOD": novo_ome_qod,
            "Atividade": novo_atividade,
            "Município": novo_municipio,
            "Região": novo_regiao,

            "Tempo de serviço (anos)": novo_tempo_servico_anos,
            "Tempo de serviço (ano, mês, dias)": novo_tempo_servico_amd,
            "Tempo de serviço (dias)": novo_tempo_servico_dias,
            "Tempo na OBM atual": novo_tempo_obm_atual,

            "Data da última promoção ou Implant. PCNH": novo_data_ult_promocao,
            "Princípio da última promoção": novo_principio_ult_promocao,
            "Tempo no Posto/Grad. atual EM DIAS": novo_tempo_posto_atual_dias,

            "Data da Movimentação em SP": novo_data_mov_sp,
            "OME ANTERIOR AO ÚLTIMO SP PUBLICADO": novo_ome_anterior,
            "Data de chegada na OBM Anteior": novo_data_chegada,
            "Movimentado (apagar antes de atualizar o SP)": novo_movimentado,

            "ÓRGÃO": novo_orgao,
            "Poder": novo_poder,
            "Ônus para Origem": novo_onus,
            "Início da Cessão ou requisição": novo_inicio_cessao,

            "Renovação de cessão - Atos/Portarias/Documentos": novo_renovacao,
            "DOE/BGSDS de renovação": novo_doe,
            "SEI deslig.": novo_sei,

            "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP": novo_afastamentos,

            "INÍCIO DA LTIP": novo_inicio_ltip,
            "TÉRMINO DA LTIP (inserir data de apresentação)": novo_termino_ltip,

            "Somatório LTIP gozada em anos": novo_somatorio_anos,
            "Somatório LTIP gozada em anos/meses/dias": novo_somatorio_amd,
            "Somatório de todas LTIP gozadas em dias": novo_somatorio_dias,
            "TOTAL DIAS EM LTIP no MESMO Posto/Grad.": novo_total_ltip,

            "Ato": novo_ato,
            "Doc. Publicação": novo_doc_publicacao,
            "SP da Adição": novo_sp_adicao,
            "Processo RR": novo_processo_rr,

            "Suplemento de Pessoal nº/Ano": novo_suplemento,
            "Data Suplemento de Pessoal": novo_data_suplemento,
            "Hoje": novo_hoje,
            "OBS": novo_obs,
        }


        # ====================================================
        # BOTÃO SALVAR
        # ====================================================

        st.markdown("---")

        salvar = st.button(
            "💾 SALVAR NOVO CADASTRO",
            type="primary",
            use_container_width=True,
            key="botao_salvar_novo"
        )


        if salvar:

            matricula = limpar_valor(
                novos_dados["Matrícula"]
            )

            nome = limpar_valor(
                novos_dados["Nome"]
            )

            if not matricula:

                st.error(
                    "❌ Informe a Matrícula."
                )

            elif not nome:

                st.error(
                    "❌ Informe o Nome."
                )

            else:

                try:

                    with st.spinner(
                        "💾 Gravando no Google Sheets..."
                    ):

                        numero_linha = salvar_novo_cadastro(
                            novos_dados
                        )

                    st.success(
                        f"🎉 CADASTRO SALVO E CONFIRMADO!\n\n"
                        f"**Matrícula:** {matricula}\n\n"
                        f"**Nome:** {nome}\n\n"
                        f"**Linha gravada:** {numero_linha}"
                    )

                    # Atualiza somente o cache.
                    # NÃO executa rerun imediatamente.
                    st.cache_data.clear()

                    st.info(
                        "✅ A gravação foi confirmada diretamente "
                        "no Google Sheets. Você pode conferir a "
                        "nova linha na planilha."
                    )

                except Exception as erro:

                    st.error(
                        "❌ O CADASTRO NÃO FOI SALVO."
                    )

                    st.error(
                        str(erro)
                    )

                    with st.expander(
                        "🔎 Detalhes técnicos"
                    ):

                        st.exception(erro)


    # ========================================================
    # EDIÇÃO
    # ========================================================

    with st.expander(
        "✏️ Editar Registro Existente",
        expanded=False
    ):

        if (
            "Matrícula" in df.columns
            and "Nome" in df.columns
        ):

            opcoes = df.apply(
                lambda r:
                f"{r['Matrícula']} - {r['Nome']}",
                axis=1
            ).tolist()

            selecionado = st.selectbox(
                "Selecione o militar:",
                [""] + opcoes,
                key="militar_edicao"
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

                    dados_atual = (
                        registro.iloc[0]
                        .to_dict()
                    )

                    st.info(
                        f"Editando: **{dados_atual.get('Nome', '')}**"
                    )

                    with st.form(
                        "form_edicao"
                    ):

                        # Campos principais
                        e_nome = st.text_input(
                            "Nome",
                            value=limpar_valor(
                                dados_atual.get("Nome")
                            )
                        )

                        e_nome_guerra = st.text_input(
                            "Nome de Guerra",
                            value=limpar_valor(
                                dados_atual.get("Nome de Guerra")
                            )
                        )

                        e_posto = st.text_input(
                            "Posto/ Grad",
                            value=limpar_valor(
                                dados_atual.get("Posto/ Grad")
                            )
                        )

                        e_ome = st.text_input(
                            "OME",
                            value=limpar_valor(
                                dados_atual.get("OME")
                            )
                        )

                        e_atividade = st.text_input(
                            "Atividade",
                            value=limpar_valor(
                                dados_atual.get("Atividade")
                            )
                        )

                        e_municipio = st.text_input(
                            "Município",
                            value=limpar_valor(
                                dados_atual.get("Município")
                            )
                        )

                        e_fones = st.text_input(
                            "Fones",
                            value=limpar_valor(
                                dados_atual.get("Fones")
                            )
                        )

                        e_cpf = st.text_input(
                            "CPF",
                            value=limpar_valor(
                                dados_atual.get("CPF")
                            )
                        )

                        e_obs = st.text_area(
                            "OBS",
                            value=limpar_valor(
                                dados_atual.get("OBS")
                            )
                        )

                        atualizar = st.form_submit_button(
                            "🔄 ATUALIZAR REGISTRO",
                            use_container_width=True
                        )

                    if atualizar:

                        dados_edicao = dados_atual.copy()

                        dados_edicao["Nome"] = e_nome
                        dados_edicao["Nome de Guerra"] = e_nome_guerra
                        dados_edicao["Posto/ Grad"] = e_posto
                        dados_edicao["OME"] = e_ome
                        dados_edicao["Atividade"] = e_atividade
                        dados_edicao["Município"] = e_municipio
                        dados_edicao["Fones"] = e_fones
                        dados_edicao["CPF"] = e_cpf
                        dados_edicao["OBS"] = e_obs

                        try:

                            with st.spinner(
                                "🔄 Atualizando..."
                            ):

                                linha = atualizar_cadastro(
                                    matricula_editar,
                                    dados_edicao
                                )

                            st.success(
                                f"✅ Registro atualizado e "
                                f"confirmado na linha {linha}."
                            )

                            st.cache_data.clear()

                        except Exception as erro:

                            st.error(
                                "❌ A atualização NÃO foi confirmada."
                            )

                            st.error(
                                str(erro)
                            )

                else:

                    st.error(
                        "Registro não encontrado."
                    )


    # ========================================================
    # EXCLUSÃO
    # ========================================================

    with st.expander(
        "🗑️ Excluir Registro",
        expanded=False
    ):

        if (
            "Matrícula" in df.columns
            and "Nome" in df.columns
        ):

            opcoes_exclusao = df.apply(
                lambda r:
                f"{r['Matrícula']} - {r['Nome']}",
                axis=1
            ).tolist()

            selecionado_exc = st.selectbox(
                "Selecione o militar:",
                [""] + opcoes_exclusao,
                key="militar_exclusao"
            )

            if selecionado_exc:

                matricula_exc = (
                    selecionado_exc
                    .split(" - ")[0]
                    .strip()
                )

                st.warning(
                    f"Você selecionou a matrícula "
                    f"**{matricula_exc}**."
                )

                confirmar = st.checkbox(
                    "Confirmo que desejo excluir permanentemente.",
                    key="confirmar_exclusao_final"
                )

                if st.button(
                    "🔴 EXCLUIR REGISTRO",
                    disabled=not confirmar,
                    type="primary",
                    key="excluir_final"
                ):

                    try:

                        with st.spinner(
                            "🗑️ Excluindo..."
                        ):

                            linha = excluir_cadastro(
                                matricula_exc
                            )

                        st.success(
                            f"✅ Registro excluído. "
                            f"Linha removida: {linha}"
                        )

                        st.cache_data.clear()

                    except Exception as erro:

                        st.error(
                            "❌ A exclusão NÃO foi realizada."
                        )

                        st.error(
                            str(erro)
                        )


except KeyError as erro:

    st.error(
        f"❌ Chave não encontrada nos Secrets: {erro}"
    )

except Exception as erro:

    st.error(
        "❌ Erro geral da aplicação."
    )

    st.exception(erro)
