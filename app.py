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

@st.cache_resource
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


# ============================================================
# ABRIR PLANILHA
# ============================================================

def get_sheet():

    sheet_id = st.secrets[
        "SHEET_ID"
    ]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(
        sheet_id
    )

    worksheet = spreadsheet.sheet1

    return worksheet


# ============================================================
# LIMPAR NOME DOS CABEÇALHOS
# ============================================================

def limpar_header(valor):

    if valor is None:
        return ""

    return str(valor).strip()


# ============================================================
# LER PLANILHA DIRETAMENTE
# ============================================================

@st.cache_data(ttl=3)
def carregar_planilha():

    sheet_id = st.secrets[
        "SHEET_ID"
    ]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(
        sheet_id
    )

    worksheet = spreadsheet.sheet1

    valores = worksheet.get_all_values()

    if not valores:
        return pd.DataFrame()

    headers = [
        limpar_header(x)
        for x in valores[0]
    ]

    linhas = valores[1:]

    # Garante que todas as linhas tenham
    # exatamente o mesmo número de colunas
    quantidade_colunas = len(headers)

    linhas_corrigidas = []

    for linha in linhas:

        linha = list(linha)

        if len(linha) < quantidade_colunas:

            linha += [
                ""
            ] * (
                quantidade_colunas
                - len(linha)
            )

        elif len(linha) > quantidade_colunas:

            linha = linha[
                :quantidade_colunas
            ]

        linhas_corrigidas.append(
            linha
        )

    df = pd.DataFrame(
        linhas_corrigidas,
        columns=headers
    )

    return df


# ============================================================
# FUNÇÃO AUXILIAR
# ============================================================

def campo(dados, nome):

    valor = dados.get(
        nome,
        ""
    )

    if valor is None:
        return ""

    try:

        if pd.isna(valor):
            return ""

    except:
        pass

    return str(valor)


# ============================================================
# CABEÇALHO
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
    "🔄 Atualizar dados"
):

    carregar_planilha.clear()

    st.rerun()


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
    <h1 style='text-align:center;'>
    DGP - Dados dos Militares
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# CARREGA DADOS
# ============================================================

