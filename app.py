import gspread
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

            st.session_state.pop("username", None)
            st.session_state.pop("password", None)

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

@st.cache_resource
def get_gspread_client():

    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


# ============================================================
# ABRIR PLANILHA
# ============================================================

def get_sheet():

    SHEET_ID = st.secrets["SHEET_ID"]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(SHEET_ID)

    # PRIMEIRA ABA DA PLANILHA
    sheet = spreadsheet.sheet1

    return spreadsheet, sheet


# ============================================================
# LER DADOS DIRETAMENTE DO GOOGLE SHEETS
# ============================================================

@st.cache_data(ttl=5)
def load_data():

    SHEET_ID = st.secrets["SHEET_ID"]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(SHEET_ID)

    sheet = spreadsheet.sheet1

    values = sheet.get_all_values()

    if not values:

        return pd.DataFrame()

    headers = values[0]

    rows = values[1:]

    # Garante que todas as linhas tenham o mesmo número
    # de colunas que o cabeçalho
    dados_corrigidos = []

    for row in rows:

        row = list(row)

        if len(row) < len(headers):

            row += [""] * (len(headers) - len(row))

        elif len(row) > len(headers):

            row = row[:len(headers)]

        dados_corrigidos.append(row)

    df = pd.DataFrame(
        dados_corrigidos,
        columns=headers
    )

    return df


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def limpar_valor(valor):

    if valor is None:
        return ""

    if pd.isna(valor):
        return ""

    return str(valor).strip()


# ============================================================
# MAPA DOS CAMPOS
# ============================================================

