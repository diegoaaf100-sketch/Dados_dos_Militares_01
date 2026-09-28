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
# ESCOPOS GOOGLE
# ============================================================
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
            on_click=password_entered,
            use_container_width=True
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
# AUTENTICAÇÃO GOOGLE SHEETS
# ============================================================
def get_gspread_client():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


# ============================================================
# FUNÇÃO PARA OBTER A PLANILHA
# ============================================================
def get_sheet(sheet_id):

    client = get_gspread_client()

    spreadsheet = client.open_by_key(sheet_id)

    sheet = spreadsheet.sheet1

    return spreadsheet, sheet


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.success("Autenticado com sucesso!")

if st.sidebar.button(
    "🚪 Sair / Logout",
    use_container_width=True
):

    st.session_state["password_correct"] = False
    st.rerun()


if st.sidebar.button(
    "🔄 Forçar Atualização",
    use_container_width=True
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
    """
    <h1 style='text-align: center;'>
        DGP - Dados dos Militares
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================
@st.cache_data(ttl=5)
def load_data(sheet_id):

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv"
    )

    df = pd.read_csv(
        url,
        header=0,
        dtype=str
    )

    df.columns = [
        str(col).strip().replace(":", "-")
        for col in df.columns
    ]

    df = df.fillna("")

    return df


# ============================================================
# FUNÇÃO AUXILIAR
# ============================================================
def limpar_valor(valor):

    if valor is None:
        return ""

    if pd.isna(valor):
        return ""

    return str(valor)


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
try:

    SHEET_ID = st.secrets["SHEET_ID"]

    # ========================================================
    # CARREGA DADOS
    # ========================================================
    df = load_data(SHEET_ID)

    st.subheader("📋 Visualização dos Registros")

    st.dataframe(
        df,
        use_container_width=True,
        height=450
    )

    st.markdown("---")


    # ========================================================
    # 1. NOVO CADASTRO
    # ========================================================
    with st.expander(
        "➕ **Novo Cadastro de Militar**",
        expanded=False
    ):

        st.info(
            "Preencha os dados abaixo. "
            "Depois clique em **💾 SALVAR NOVO CADASTRO**. "
            "Os campos não serão enviados até você clicar no botão."
        )

        # ====================================================
        # FORMULÁRIO
        # ====================================================
        with st.form(
            "form_novo_cadastro",
            clear_on_submit=False
        ):

            # =================================================
            # ABA 1
            # =================================================
            tab_pessoal, tab_lotacao, tab_cessao, tab_ltip, tab_outros = st.tabs(
                [
                    "👤 Identificação & Pessoal",
                    "🏢 Lotação & Promoção",
                    "🔄 Cessão & Movimentação",
                    "⏳ LTIP & Afastamentos",
                    "📝 Documentos & Observações",
                ]
            )

            # =================================================
            # ABA 1 - PESSOAL
            # =================================================
            with tab_pessoal:

                c1, c2, c3 = st.columns(3)

                with c1:

                    novo_num_funcional = st.text_input(
                        "nº Funcional:",
                        key="cad_num_funcional"
                    )

                    novo_matricula = st.text_input(
                        "Matrícula:",
                        key="cad_matricula"
                    )

                    novo_cpf_ponto = st.text_input(
                        "CPF.:",
                        key="cad_cpf_ponto"
                    )

                    novo_cpf = st.text_input(
                        "CPF:",
                        key="cad_cpf"
                    )

                    novo_num_ident = st.text_input(
                        "Nº IDENT.:",
                        key="cad_num_ident"
                    )

                with c2:

                    novo_nome = st.text_input(
                        "Nome:",
                        key="cad_nome"
                    )

                    novo_nome_guerra = st.text_input(
                        "Nome de Guerra:",
                        key="cad_nome_guerra"
                    )

                    novo_sexo = st.selectbox(
                        "SEXO:",
                        [
                            "",
                            "MASCULINO",
                            "FEMININO"
                        ],
                        key="cad_sexo"
                    )

                    novo_raca = st.selectbox(
                        "Raça/Cor:",
                        [
                            "",
                            "BRANCA",
                            "PRETA",
                            "PARDA",
                            "AMARELA",
                            "INDÍGENA"
                        ],
                        key="cad_raca"
                    )

                with c3:

                    novo_posto_grad = st.text_input(
                        "Posto/ Grad:",
                        key="cad_posto_grad"
                    )

                    novo_fones = st.text_input(
                        "Fones:",
                        key="cad_fones"
                    )

                    novo_ano_ingresso = st.text_input(
                        "Ano de ingresso:",
                        key="cad_ano_ingresso"
                    )

                    novo_data_praca = st.text_input(
                        "Data de praça:",
                        key="cad_data_praca"
                    )


            # =================================================
            # ABA 2 - LOTAÇÃO
            # =================================================
            with tab_lotacao:

                c1, c2, c3 = st.columns(3)

                with c1:

                    novo_ome = st.text_input(
                        "OME:",
                        key="cad_ome"
                    )

                    novo_ome_qod = st.text_input(
                        "OME QOD:",
                        key="cad_ome_qod"
                    )

                    novo_atividade = st.text_input(
                        "Atividade:",
                        key="cad_atividade"
                    )

                    novo_municipio = st.text_input(
                        "Município:",
                        key="cad_municipio"
                    )

                    novo_regiao = st.text_input(
                        "Região:",
                        key="cad_regiao"
                    )

                with c2:

                    novo_tempo_servico_anos = st.text_input(
                        "Tempo de serviço (anos):",
                        key="cad_tempo_servico_anos"
                    )

                    novo_tempo_servico_amd = st.text_input(
                        "Tempo de serviço (ano, mês, dias):",
                        key="cad_tempo_servico_amd"
                    )

                    novo_tempo_servico_dias = st.text_input(
                        "Tempo de serviço (dias):",
                        key="cad_tempo_servico_dias"
                    )

                    novo_tempo_obm_atual = st.text_input(
                        "Tempo na OBM atual:",
                        key="cad_tempo_obm_atual"
                    )

                with c3:

                    novo_data_ult_promocao = st.text_input(
                        "Data da última promoção ou Implant. PCNH:",
                        key="cad_data_ult_promocao"
                    )

                    novo_principio_ult_promocao = st.text_input(
                        "Princípio da última promoção:",
                        key="cad_principio_promocao"
                    )

                    novo_tempo_posto_atual_dias = st.text_input(
                        "Tempo no Posto/Grad. atual EM DIAS:",
                        key="cad_tempo_posto"
                    )


            # =================================================
            # ABA 3 - CESSÃO
            # =================================================
            with tab_cessao:

                c1, c2, c3 = st.columns(3)

                with c1:

                    novo_data_mov_sp = st.text_input(
                        "Data da Movimentação em SP:",
                        key="cad_data_mov_sp"
                    )

                    novo_ome_anterior = st.text_input(
                        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:",
                        key="cad_ome_anterior"
                    )

                    novo_data_chegada = st.text_input(
                        "Data de chegada na OBM Anteior:",
                        key="cad_data_chegada"
                    )

                    novo_movimentado = st.text_input(
                        "Movimentado (apagar antes de atualizar o SP):",
                        key="cad_movimentado"
                    )

                with c2:

                    novo_orgao = st.text_input(
                        "ÓRGÃO:",
                        key="cad_orgao"
                    )

                    novo_poder = st.text_input(
                        "Poder:",
                        key="cad_poder"
                    )

                    novo_onus = st.selectbox(
                        "Ônus para Origem:",
                        [
                            "",
                            "SIM",
                            "NÃO"
                        ],
                        key="cad_onus"
                    )

                    novo_inicio_cessao = st.text_input(
                        "Início da Cessão ou requisição:",
                        key="cad_inicio_cessao"
                    )

                with c3:

                    novo_renovacao = st.text_input(
                        "Renovação de cessão - Atos/Portarias/Documentos:",
                        key="cad_renovacao"
                    )

                    novo_doe = st.text_input(
                        "DOE/BGSDS de renovação:",
                        key="cad_doe"
                    )

                    novo_sei = st.text_input(
                        "SEI deslig.:",
                        key="cad_sei"
                    )


            # =================================================
            # ABA 4 - LTIP
            # =================================================
            with tab_ltip:

                c1, c2 = st.columns(2)

                with c1:

                    novo_afastamentos = st.text_area(
                        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
                        "ININTERRUPTOS, PUBLICADOS EM SP:",
                        key="cad_afastamentos"
                    )

                    novo_inicio_ltip = st.text_input(
                        "INÍCIO DA LTIP:",
                        key="cad_inicio_ltip"
                    )

                    novo_termino_ltip = st.text_input(
                        "TÉRMINO DA LTIP (inserir data de apresentação):",
                        key="cad_termino_ltip"
                    )

                with c2:

                    novo_somatorio_anos = st.text_input(
                        "Somatório LTIP gozada em anos:",
                        key="cad_somatorio_anos"
                    )

                    novo_somatorio_amd = st.text_input(
                        "Somatório LTIP gozada em anos/meses/dias:",
                        key="cad_somatorio_amd"
                    )

                    novo_somatorio_dias = st.text_input(
                        "Somatório de todas LTIP gozadas em dias:",
                        key="cad_somatorio_dias"
                    )

                    novo_total_ltip = st.text_input(
                        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:",
                        key="cad_total_ltip"
                    )


            # =================================================
            # ABA 5 - DOCUMENTOS
            # =================================================
            with tab_outros:

                c1, c2 = st.columns(2)

                with c1:

                    novo_ato = st.text_input(
                        "Ato:",
                        key="cad_ato"
                    )

                    novo_doc_publicacao = st.text_input(
                        "Doc. Publicação:",
                        key="cad_doc_publicacao"
                    )

                    novo_sp_adicao = st.text_input(
                        "SP da Adição:",
                        key="cad_sp_adicao"
                    )

                    novo_processo_rr = st.text_input(
                        "Processo RR:",
                        key="cad_processo_rr"
                    )

                with c2:

                    novo_suplemento = st.text_input(
                        "Suplemento de Pessoal nº/Ano:",
                        key="cad_suplemento"
                    )

                    novo_data_suplemento = st.text_input(
                        "Data Suplemento de Pessoal:",
                        key="cad_data_suplemento"
                    )

                    novo_hoje = st.text_input(
                        "Hoje:",
                        key="cad_hoje"
                    )

                    novo_obs = st.text_area(
                        "OBS:",
                        key="cad_obs"
                    )


            # =================================================
            # BOTÃO DO FORMULÁRIO
            # =================================================
            salvar_novo = st.form_submit_button(
                "💾 SALVAR NOVO CADASTRO",
                type="primary",
                use_container_width=True
            )


        # ====================================================
        # PROCESSAMENTO DO CADASTRO
        # ====================================================
        if salvar_novo:

            matricula_nova = str(
                novo_matricula
            ).strip()

            nome_novo = str(
                novo_nome
            ).strip()


            # =================================================
            # VALIDAÇÕES
            # =================================================
            if not matricula_nova:

                st.error(
                    "❌ Informe a **Matrícula**."
                )

                st.stop()


            if not nome_novo:

                st.error(
                    "❌ Informe o **Nome**."
                )

                st.stop()


            try:

                with st.spinner(
                    "💾 Salvando cadastro no Google Sheets..."
                ):

                    # =========================================
                    # CONECTA AO GOOGLE
                    # =========================================
                    spreadsheet, sheet = get_sheet(
                        SHEET_ID
                    )


                    # =========================================
                    # LÊ CABEÇALHOS
                    # =========================================
                    headers = sheet.row_values(1)

                    if not headers:

                        st.error(
                            "❌ A primeira linha da planilha "
                            "não possui cabeçalhos."
                        )

                        st.stop()


                    # =========================================
                    # NORMALIZA CABEÇALHOS
                    # =========================================
                    headers = [
                        str(h).strip()
                        for h in headers
                    ]


                    # =========================================
                    # CONFERE MATRÍCULA
                    # =========================================
                    if "Matrícula" not in headers:

                        st.error(
                            "❌ A coluna 'Matrícula' "
                            "não foi encontrada na planilha."
                        )

                        st.write(
                            "Cabeçalhos encontrados:"
                        )

                        st.write(headers)

                        st.stop()


                    coluna_matricula = (
                        headers.index("Matrícula") + 1
                    )


                    # =========================================
                    # BUSCA MATRÍCULAS EXISTENTES
                    # =========================================
                    valores_matricula = (
                        sheet.col_values(
                            coluna_matricula
                        )
                    )


                    matriculas_existentes = {
                        str(valor).strip()
                        for valor in valores_matricula[1:]
                        if str(valor).strip()
                    }


                    # =========================================
                    # DUPLICIDADE
                    # =========================================
                    if matricula_nova in matriculas_existentes:

                        st.error(
                            f"❌ A matrícula "
                            f"**{matricula_nova}** "
                            f"já existe na planilha."
                        )

                        st.stop()


                    # =========================================
                    # MONTA DICIONÁRIO
                    # =========================================
                    novos_dados = {

                        "nº Funcional":
                            novo_num_funcional,

                        "Matrícula":
                            matricula_nova,

                        "CPF.":
                            novo_cpf_ponto,

                        "CPF":
                            novo_cpf,

                        "Nº IDENT.":
                            novo_num_ident,

                        "Nome":
                            nome_novo,

                        "Nome de Guerra":
                            novo_nome_guerra,

                        "SEXO":
                            novo_sexo,

                        "Raça/Cor":
                            novo_raca,

                        "Posto/ Grad":
                            novo_posto_grad,

                        "Fones":
                            novo_fones,

                        "Ano de ingresso":
                            novo_ano_ingresso,

                        "Data de praça":
                            novo_data_praca,

                        "OME":
                            novo_ome,

                        "OME QOD":
                            novo_ome_qod,

                        "Atividade":
                            novo_atividade,

                        "Município":
                            novo_municipio,

                        "Região":
                            novo_regiao,

                        "Tempo de serviço (anos)":
                            novo_tempo_servico_anos,

                        "Tempo de serviço (ano, mês, dias)":
                            novo_tempo_servico_amd,

                        "Tempo de serviço (dias)":
                            novo_tempo_servico_dias,

                        "Tempo na OBM atual":
                            novo_tempo_obm_atual,

                        "Data da última promoção ou Implant. PCNH":
                            novo_data_ult_promocao,

                        "Princípio da última promoção":
                            novo_principio_ult_promocao,

                        "Tempo no Posto/Grad. atual EM DIAS":
                            novo_tempo_posto_atual_dias,

                        "Data da Movimentação em SP":
                            novo_data_mov_sp,

                        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO":
                            novo_ome_anterior,

                        "Data de chegada na OBM Anteior":
                            novo_data_chegada,

                        "Movimentado (apagar antes de atualizar o SP)":
                            novo_movimentado,

                        "ÓRGÃO":
                            novo_orgao,

                        "Poder":
                            novo_poder,

                        "Ônus para Origem":
                            novo_onus,

                        "Início da Cessão ou requisição":
                            novo_inicio_cessao,

                        "Renovação de cessão - Atos/Portarias/Documentos":
                            novo_renovacao,

                        "DOE/BGSDS de renovação":
                            novo_doe,

                        "SEI deslig.":
                            novo_sei,

                        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP":
                            novo_afastamentos,

                        "INÍCIO DA LTIP":
                            novo_inicio_ltip,

                        "TÉRMINO DA LTIP (inserir data de apresentação)":
                            novo_termino_ltip,

                        "Somatório LTIP gozada em anos":
                            novo_somatorio_anos,

                        "Somatório LTIP gozada em anos/meses/dias":
                            novo_somatorio_amd,

                        "Somatório de todas LTIP gozadas em dias":
                            novo_somatorio_dias,

                        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.":
                            novo_total_ltip,

                        "Ato":
                            novo_ato,

                        "Doc. Publicação":
                            novo_doc_publicacao,

                        "SP da Adição":
                            novo_sp_adicao,

                        "Processo RR":
                            novo_processo_rr,

                        "Suplemento de Pessoal nº/Ano":
                            novo_suplemento,

                        "Data Suplemento de Pessoal":
                            novo_data_suplemento,

                        "Hoje":
                            novo_hoje,

                        "OBS":
                            novo_obs,
                    }


                    # =========================================
                    # MONTA LINHA EXATAMENTE NA ORDEM
                    # DOS CABEÇALHOS DA PLANILHA
                    # =========================================
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


                    # =========================================
                    # GRAVA
                    # =========================================
                    sheet.append_row(
                        nova_linha,
                        value_input_option="USER_ENTERED"
                    )


                    # =========================================
                    # CONFIRMAÇÃO REAL
                    # =========================================
                    valores_depois = (
                        sheet.col_values(
                            coluna_matricula
                        )
                    )

                    encontrou = any(
                        str(valor).strip()
                        == matricula_nova
                        for valor in valores_depois
                    )


                    if not encontrou:

                        st.error(
                            "❌ O Google Sheets não confirmou "
                            "a gravação da nova matrícula."
                        )

                        st.stop()


                # =============================================
                # SUCESSO
                # =============================================
                st.success(
                    f"🎉 Cadastro salvo com sucesso!\n\n"
                    f"**Matrícula:** {matricula_nova}\n\n"
                    f"**Nome:** {nome_novo}"
                )

                st.balloons()


                # =============================================
                # LIMPA CACHE
                # =============================================
                st.cache_data.clear()


                # =============================================
                # MOSTRA A LINHA GRAVADA
                # =============================================
                st.info(
                    "✅ O registro foi gravado no Google Sheets. "
                    "Atualizando a tabela..."
                )

                st.rerun()


            except Exception as erro:

                st.error(
                    "❌ ERRO AO SALVAR O NOVO CADASTRO"
                )

                st.exception(erro)


    # ========================================================
    # 2. EDITAR REGISTRO
    # ========================================================
    with st.expander(
        "✏️ **Editar Registro Existente**",
        expanded=False
    ):

        if (
            "Matrícula" in df.columns
            and "Nome" in df.columns
        ):

            opcoes_militares_edicao = df.apply(
                lambda r:
                f"{r['Matrícula']} - {r['Nome']}",
                axis=1
            ).tolist()


            militar_selecionado_edicao = st.selectbox(
                "Selecione o militar que deseja editar:",
                [""] + opcoes_militares_edicao,
                key="seletor_militar_edicao"
            )


            if militar_selecionado_edicao:

                matricula_editar = (
                    militar_selecionado_edicao
                    .split(" - ")[0]
                    .strip()
                )


                registros = df[
                    df["Matrícula"].astype(str)
                    .str.strip()
                    == matricula_editar
                ]


                if registros.empty:

                    st.error(
                        "❌ Registro não localizado."
                    )

                else:

                    dados_militar = (
                        registros.iloc[0].to_dict()
                    )


                    st.info(
                        f"Editando: "
                        f"**{dados_militar.get('Nome', '')}** "
                        f"| Matrícula: "
                        f"**{matricula_editar}**"
                    )


                    # =================================================
                    # FORMULÁRIO DE EDIÇÃO
                    # =================================================
                    with st.form(
                        "form_edicao_militar",
                        clear_on_submit=False
                    ):

                        tab_ed_pessoal, tab_ed_lotacao, tab_ed_cessao, tab_ed_ltip, tab_ed_outros = st.tabs(
                            [
                                "👤 Identificação & Pessoal",
                                "🏢 Lotação & Promoção",
                                "🔄 Cessão & Movimentação",
                                "⏳ LTIP & Afastamentos",
                                "📝 Documentos & Observações",
                            ]
                        )


                        def valor_edicao(coluna):

                            return limpar_valor(
                                dados_militar.get(
                                    coluna,
                                    ""
                                )
                            )


                        # =================================================
                        # ABA PESSOAL
                        # =================================================
                        with tab_ed_pessoal:

                            c1, c2, c3 = st.columns(3)

                            with c1:

                                e_num_funcional = st.text_input(
                                    "nº Funcional:",
                                    value=valor_edicao(
                                        "nº Funcional"
                                    ),
                                    key="ed_num_funcional"
                                )

                                st.text_input(
                                    "Matrícula:",
                                    value=matricula_editar,
                                    disabled=True,
                                    key="ed_matricula_visual"
                                )

                                e_cpf_ponto = st.text_input(
                                    "CPF.:",
                                    value=valor_edicao("CPF."),
                                    key="ed_cpf_ponto"
                                )

                                e_cpf = st.text_input(
                                    "CPF:",
                                    value=valor_edicao("CPF"),
                                    key="ed_cpf"
                                )

                                e_num_ident = st.text_input(
                                    "Nº IDENT.:",
                                    value=valor_edicao("Nº IDENT."),
                                    key="ed_num_ident"
                                )

                            with c2:

                                e_nome = st.text_input(
                                    "Nome:",
                                    value=valor_edicao("Nome"),
                                    key="ed_nome"
                                )

                                e_nome_guerra = st.text_input(
                                    "Nome de Guerra:",
                                    value=valor_edicao(
                                        "Nome de Guerra"
                                    ),
                                    key="ed_nome_guerra"
                                )

                                sexo_atual = (
                                    valor_edicao("SEXO")
                                    .upper()
                                )

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

                                e_sexo = st.selectbox(
                                    "SEXO:",
                                    opcoes_sexo,
                                    index=idx_sexo,
                                    key="ed_sexo"
                                )


                                raca_atual = (
                                    valor_edicao(
                                        "Raça/Cor"
                                    ).upper()
                                )

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

                                e_raca = st.selectbox(
                                    "Raça/Cor:",
                                    opcoes_raca,
                                    index=idx_raca,
                                    key="ed_raca"
                                )

                            with c3:

                                e_posto_grad = st.text_input(
                                    "Posto/ Grad:",
                                    value=valor_edicao(
                                        "Posto/ Grad"
                                    ),
                                    key="ed_posto_grad"
                                )

                                e_fones = st.text_input(
                                    "Fones:",
                                    value=valor_edicao(
                                        "Fones"
                                    ),
                                    key="ed_fones"
                                )

                                e_ano_ingresso = st.text_input(
                                    "Ano de ingresso:",
                                    value=valor_edicao(
                                        "Ano de ingresso"
                                    ),
                                    key="ed_ano_ingresso"
                                )

                                e_data_praca = st.text_input(
                                    "Data de praça:",
                                    value=valor_edicao(
                                        "Data de praça"
                                    ),
                                    key="ed_data_praca"
                                )


                        # =================================================
                        # ABA LOTAÇÃO
                        # =================================================
                        with tab_ed_lotacao:

                            c1, c2, c3 = st.columns(3)

                            with c1:

                                e_ome = st.text_input(
                                    "OME:",
                                    value=valor_edicao("OME"),
                                    key="ed_ome"
                                )

                                e_ome_qod = st.text_input(
                                    "OME QOD:",
                                    value=valor_edicao("OME QOD"),
                                    key="ed_ome_qod"
                                )

                                e_atividade = st.text_input(
                                    "Atividade:",
                                    value=valor_edicao(
                                        "Atividade"
                                    ),
                                    key="ed_atividade"
                                )

                                e_municipio = st.text_input(
                                    "Município:",
                                    value=valor_edicao(
                                        "Município"
                                    ),
                                    key="ed_municipio"
                                )

                                e_regiao = st.text_input(
                                    "Região:",
                                    value=valor_edicao(
                                        "Região"
                                    ),
                                    key="ed_regiao"
                                )

                            with c2:

                                e_tempo_servico_anos = st.text_input(
                                    "Tempo de serviço (anos):",
                                    value=valor_edicao(
                                        "Tempo de serviço (anos)"
                                    ),
                                    key="ed_tempo_anos"
                                )

                                e_tempo_servico_amd = st.text_input(
                                    "Tempo de serviço (ano, mês, dias):",
                                    value=valor_edicao(
                                        "Tempo de serviço (ano, mês, dias)"
                                    ),
                                    key="ed_tempo_amd"
                                )

                                e_tempo_servico_dias = st.text_input(
                                    "Tempo de serviço (dias):",
                                    value=valor_edicao(
                                        "Tempo de serviço (dias)"
                                    ),
                                    key="ed_tempo_dias"
                                )

                                e_tempo_obm_atual = st.text_input(
                                    "Tempo na OBM atual:",
                                    value=valor_edicao(
                                        "Tempo na OBM atual"
                                    ),
                                    key="ed_tempo_obm"
                                )

                            with c3:

                                e_data_ult_promocao = st.text_input(
                                    "Data da última promoção ou Implant. PCNH:",
                                    value=valor_edicao(
                                        "Data da última promoção ou Implant. PCNH"
                                    ),
                                    key="ed_data_promocao"
                                )

                                e_principio_ult_promocao = st.text_input(
                                    "Princípio da última promoção:",
                                    value=valor_edicao(
                                        "Princípio da última promoção"
                                    ),
                                    key="ed_principio"
                                )

                                e_tempo_posto_atual_dias = st.text_input(
                                    "Tempo no Posto/Grad. atual EM DIAS:",
                                    value=valor_edicao(
                                        "Tempo no Posto/Grad. atual EM DIAS"
                                    ),
                                    key="ed_tempo_posto"
                                )


                        # =================================================
                        # ABA CESSÃO
                        # =================================================
                        with tab_ed_cessao:

                            c1, c2, c3 = st.columns(3)

                            with c1:

                                e_data_mov_sp = st.text_input(
                                    "Data da Movimentação em SP:",
                                    value=valor_edicao(
                                        "Data da Movimentação em SP"
                                    ),
                                    key="ed_data_mov_sp"
                                )

                                e_ome_anterior = st.text_input(
                                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:",
                                    value=valor_edicao(
                                        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO"
                                    ),
                                    key="ed_ome_anterior"
                                )

                                e_data_chegada = st.text_input(
                                    "Data de chegada na OBM Anteior:",
                                    value=valor_edicao(
                                        "Data de chegada na OBM Anteior"
                                    ),
                                    key="ed_data_chegada"
                                )

                                e_movimentado = st.text_input(
                                    "Movimentado (apagar antes de atualizar o SP):",
                                    value=valor_edicao(
                                        "Movimentado (apagar antes de atualizar o SP)"
                                    ),
                                    key="ed_movimentado"
                                )

                            with c2:

                                e_orgao = st.text_input(
                                    "ÓRGÃO:",
                                    value=valor_edicao(
                                        "ÓRGÃO"
                                    ),
                                    key="ed_orgao"
                                )

                                e_poder = st.text_input(
                                    "Poder:",
                                    value=valor_edicao(
                                        "Poder"
                                    ),
                                    key="ed_poder"
                                )

                                onus_atual = (
                                    valor_edicao(
                                        "Ônus para Origem"
                                    ).upper()
                                )

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

                                e_onus = st.selectbox(
                                    "Ônus para Origem:",
                                    opcoes_onus,
                                    index=idx_onus,
                                    key="ed_onus"
                                )

                                e_inicio_cessao = st.text_input(
                                    "Início da Cessão ou requisição:",
                                    value=valor_edicao(
                                        "Início da Cessão ou requisição"
                                    ),
                                    key="ed_inicio_cessao"
                                )

                            with c3:

                                e_renovacao = st.text_input(
                                    "Renovação de cessão - Atos/Portarias/Documentos:",
                                    value=valor_edicao(
                                        "Renovação de cessão - Atos/Portarias/Documentos"
                                    ),
                                    key="ed_renovacao"
                                )

                                e_doe = st.text_input(
                                    "DOE/BGSDS de renovação:",
                                    value=valor_edicao(
                                        "DOE/BGSDS de renovação"
                                    ),
                                    key="ed_doe"
                                )

                                e_sei = st.text_input(
                                    "SEI deslig.:",
                                    value=valor_edicao(
                                        "SEI deslig."
                                    ),
                                    key="ed_sei"
                                )


                        # =================================================
                        # ABA LTIP
                        # =================================================
                        with tab_ed_ltip:

                            c1, c2 = st.columns(2)

                            with c1:

                                e_afastamentos = st.text_area(
                                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP:",
                                    value=valor_edicao(
                                        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP"
                                    ),
                                    key="ed_afastamentos"
                                )

                                e_inicio_ltip = st.text_input(
                                    "INÍCIO DA LTIP:",
                                    value=valor_edicao(
                                        "INÍCIO DA LTIP"
                                    ),
                                    key="ed_inicio_ltip"
                                )

                                e_termino_ltip = st.text_input(
                                    "TÉRMINO DA LTIP (inserir data de apresentação):",
                                    value=valor_edicao(
                                        "TÉRMINO DA LTIP (inserir data de apresentação)"
                                    ),
                                    key="ed_termino_ltip"
                                )

                            with c2:

                                e_somatorio_anos = st.text_input(
                                    "Somatório LTIP gozada em anos:",
                                    value=valor_edicao(
                                        "Somatório LTIP gozada em anos"
                                    ),
                                    key="ed_somatorio_anos"
                                )

                                e_somatorio_amd = st.text_input(
                                    "Somatório LTIP gozada em anos/meses/dias:",
                                    value=valor_edicao(
                                        "Somatório LTIP gozada em anos/meses/dias"
                                    ),
                                    key="ed_somatorio_amd"
                                )

                                e_somatorio_dias = st.text_input(
                                    "Somatório de todas LTIP gozadas em dias:",
                                    value=valor_edicao(
                                        "Somatório de todas LTIP gozadas em dias"
                                    ),
                                    key="ed_somatorio_dias"
                                )

                                e_total_ltip = st.text_input(
                                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:",
                                    value=valor_edicao(
                                        "TOTAL DIAS EM LTIP no MESMO Posto/Grad."
                                    ),
                                    key="ed_total_ltip"
                                )


                        # =================================================
                        # ABA OUTROS
                        # =================================================
                        with tab_ed_outros:

                            c1, c2 = st.columns(2)

                            with c1:

                                e_ato = st.text_input(
                                    "Ato:",
                                    value=valor_edicao(
                                        "Ato"
                                    ),
                                    key="ed_ato"
                                )

                                e_doc_publicacao = st.text_input(
                                    "Doc. Publicação:",
                                    value=valor_edicao(
                                        "Doc. Publicação"
                                    ),
                                    key="ed_doc_publicacao"
                                )

                                e_sp_adicao = st.text_input(
                                    "SP da Adição:",
                                    value=valor_edicao(
                                        "SP da Adição"
                                    ),
                                    key="ed_sp_adicao"
                                )

                                e_processo_rr = st.text_input(
                                    "Processo RR:",
                                    value=valor_edicao(
                                        "Processo RR"
                                    ),
                                    key="ed_processo_rr"
                                )

                            with c2:

                                e_suplemento = st.text_input(
                                    "Suplemento de Pessoal nº/Ano:",
                                    value=valor_edicao(
                                        "Suplemento de Pessoal nº/Ano"
                                    ),
                                    key="ed_suplemento"
                                )

                                e_data_suplemento = st.text_input(
                                    "Data Suplemento de Pessoal:",
                                    value=valor_edicao(
                                        "Data Suplemento de Pessoal"
                                    ),
                                    key="ed_data_suplemento"
                                )

                                e_hoje = st.text_input(
                                    "Hoje:",
                                    value=valor_edicao(
                                        "Hoje"
                                    ),
                                    key="ed_hoje"
                                )

                                e_obs = st.text_area(
                                    "OBS:",
                                    value=valor_edicao(
                                        "OBS"
                                    ),
                                    key="ed_obs"
                                )


                        # =================================================
                        # BOTÃO ATUALIZAR
                        # =================================================
                        btn_atualizar = st.form_submit_button(
                            "🔄 ATUALIZAR REGISTRO NA PLANILHA",
                            type="primary",
                            use_container_width=True
                        )


                    # =====================================================
                    # PROCESSAMENTO DA EDIÇÃO
                    # =====================================================
                    if btn_atualizar:

                        try:

                            with st.spinner(
                                "🔄 Atualizando registro..."
                            ):

                                _, sheet = get_sheet(
                                    SHEET_ID
                                )


                                headers = [
                                    str(h).strip()
                                    for h in sheet.row_values(1)
                                ]


                                cell = sheet.find(
                                    matricula_editar
                                )


                                if not cell:

                                    st.error(
                                        "❌ Matrícula não localizada."
                                    )

                                    st.stop()


                                dados_editados = {

                                    "nº Funcional":
                                        e_num_funcional,

                                    "Matrícula":
                                        matricula_editar,

                                    "CPF.":
                                        e_cpf_ponto,

                                    "CPF":
                                        e_cpf,

                                    "Nº IDENT.":
                                        e_num_ident,

                                    "Nome":
                                        e_nome,

                                    "Nome de Guerra":
                                        e_nome_guerra,

                                    "SEXO":
                                        e_sexo,

                                    "Raça/Cor":
                                        e_raca,

                                    "Posto/ Grad":
                                        e_posto_grad,

                                    "Fones":
                                        e_fones,

                                    "Ano de ingresso":
                                        e_ano_ingresso,

                                    "Data de praça":
                                        e_data_praca,

                                    "OME":
                                        e_ome,

                                    "OME QOD":
                                        e_ome_qod,

                                    "Atividade":
                                        e_atividade,

                                    "Município":
                                        e_municipio,

                                    "Região":
                                        e_regiao,

                                    "Tempo de serviço (anos)":
                                        e_tempo_servico_anos,

                                    "Tempo de serviço (ano, mês, dias)":
                                        e_tempo_servico_amd,

                                    "Tempo de serviço (dias)":
                                        e_tempo_servico_dias,

                                    "Tempo na OBM atual":
                                        e_tempo_obm_atual,

                                    "Data da última promoção ou Implant. PCNH":
                                        e_data_ult_promocao,

                                    "Princípio da última promoção":
                                        e_principio_ult_promocao,

                                    "Tempo no Posto/Grad. atual EM DIAS":
                                        e_tempo_posto_atual_dias,

                                    "Data da Movimentação em SP":
                                        e_data_mov_sp,

                                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO":
                                        e_ome_anterior,

                                    "Data de chegada na OBM Anteior":
                                        e_data_chegada,

                                    "Movimentado (apagar antes de atualizar o SP)":
                                        e_movimentado,

                                    "ÓRGÃO":
                                        e_orgao,

                                    "Poder":
                                        e_poder,

                                    "Ônus para Origem":
                                        e_onus,

                                    "Início da Cessão ou requisição":
                                        e_inicio_cessao,

                                    "Renovação de cessão - Atos/Portarias/Documentos":
                                        e_renovacao,

                                    "DOE/BGSDS de renovação":
                                        e_doe,

                                    "SEI deslig.":
                                        e_sei,

                                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP":
                                        e_afastamentos,

                                    "INÍCIO DA LTIP":
                                        e_inicio_ltip,

                                    "TÉRMINO DA LTIP (inserir data de apresentação)":
                                        e_termino_ltip,

                                    "Somatório LTIP gozada em anos":
                                        e_somatorio_anos,

                                    "Somatório LTIP gozada em anos/meses/dias":
                                        e_somatorio_amd,

                                    "Somatório de todas LTIP gozadas em dias":
                                        e_somatorio_dias,

                                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.":
                                        e_total_ltip,

                                    "Ato":
                                        e_ato,

                                    "Doc. Publicação":
                                        e_doc_publicacao,

                                    "SP da Adição":
                                        e_sp_adicao,

                                    "Processo RR":
                                        e_processo_rr,

                                    "Suplemento de Pessoal nº/Ano":
                                        e_suplemento,

                                    "Data Suplemento de Pessoal":
                                        e_data_suplemento,

                                    "Hoje":
                                        e_hoje,

                                    "OBS":
                                        e_obs,
                                }


                                linha_atualizada = [
                                    str(
                                        dados_editados.get(
                                            coluna,
                                            ""
                                        )
                                    )
                                    for coluna in headers
                                ]


                                sheet.update(
                                    f"A{cell.row}",
                                    [
                                        linha_atualizada
                                    ],
                                    value_input_option="USER_ENTERED"
                                )


                            st.success(
                                f"✅ Registro da matrícula "
                                f"**{matricula_editar}** "
                                f"atualizado com sucesso!"
                            )

                            st.cache_data.clear()

                            st.rerun()


                        except Exception as erro_edicao:

                            st.error(
                                "❌ Erro ao atualizar o registro."
                            )

                            st.exception(
                                erro_edicao
                            )

        else:

            st.info(
                "As colunas 'Matrícula' e 'Nome' "
                "são necessárias."
            )


    # ========================================================
    # 3. EXCLUSÃO
    # ========================================================
    with st.expander(
        "🗑️ **Excluir Registro da Planilha**",
        expanded=False
    ):

        st.warning(
            "⚠️ A exclusão removerá permanentemente "
            "o registro do Google Sheets."
        )


        if (
            "Matrícula" in df.columns
            and "Nome" in df.columns
        ):

            opcoes_militares = df.apply(
                lambda r:
                f"{r['Matrícula']} - {r['Nome']}",
                axis=1
            ).tolist()


            militar_selecionado = st.selectbox(
                "Selecione o militar que deseja excluir:",
                [""] + opcoes_militares,
                key="seletor_militar_exclusao"
            )


            if militar_selecionado:

                matricula_alvo = (
                    militar_selecionado
                    .split(" - ")[0]
                    .strip()
                )


                registro_alvo = df[
                    df["Matrícula"].astype(str)
                    .str.strip()
                    == matricula_alvo
                ]


                st.write(
                    "**Dados do registro selecionado:**"
                )


                st.dataframe(
                    registro_alvo,
                    use_container_width=True
                )


                confirmar = st.checkbox(
                    "Confirmo que desejo excluir "
                    "permanentemente este registro.",
                    key="confirmar_exclusao"
                )


                btn_excluir = st.button(
                    "🔴 EXCLUIR REGISTRO",
                    type="primary",
                    disabled=not confirmar,
                    use_container_width=True,
                    key="btn_excluir"
                )


                if btn_excluir:

                    try:

                        with st.spinner(
                            "🗑️ Excluindo registro..."
                        ):

                            _, sheet = get_sheet(
                                SHEET_ID
                            )


                            cell = sheet.find(
                                matricula_alvo
                            )


                            if not cell:

                                st.error(
                                    "❌ Matrícula não localizada."
                                )

                                st.stop()


                            sheet.delete_rows(
                                cell.row
                            )


                        st.success(
                            f"✅ Registro da matrícula "
                            f"**{matricula_alvo}** "
                            f"excluído com sucesso!"
                        )

                        st.cache_data.clear()

                        st.rerun()


                    except Exception as erro_exclusao:

                        st.error(
                            "❌ Erro ao excluir registro."
                        )

                        st.exception(
                            erro_exclusao
                        )

        else:

            st.info(
                "As colunas 'Matrícula' e 'Nome' "
                "são necessárias."
            )


# ============================================================
# ERROS GERAIS
# ============================================================
except KeyError as erro:

    st.error(
        f"❌ Chave não encontrada no secrets.toml: {erro}"
    )

except Exception as erro:

    st.error(
        "❌ Ocorreu um erro geral na aplicação."
    )

    st.exception(erro)