try:

    SHEET_ID = st.secrets[
        "SHEET_ID"
    ]

    df = carregar_planilha()

    # ========================================================
    # VISUALIZAÇÃO
    # ========================================================

    st.subheader(
        "📋 Visualização dos Registros"
    )

    st.dataframe(
        df,
        use_container_width=True,
        height=500
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
            "**💾 SALVAR NOVO CADASTRO**."
        )

        # ----------------------------------------------------
        # FORMULÁRIO
        # ----------------------------------------------------

        with st.form(
            "form_novo_cadastro",
            clear_on_submit=False
        ):

            # =================================================
            # ABA 1
            # =================================================

            (
                tab_pessoal,
                tab_lotacao,
                tab_cessao,
                tab_ltip,
                tab_outros
            ) = st.tabs(
                [
                    "👤 Identificação & Pessoal",
                    "🏢 Lotação & Promoção",
                    "🔄 Cessão & Movimentação",
                    "⏳ LTIP & Afastamentos",
                    "📝 Documentos & Observações",
                ]
            )

            # =================================================
            # PESSOAL
            # =================================================

            with tab_pessoal:

                c1, c2, c3 = st.columns(3)

                with c1:

                    novo_num_funcional = st.text_input(
                        "nº Funcional",
                        key="cad_num_funcional"
                    )

                    novo_matricula = st.text_input(
                        "Matrícula *",
                        key="cad_matricula"
                    )

                    novo_cpf_ponto = st.text_input(
                        "CPF.",
                        key="cad_cpf_ponto"
                    )

                    novo_cpf = st.text_input(
                        "CPF",
                        key="cad_cpf"
                    )

                    novo_num_ident = st.text_input(
                        "Nº IDENT.",
                        key="cad_num_ident"
                    )

                with c2:

                    novo_nome = st.text_input(
                        "Nome *",
                        key="cad_nome"
                    )

                    novo_nome_guerra = st.text_input(
                        "Nome de Guerra",
                        key="cad_nome_guerra"
                    )

                    novo_sexo = st.selectbox(
                        "SEXO",
                        [
                            "",
                            "MASCULINO",
                            "FEMININO"
                        ],
                        key="cad_sexo"
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
                        key="cad_raca"
                    )

                with c3:

                    novo_posto_grad = st.text_input(
                        "Posto/ Grad",
                        key="cad_posto_grad"
                    )

                    novo_fones = st.text_input(
                        "Fones",
                        key="cad_fones"
                    )

                    novo_ano_ingresso = st.text_input(
                        "Ano de ingresso",
                        key="cad_ano_ingresso"
                    )

                    novo_data_praca = st.text_input(
                        "Data de praça",
                        key="cad_data_praca"
                    )


            # =================================================
            # LOTAÇÃO
            # =================================================

            with tab_lotacao:

                c1, c2, c3 = st.columns(3)

                with c1:

                    novo_ome = st.text_input(
                        "OME",
                        key="cad_ome"
                    )

                    novo_ome_qod = st.text_input(
                        "OME QOD",
                        key="cad_ome_qod"
                    )

                    novo_atividade = st.text_input(
                        "Atividade",
                        key="cad_atividade"
                    )

                    novo_municipio = st.text_input(
                        "Município",
                        key="cad_municipio"
                    )

                    novo_regiao = st.text_input(
                        "Região",
                        key="cad_regiao"
                    )

                with c2:

                    novo_tempo_servico_anos = st.text_input(
                        "Tempo de serviço (anos)",
                        key="cad_tempo_anos"
                    )

                    novo_tempo_servico_amd = st.text_input(
                        "Tempo de serviço (ano, mês, dias)",
                        key="cad_tempo_amd"
                    )

                    novo_tempo_servico_dias = st.text_input(
                        "Tempo de serviço (dias)",
                        key="cad_tempo_dias"
                    )

                    novo_tempo_obm_atual = st.text_input(
                        "Tempo na OBM atual",
                        key="cad_tempo_obm"
                    )

                with c3:

                    novo_data_ult_promocao = st.text_input(
                        "Data da última promoção ou Implant. PCNH",
                        key="cad_data_promocao"
                    )

                    novo_principio_ult_promocao = st.text_input(
                        "Princípio da última promoção",
                        key="cad_principio_promocao"
                    )

                    novo_tempo_posto_atual_dias = st.text_input(
                        "Tempo no Posto/Grad. atual EM DIAS",
                        key="cad_tempo_posto"
                    )


            # =================================================
            # CESSÃO
            # =================================================

            with tab_cessao:

                c1, c2, c3 = st.columns(3)

                with c1:

                    novo_data_mov_sp = st.text_input(
                        "Data da Movimentação em SP",
                        key="cad_data_mov_sp"
                    )

                    novo_ome_anterior = st.text_input(
                        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO",
                        key="cad_ome_anterior"
                    )

                    novo_data_chegada = st.text_input(
                        "Data de chegada na OBM Anteior",
                        key="cad_data_chegada"
                    )

                    novo_movimentado = st.text_input(
                        "Movimentado",
                        key="cad_movimentado"
                    )

                with c2:

                    novo_orgao = st.text_input(
                        "ÓRGÃO",
                        key="cad_orgao"
                    )

                    novo_poder = st.text_input(
                        "Poder",
                        key="cad_poder"
                    )

                    novo_onus = st.selectbox(
                        "Ônus para Origem",
                        [
                            "",
                            "SIM",
                            "NÃO"
                        ],
                        key="cad_onus"
                    )

                    novo_inicio_cessao = st.text_input(
                        "Início da Cessão ou requisição",
                        key="cad_inicio_cessao"
                    )

                with c3:

                    novo_renovacao = st.text_input(
                        "Renovação de cessão - Atos/Portarias/Documentos",
                        key="cad_renovacao"
                    )

                    novo_doe = st.text_input(
                        "DOE/BGSDS de renovação",
                        key="cad_doe"
                    )

                    novo_sei = st.text_input(
                        "SEI deslig.",
                        key="cad_sei"
                    )


            # =================================================
            # LTIP
            # =================================================

            with tab_ltip:

                c1, c2 = st.columns(2)

                with c1:

                    novo_afastamentos = st.text_area(
                        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP",
                        key="cad_afastamentos"
                    )

                    novo_inicio_ltip = st.text_input(
                        "INÍCIO DA LTIP",
                        key="cad_inicio_ltip"
                    )

                    novo_termino_ltip = st.text_input(
                        "TÉRMINO DA LTIP",
                        key="cad_termino_ltip"
                    )

                with c2:

                    novo_somatorio_anos = st.text_input(
                        "Somatório LTIP gozada em anos",
                        key="cad_somatorio_anos"
                    )

                    novo_somatorio_amd = st.text_input(
                        "Somatório LTIP gozada em anos/meses/dias",
                        key="cad_somatorio_amd"
                    )

                    novo_somatorio_dias = st.text_input(
                        "Somatório de todas LTIP gozadas em dias",
                        key="cad_somatorio_dias"
                    )

                    novo_total_ltip = st.text_input(
                        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.",
                        key="cad_total_ltip"
                    )


            # =================================================
            # OUTROS
            # =================================================

            with tab_outros:

                c1, c2 = st.columns(2)

                with c1:

                    novo_ato = st.text_input(
                        "Ato",
                        key="cad_ato"
                    )

                    novo_doc_publicacao = st.text_input(
                        "Doc. Publicação",
                        key="cad_doc_publicacao"
                    )

                    novo_sp_adicao = st.text_input(
                        "SP da Adição",
                        key="cad_sp_adicao"
                    )

                    novo_processo_rr = st.text_input(
                        "Processo RR",
                        key="cad_processo_rr"
                    )

                with c2:

                    novo_suplemento = st.text_input(
                        "Suplemento de Pessoal nº/Ano",
                        key="cad_suplemento"
                    )

                    novo_data_suplemento = st.text_input(
                        "Data Suplemento de Pessoal",
                        key="cad_data_suplemento"
                    )

                    novo_hoje = st.text_input(
                        "Hoje",
                        key="cad_hoje"
                    )

                    novo_obs = st.text_area(
                        "OBS",
                        key="cad_obs"
                    )


            # =================================================
            # BOTÃO
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

            matricula = (
                novo_matricula
                .strip()
            )

            nome = (
                novo_nome
                .strip()
            )

            if not matricula:

                st.error(
                    "❌ A matrícula é obrigatória."
                )

            elif not nome:

                st.error(
                    "❌ O nome é obrigatório."
                )

            else:

                try:

                    # -----------------------------------------
                    # CONECTA
                    # -----------------------------------------

                    sheet = get_sheet()

                    st.info(
                        "🔄 Conectado ao Google Sheets."
                    )

                    # -----------------------------------------
                    # CABEÇALHOS REAIS
                    # -----------------------------------------

                    headers = [
                        limpar_header(x)
                        for x in sheet.row_values(1)
                    ]

                    if not headers:

                        st.error(
                            "❌ A planilha não possui "
                            "cabeçalhos na linha 1."
                        )

                        st.stop()


                    # -----------------------------------------
                    # LOCALIZA MATRÍCULA
                    # -----------------------------------------

                    if "Matrícula" not in headers:

                        st.error(
                            "❌ A coluna 'Matrícula' não "
                            "existe na linha 1 da planilha."
                        )

                        st.write(
                            "Cabeçalhos encontrados:"
                        )

                        st.write(headers)

                        st.stop()


                    indice_matricula = (
                        headers.index(
                            "Matrícula"
                        )
                    )

                    coluna_matricula = (
                        indice_matricula + 1
                    )


                    # -----------------------------------------
                    # VERIFICA DUPLICIDADE
                    # -----------------------------------------

                    valores = sheet.col_values(
                        coluna_matricula
                    )

                    existe = False

                    for valor in valores[1:]:

                        if (
                            str(valor).strip()
                            == matricula
                        ):

                            existe = True
                            break


                    if existe:

                        st.error(
                            f"❌ A matrícula "
                            f"**{matricula}** "
                            "já existe na planilha."
                        )

                    else:

                        # -------------------------------------
                        # MONTA DADOS
                        # -------------------------------------

                        dados_novo = {

                            "nº Funcional":
                                novo_num_funcional,

                            "Matrícula":
                                matricula,

                            "CPF.":
                                novo_cpf_ponto,

                            "CPF":
                                novo_cpf,

                            "Nº IDENT.":
                                novo_num_ident,

                            "Nome":
                                nome,

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


                        # -------------------------------------
                        # CRIA LINHA EXATAMENTE NA ORDEM
                        # DA PLANILHA
                        # -------------------------------------

                        nova_linha = []

                        for header in headers:

                            valor = dados_novo.get(
                                header,
                                ""
                            )

                            if valor is None:
                                valor = ""

                            nova_linha.append(
                                str(valor)
                            )


                        # -------------------------------------
                        # MOSTRA O QUE SERÁ GRAVADO
                        # -------------------------------------

                        st.write(
                            "📝 Preparando novo cadastro..."
                        )

                        st.write(
                            f"Matrícula: **{matricula}**"
                        )

                        st.write(
                            f"Nome: **{nome}**"
                        )

                        st.write(
                            f"Quantidade de colunas: "
                            f"**{len(nova_linha)}**"
                        )


                        # -------------------------------------
                        # LOCALIZA PRÓXIMA LINHA
                        # -------------------------------------

                        todas_linhas = (
                            sheet.get_all_values()
                        )

                        proxima_linha = (
                            len(todas_linhas) + 1
                        )


                        # -------------------------------------
                        # GRAVA DIRETAMENTE
                        # -------------------------------------

                        st.info(
                            "💾 Gravando diretamente "
                            "na planilha..."
                        )

                        intervalo = (
                            f"A{proxima_linha}:"
                            f"{gspread.utils.rowcol_to_a1("
                            proxima_linha,
                            len(nova_linha)
                            )}"
                        )

                        # Corrige o intervalo para
                        # ficar no formato A55:AX55
                        ultima_coluna = (
                            gspread.utils.rowcol_to_a1(
                                1,
                                len(nova_linha)
                            ).replace(
                                "1",
                                ""
                            )
                        )

                        intervalo = (
                            f"A{proxima_linha}:"
                            f"{ultima_coluna}"
                            f"{proxima_linha}"
                        )


                        sheet.update(
                            intervalo,
                            [
                                nova_linha
                            ],
                            value_input_option="USER_ENTERED"
                        )


                        # -------------------------------------
                        # VERIFICAÇÃO REAL
                        # -------------------------------------

                        time.sleep(1)

                        linha_verificada = (
                            sheet.row_values(
                                proxima_linha
                            )
                        )


                        # Completa se necessário
                        if len(
                            linha_verificada
                        ) < len(headers):

                            linha_verificada += [
                                ""
                            ] * (
                                len(headers)
                                - len(
                                    linha_verificada
                                )
                            )


                        matricula_gravada = (
                            str(
                                linha_verificada[
                                    indice_matricula
                                ]
                            ).strip()
                            if indice_matricula
                            < len(linha_verificada)
                            else ""
                        )


                        # -------------------------------------
                        # CONFIRMAÇÃO
                        # -------------------------------------

                        if (
                            matricula_gravada
                            == matricula
                        ):

                            st.success(
                                "🎉 CADASTRO GRAVADO "
                                "COM SUCESSO!"
                            )

                            st.success(
                                f"👤 Nome: **{nome}**"
                            )

                            st.success(
                                f"🪪 Matrícula: "
                                f"**{matricula}**"
                            )

                            st.info(
                                f"📍 Linha gravada: "
                                f"**{proxima_linha}**"
                            )

                            # ---------------------------------
                            # ATUALIZA DATAFRAME
                            # ---------------------------------

                            carregar_planilha.clear()

                            df = (
                                carregar_planilha()
                            )

                            st.subheader(
                                "✅ Cadastro confirmado "
                                "na planilha"
                            )

                            st.dataframe(
                                df.tail(5),
                                use_container_width=True
                            )

                        else:

                            st.error(
                                "⚠️ A gravação foi enviada, "
                                "mas a verificação não "
                                "encontrou a matrícula "
                                "na linha esperada."
                            )

                            st.write(
                                "Matrícula esperada:",
                                matricula
                            )

                            st.write(
                                "Matrícula encontrada:",
                                matricula_gravada
                            )

                            st.write(
                                "Linha verificada:",
                                linha_verificada
                            )


                except Exception as erro:

                    st.error(
                        "❌ ERRO AO GRAVAR NO "
                        "GOOGLE SHEETS"
                    )

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

            opcoes = []

            for _, linha in df.iterrows():

                matricula = str(
                    linha.get(
                        "Matrícula",
                        ""
                    )
                ).strip()

                nome = str(
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
                key="editar_selecao"
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


                if not registros.empty:

                    dados = (
                        registros.iloc[0]
                        .to_dict()
                    )

                    st.info(
                        f"Editando: "
                        f"**{dados.get('Nome', '')}**"
                    )


                    # ========================================
                    # EDIÇÃO SIMPLIFICADA
                    # ========================================

                    with st.form(
                        "form_edicao"
                    ):

                        campos_edicao = {}

                        colunas_editaveis = (
                            list(df.columns)
                        )

                        for coluna in colunas_editaveis:

                            valor_atual = campo(
                                dados,
                                coluna
                            )

                            if coluna == "Matrícula":

                                st.text_input(
                                    coluna,
                                    value=valor_atual,
                                    disabled=True
                                )

                                campos_edicao[
                                    coluna
                                ] = valor_atual

                            elif coluna == "OBS":

                                campos_edicao[
                                    coluna
                                ] = st.text_area(
                                    coluna,
                                    value=valor_atual
                                )

                            else:

                                campos_edicao[
                                    coluna
                                ] = st.text_input(
                                    coluna,
                                    value=valor_atual
                                )


                        atualizar = (
                            st.form_submit_button(
                                "💾 SALVAR ALTERAÇÕES",
                                type="primary",
                                use_container_width=True
                            )
                        )


                    if atualizar:

                        try:

                            sheet = get_sheet()

                            headers = [
                                limpar_header(x)
                                for x
                                in sheet.row_values(1)
                            ]

                            if (
                                "Matrícula"
                                not in headers
                            ):

                                st.error(
                                    "Coluna Matrícula "
                                    "não encontrada."
                                )

                                st.stop()


                            indice = (
                                headers.index(
                                    "Matrícula"
                                )
                            )


                            todas = (
                                sheet.get_all_values()
                            )


                            linha_encontrada = None


                            for numero, linha in enumerate(
                                todas[1:],
                                start=2
                            ):

                                if len(linha) <= indice:
                                    continue

                                if (
                                    str(
                                        linha[indice]
                                    ).strip()
                                    == matricula_editar
                                ):

                                    linha_encontrada = (
                                        numero
                                    )

                                    break


                            if (
                                linha_encontrada
                                is None
                            ):

                                st.error(
                                    "Registro não encontrado."
                                )

                            else:

                                linha_nova = []

                                for header in headers:

                                    valor = (
                                        campos_edicao
                                        .get(
                                            header,
                                            ""
                                        )
                                    )

                                    linha_nova.append(
                                        str(
                                            valor
                                            if valor
                                            is not None
                                            else ""
                                        )
                                    )


                                ultima_coluna = (
                                    gspread.utils.rowcol_to_a1(
                                        1,
                                        len(linha_nova)
                                    ).replace(
                                        "1",
                                        ""
                                    )
                                )


                                intervalo = (
                                    f"A{linha_encontrada}:"
                                    f"{ultima_coluna}"
                                    f"{linha_encontrada}"
                                )


                                sheet.update(
                                    intervalo,
                                    [linha_nova],
                                    value_input_option="USER_ENTERED"
                                )


                                time.sleep(1)


                                verificacao = (
                                    sheet.row_values(
                                        linha_encontrada
                                    )
                                )


                                if (
                                    len(verificacao)
                                    > indice
                                    and
                                    str(
                                        verificacao[
                                            indice
                                        ]
                                    ).strip()
                                    ==
                                    matricula_editar
                                ):

                                    st.success(
                                        "✅ Registro atualizado "
                                        "com sucesso!"
                                    )

                                    carregar_planilha.clear()

                                    time.sleep(1)

                                    st.rerun()

                                else:

                                    st.error(
                                        "❌ A atualização "
                                        "não pôde ser "
                                        "confirmada."
                                    )


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
            "Matrícula" in df.columns
            and "Nome" in df.columns
        ):

            opcoes_exclusao = []

            for _, linha in df.iterrows():

                matricula = str(
                    linha.get(
                        "Matrícula",
                        ""
                    )
                ).strip()

                nome = str(
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
                    key="exclusao_selecao"
                )
            )


            if selecionado_exclusao:

                matricula_excluir = (
                    selecionado_exclusao
                    .split(" - ", 1)[0]
                    .strip()
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
                    key="botao_excluir"
                ):

                    try:

                        sheet = get_sheet()

                        headers = [
                            limpar_header(x)
                            for x
                            in sheet.row_values(1)
                        ]

                        indice = (
                            headers.index(
                                "Matrícula"
                            )
                        )


                        todas = (
                            sheet.get_all_values()
                        )


                        linha_excluir = None


                        for numero, linha in enumerate(
                            todas[1:],
                            start=2
                        ):

                            if len(linha) <= indice:
                                continue

                            if (
                                str(
                                    linha[indice]
                                ).strip()
                                ==
                                matricula_excluir
                            ):

                                linha_excluir = (
                                    numero
                                )

                                break


                        if (
                            linha_excluir
                            is not None
                        ):

                            sheet.delete_rows(
                                linha_excluir
                            )

                            st.success(
                                "✅ Registro excluído "
                                "com sucesso."
                            )

                            carregar_planilha.clear()

                            time.sleep(1)

                            st.rerun()

                        else:

                            st.error(
                                "❌ Registro não encontrado."
                            )


                    except Exception as erro:

                        st.error(
                            "❌ Erro ao excluir:"
                        )

                        st.exception(
                            erro
                        )


except KeyError as erro:

    st.error(
        "❌ Erro no secrets.toml:"
    )

    st.exception(erro)


except Exception as erro:

    st.error(
        "❌ Erro geral da aplicação:"
    )

    st.exception(erro)