CAMPOS = [
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
# FUNÇÃO PARA OBTER VALOR
# ============================================================

def obter_valor(dados, campo):

    if dados is None:
        return ""

    valor = dados.get(campo, "")

    return limpar_valor(valor)


# ============================================================
# FORMULÁRIO
# ============================================================

def formulario_militar(
    dados=None,
    prefixo="novo"
):

    if dados is None:
        dados = {}

    def v(campo):
        return obter_valor(dados, campo)

    # ========================================================
    # ABAS
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
    # ABA 1
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

            sexo_valor = v("SEXO").upper()

            opcoes_sexo = [
                "",
                "MASCULINO",
                "FEMININO"
            ]

            sexo = st.selectbox(
                "SEXO:",
                opcoes_sexo,
                index=(
                    opcoes_sexo.index(sexo_valor)
                    if sexo_valor in opcoes_sexo
                    else 0
                ),
                key=f"{prefixo}_sexo"
            )

            raca_valor = v("Raça/Cor").upper()

            opcoes_raca = [
                "",
                "BRANCA",
                "PRETA",
                "PARDA",
                "AMARELA",
                "INDÍGENA"
            ]

            raca_cor = st.selectbox(
                "Raça/Cor:",
                opcoes_raca,
                index=(
                    opcoes_raca.index(raca_valor)
                    if raca_valor in opcoes_raca
                    else 0
                ),
                key=f"{prefixo}_raca"
            )

        with c3:

            posto_grad = st.text_input(
                "Posto/ Grad:",
                value=v("Posto/ Grad"),
                key=f"{prefixo}_posto"
            )

            fones = st.text_input(
                "Fones:",
                value=v("Fones"),
                key=f"{prefixo}_fones"
            )

            ano_ingresso = st.text_input(
                "Ano de ingresso:",
                value=v("Ano de ingresso"),
                key=f"{prefixo}_ano"
            )

            data_praca = st.text_input(
                "Data de praça:",
                value=v("Data de praça"),
                key=f"{prefixo}_praca"
            )

    # ========================================================
    # ABA 2
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
                value=v("Tempo de serviço (anos)"),
                key=f"{prefixo}_tempo_anos"
            )

            tempo_servico_amd = st.text_input(
                "Tempo de serviço (ano, mês, dias):",
                value=v("Tempo de serviço (ano, mês, dias)"),
                key=f"{prefixo}_tempo_amd"
            )

            tempo_servico_dias = st.text_input(
                "Tempo de serviço (dias):",
                value=v("Tempo de serviço (dias)"),
                key=f"{prefixo}_tempo_dias"
            )

            tempo_obm_atual = st.text_input(
                "Tempo na OBM atual:",
                value=v("Tempo na OBM atual"),
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
    # ABA 3
    # ========================================================

    with tab_cessao:

        c1, c2, c3 = st.columns(3)

        with c1:

            data_mov_sp = st.text_input(
                "Data da Movimentação em SP:",
                value=v("Data da Movimentação em SP"),
                key=f"{prefixo}_mov_sp"
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
                key=f"{prefixo}_chegada"
            )

            movimentado = st.text_input(
                "Movimentado:",
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

            onus_valor = v("Ônus para Origem").upper()

            opcoes_onus = [
                "",
                "SIM",
                "NÃO"
            ]

            onus_origem = st.selectbox(
                "Ônus para Origem:",
                opcoes_onus,
                index=(
                    opcoes_onus.index(onus_valor)
                    if onus_valor in opcoes_onus
                    else 0
                ),
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
    # ABA 4
    # ========================================================

    with tab_ltip:

        c1, c2 = st.columns(2)

        with c1:

            afastamentos = st.text_area(
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP:",
                value=v(
                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP"
                ),
                key=f"{prefixo}_afastamentos"
            )

            inicio_ltip = st.text_input(
                "INÍCIO DA LTIP:",
                value=v("INÍCIO DA LTIP"),
                key=f"{prefixo}_inicio_ltip"
            )

            termino_ltip = st.text_input(
                "TÉRMINO DA LTIP:",
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
    # ABA 5
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
                key=f"{prefixo}_doc"
            )

            sp_adicao = st.text_input(
                "SP da Adição:",
                value=v("SP da Adição"),
                key=f"{prefixo}_sp"
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
        "Data da última promoção ou Implant. PCNH": data_ult_promocao,
        "Princípio da última promoção": principio_ult_promocao,
        "Tempo no Posto/Grad. atual EM DIAS": tempo_posto_atual_dias,
        "Data da Movimentação em SP": data_mov_sp,
        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO": ome_anterior,
        "Data de chegada na OBM Anteior": data_chegada,
        "Movimentado (apagar antes de atualizar o SP)": movimentado,
        "ÓRGÃO": orgao,
        "Poder": poder,
        "Ônus para Origem": onus_origem,
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
# MONTAR LINHA DE ACORDO COM OS CABEÇALHOS DA PLANILHA
# ============================================================

def montar_linha(headers, dados):

    linha = []

    for header in headers:

        if header in dados:

            valor = dados[header]

        else:

            valor = ""

        valor = limpar_valor(valor)

        linha.append(valor)

    return linha


# ============================================================
# LOCALIZAR MATRÍCULA
# ============================================================

def localizar_matricula(sheet, matricula):

    headers = sheet.row_values(1)

    if "Matrícula" not in headers:

        raise Exception(
            "A coluna 'Matrícula' não existe na primeira linha da planilha."
        )

    coluna = headers.index("Matrícula") + 1

    valores = sheet.col_values(coluna)

    matricula_procurada = limpar_valor(matricula)

    for numero_linha, valor in enumerate(valores, start=1):

        if numero_linha == 1:
            continue

        if limpar_valor(valor) == matricula_procurada:

            return numero_linha

    return None


# ============================================================
# CABEÇALHO
# ============================================================

st.sidebar.success("Autenticado com sucesso!")

if st.sidebar.button("🚪 Sair / Logout"):

    st.session_state["password_correct"] = False

    st.rerun()


if st.sidebar.button("🔄 Forçar Atualização"):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# LOGOS
# ============================================================

_, col_img1, col_img2, _ = st.columns(
    [2, 1, 1, 2]
)

with col_img1:

    st.image(
        "images.png",
        width=140
    )

with col_img2:

    st.image(
        "11679.png",
        width=140
    )


st.markdown(
    "<h1 style='text-align:center;'>DGP - Dados dos Militares</h1>",
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

try:

    # --------------------------------------------------------
    # CARREGA DADOS
    # --------------------------------------------------------

    df = load_data()

    st.subheader("📋 Visualização dos Registros")

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
        "➕ NOVO CADASTRO DE MILITAR",
        expanded=False
    ):

        st.info(
            "Preencha os dados e clique em "
            "**💾 SALVAR NOVO CADASTRO**."
        )

        # ----------------------------------------------------
        # FORMULÁRIO
        # ----------------------------------------------------

        with st.form(
            "form_novo_cadastro",
            clear_on_submit=False
        ):

            novos_dados = formulario_militar(
                dados=None,
                prefixo="novo"
            )

            st.markdown("---")

            salvar_novo = st.form_submit_button(
                "💾 SALVAR NOVO CADASTRO",
                type="primary",
                use_container_width=True
            )

        # ----------------------------------------------------
        # SALVAR
        # ----------------------------------------------------

        if salvar_novo:

            try:

                matricula = limpar_valor(
                    novos_dados.get("Matrícula")
                )

                nome = limpar_valor(
                    novos_dados.get("Nome")
                )

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

                st.info(
                    "🔄 Conectando ao Google Sheets..."
                )

                spreadsheet, sheet = get_sheet()

                st.success(
                    f"✅ Conectado à planilha: "
                    f"{spreadsheet.title}"
                )

                headers = sheet.row_values(1)

                if not headers:

                    st.error(
                        "❌ A planilha não possui cabeçalho."
                    )

                    st.stop()

                # --------------------------------------------
                # CONFERE MATRÍCULA
                # --------------------------------------------

                linha_existente = localizar_matricula(
                    sheet,
                    matricula
                )

                if linha_existente:

                    st.error(
                        f"❌ A matrícula **{matricula}** "
                        f"já existe na linha "
                        f"**{linha_existente}**."
                    )

                    st.stop()

                # --------------------------------------------
                # MONTA LINHA
                # --------------------------------------------

                nova_linha = montar_linha(
                    headers,
                    novos_dados
                )

                # --------------------------------------------
                # VERIFICA
                # --------------------------------------------

                if len(nova_linha) != len(headers):

                    st.error(
                        "❌ Erro interno: quantidade de "
                        "colunas diferente."
                    )

                    st.write(
                        "Cabeçalhos:",
                        len(headers)
                    )

                    st.write(
                        "Valores:",
                        len(nova_linha)
                    )

                    st.stop()

                # --------------------------------------------
                # GRAVA
                # --------------------------------------------

                st.info(
                    "💾 Gravando cadastro no Google Sheets..."
                )

                sheet.append_row(
                    nova_linha,
                    value_input_option="USER_ENTERED"
                )

                # --------------------------------------------
                # CONFIRMA LENDO NOVAMENTE
                # --------------------------------------------

                time.sleep(1)

                linha_confirmada = localizar_matricula(
                    sheet,
                    matricula
                )

                if not linha_confirmada:

                    st.error(
                        "⚠️ O comando de gravação foi "
                        "executado, mas a matrícula não "
                        "foi localizada na planilha após "
                        "a gravação."
                    )

                else:

                    st.success(
                        f"🎉 CADASTRO SALVO COM SUCESSO!\n\n"
                        f"**Matrícula:** {matricula}\n\n"
                        f"**Nome:** {nome}\n\n"
                        f"**Linha:** {linha_confirmada}"
                    )

                    st.cache_data.clear()

                    time.sleep(1)

                    st.rerun()

            except Exception as erro:

                st.error(
                    "❌ ERRO AO SALVAR O CADASTRO"
                )

                st.exception(erro)


    # ========================================================
    # EDITAR
    # ========================================================

    with st.expander(
        "✏️ EDITAR REGISTRO EXISTENTE",
        expanded=False
    ):

        if (
            "Matrícula" not in df.columns
            or "Nome" not in df.columns
        ):

            st.error(
                "❌ As colunas Matrícula e Nome "
                "precisam existir na planilha."
            )

        elif df.empty:

            st.info(
                "Nenhum registro encontrado."
            )

        else:

            opcoes = []

            for _, row in df.iterrows():

                matricula = limpar_valor(
                    row.get("Matrícula", "")
                )

                nome = limpar_valor(
                    row.get("Nome", "")
                )

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

                if registro.empty:

                    st.error(
                        "❌ Registro não localizado."
                    )

                else:

                    dados_militar = (
                        registro.iloc[0].to_dict()
                    )

                    st.info(
                        f"Editando: **{dados_militar.get('Nome', '')}**"
                    )

                    with st.form(
                        "form_edicao",
                        clear_on_submit=False
                    ):

                        dados_editados = formulario_militar(
                            dados=dados_militar,
                            prefixo="editar"
                        )

                        dados_editados["Matrícula"] = (
                            matricula_editar
                        )

                        atualizar = st.form_submit_button(
                            "💾 SALVAR ALTERAÇÕES",
                            type="primary",
                            use_container_width=True
                        )

                    if atualizar:

                        try:

                            spreadsheet, sheet = get_sheet()

                            headers = sheet.row_values(1)

                            linha = localizar_matricula(
                                sheet,
                                matricula_editar
                            )

                            if not linha:

                                st.error(
                                    "❌ Matrícula não encontrada "
                                    "no Google Sheets."
                                )

                                st.stop()

                            nova_linha = montar_linha(
                                headers,
                                dados_editados
                            )

                            st.info(
                                f"💾 Atualizando linha {linha}..."
                            )

                            # --------------------------------
                            # ATUALIZA SOMENTE A LINHA
                            # --------------------------------

                            sheet.update(
                                f"A{linha}:{gspread.utils.rowcol_to_a1(linha, len(headers)).split(str(linha))[0]}{linha}",
                                [nova_linha],
                                value_input_option="USER_ENTERED"
                            )

                            st.success(
                                f"✅ Registro da matrícula "
                                f"**{matricula_editar}** "
                                f"atualizado com sucesso!"
                            )

                            st.cache_data.clear()

                            time.sleep(1)

                            st.rerun()

                        except Exception as erro:

                            st.error(
                                "❌ ERRO AO ATUALIZAR"
                            )

                            st.exception(erro)


    # ========================================================
    # EXCLUIR
    # ========================================================

    with st.expander(
        "🗑️ EXCLUIR REGISTRO",
        expanded=False
    ):

        if (
            "Matrícula" not in df.columns
            or "Nome" not in df.columns
        ):

            st.error(
                "❌ As colunas Matrícula e Nome "
                "precisam existir."
            )

        elif df.empty:

            st.info(
                "Nenhum registro encontrado."
            )

        else:

            opcoes_exclusao = []

            for _, row in df.iterrows():

                matricula = limpar_valor(
                    row.get("Matrícula", "")
                )

                nome = limpar_valor(
                    row.get("Nome", "")
                )

                if matricula:

                    opcoes_exclusao.append(
                        f"{matricula} - {nome}"
                    )

            selecionado_exclusao = st.selectbox(
                "Selecione o militar:",
                [""] + opcoes_exclusao,
                key="militar_exclusao"
            )

            if selecionado_exclusao:

                matricula_excluir = (
                    selecionado_exclusao
                    .split(" - ", 1)[0]
                    .strip()
                )

                registro = df[
                    df["Matrícula"].astype(str).str.strip()
                    == matricula_excluir
                ]

                st.dataframe(
                    registro,
                    use_container_width=True,
                    hide_index=True
                )

                confirmar = st.checkbox(
                    "Confirmo que desejo excluir permanentemente este registro.",
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

                        spreadsheet, sheet = get_sheet()

                        linha = localizar_matricula(
                            sheet,
                            matricula_excluir
                        )

                        if not linha:

                            st.error(
                                "❌ Matrícula não encontrada."
                            )

                            st.stop()

                        sheet.delete_rows(
                            linha
                        )

                        st.success(
                            f"✅ Matrícula "
                            f"**{matricula_excluir}** "
                            f"excluída com sucesso."
                        )

                        st.cache_data.clear()

                        time.sleep(1)

                        st.rerun()

                    except Exception as erro:

                        st.error(
                            "❌ ERRO AO EXCLUIR"
                        )

                        st.exception(erro)


# ============================================================
# ERROS GERAIS
# ============================================================

except KeyError as erro:

    st.error(
        f"❌ Chave não encontrada no secrets.toml: {erro}"
    )

except Exception as erro:

    st.error(
        "❌ ERRO GERAL DA APLICAÇÃO"
    )

    st.exception(erro)
