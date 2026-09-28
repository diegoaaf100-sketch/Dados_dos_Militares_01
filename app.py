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
# CONEXÃO GOOGLE SHEETS
# ============================================================
def get_gspread_client():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


# ============================================================
# ABRIR PLANILHA
# ============================================================
def get_sheet():

    sheet_id = st.secrets["SHEET_ID"]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(sheet_id)

    worksheet = spreadsheet.sheet1

    return spreadsheet, worksheet


# ============================================================
# LER PLANILHA
# ============================================================
def read_sheet_dataframe():

    spreadsheet, worksheet = get_sheet()

    values = worksheet.get_all_values()

    if not values:

        return pd.DataFrame(), spreadsheet, worksheet

    headers = values[0]

    rows = values[1:]

    quantidade_colunas = len(headers)

    dados_corrigidos = []

    for row in rows:

        row_corrigida = list(row)

        if len(row_corrigida) < quantidade_colunas:

            row_corrigida.extend(
                [""] *
                (quantidade_colunas - len(row_corrigida))
            )

        elif len(row_corrigida) > quantidade_colunas:

            row_corrigida = row_corrigida[:quantidade_colunas]

        dados_corrigidos.append(row_corrigida)

    df = pd.DataFrame(
        dados_corrigidos,
        columns=headers
    )

    return df, spreadsheet, worksheet


# ============================================================
# CACHE DE LEITURA
# ============================================================
@st.cache_data(ttl=5)
def load_data(sheet_id):

    client = get_gspread_client()

    spreadsheet = client.open_by_key(sheet_id)

    worksheet = spreadsheet.sheet1

    values = worksheet.get_all_values()

    if not values:
        return pd.DataFrame()

    headers = values[0]

    rows = values[1:]

    quantidade_colunas = len(headers)

    dados_corrigidos = []

    for row in rows:

        row = list(row)

        if len(row) < quantidade_colunas:

            row.extend(
                [""] *
                (quantidade_colunas - len(row))
            )

        elif len(row) > quantidade_colunas:

            row = row[:quantidade_colunas]

        dados_corrigidos.append(row)

    df = pd.DataFrame(
        dados_corrigidos,
        columns=headers
    )

    return df


# ============================================================
# FUNÇÃO AUXILIAR
# ============================================================
def texto(valor):

    if valor is None:
        return ""

    if pd.isna(valor):
        return ""

    valor = str(valor)

    if valor == "-":
        return ""

    return valor.strip()


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
    "🔄 Atualizar Dashboard",
    use_container_width=True
):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================
col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

with col2:

    try:
        st.image(
            "images.png",
            width=140
        )
    except:
        pass

with col3:

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
# SHEET ID
# ============================================================
try:

    SHEET_ID = st.secrets["SHEET_ID"]

except Exception as erro:

    st.error(
        f"Erro ao encontrar SHEET_ID: {erro}"
    )

    st.stop()


# ============================================================
# CARREGAR DADOS
# ============================================================
try:

    df = load_data(SHEET_ID)

except Exception as erro:

    st.error(
        f"Erro ao carregar Google Sheets: {erro}"
    )

    st.stop()


# ============================================================
# VISUALIZAÇÃO
# ============================================================
st.subheader("📋 Visualização dos Registros")

if not df.empty:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "A planilha não possui registros."
    )


st.markdown("---")


# ============================================================
# NOVO CADASTRO
# ============================================================
with st.expander(
    "➕ NOVO CADASTRO DE MILITAR",
    expanded=False
):

    st.info(
        "Preencha os dados e clique em "
        "**💾 SALVAR NOVO CADASTRO**."
    )

    # ========================================================
    # FORMULÁRIO
    # ========================================================
    with st.form(
        "form_novo_cadastro",
        clear_on_submit=False
    ):

        # ====================================================
        # ABA 1
        # ====================================================
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "👤 Identificação & Pessoal",
                "🏢 Lotação & Promoção",
                "🔄 Cessão & Movimentação",
                "⏳ LTIP & Afastamentos",
                "📝 Documentos & Observações"
            ]
        )

        # ====================================================
        # PESSOAL
        # ====================================================
        with tab1:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_num_funcional = st.text_input(
                    "nº Funcional:"
                )

                novo_matricula = st.text_input(
                    "Matrícula:"
                )

                novo_cpf_ponto = st.text_input(
                    "CPF.:"
                )

                novo_cpf = st.text_input(
                    "CPF:"
                )

                novo_num_ident = st.text_input(
                    "Nº IDENT.:"
                )

            with c2:

                novo_nome = st.text_input(
                    "Nome:"
                )

                novo_nome_guerra = st.text_input(
                    "Nome de Guerra:"
                )

                novo_sexo = st.selectbox(
                    "SEXO:",
                    [
                        "",
                        "MASCULINO",
                        "FEMININO"
                    ]
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
                    ]
                )

            with c3:

                novo_posto_grad = st.text_input(
                    "Posto/ Grad:"
                )

                novo_fones = st.text_input(
                    "Fones:"
                )

                novo_ano_ingresso = st.text_input(
                    "Ano de ingresso:"
                )

                novo_data_praca = st.text_input(
                    "Data de praça:"
                )

        # ====================================================
        # LOTAÇÃO
        # ====================================================
        with tab2:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_ome = st.text_input(
                    "OME:"
                )

                novo_ome_qod = st.text_input(
                    "OME QOD:"
                )

                novo_atividade = st.text_input(
                    "Atividade:"
                )

                novo_municipio = st.text_input(
                    "Município:"
                )

                novo_regiao = st.text_input(
                    "Região:"
                )

            with c2:

                novo_tempo_servico_anos = st.text_input(
                    "Tempo de serviço (anos):"
                )

                novo_tempo_servico_amd = st.text_input(
                    "Tempo de serviço (ano, mês, dias):"
                )

                novo_tempo_servico_dias = st.text_input(
                    "Tempo de serviço (dias):"
                )

                novo_tempo_obm_atual = st.text_input(
                    "Tempo na OBM atual:"
                )

            with c3:

                novo_data_ult_promocao = st.text_input(
                    "Data da última promoção ou Implant. PCNH:"
                )

                novo_principio_ult_promocao = st.text_input(
                    "Princípio da última promoção:"
                )

                novo_tempo_posto_atual_dias = st.text_input(
                    "Tempo no Posto/Grad. atual EM DIAS:"
                )

        # ====================================================
        # CESSÃO
        # ====================================================
        with tab3:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_data_mov_sp = st.text_input(
                    "Data da Movimentação em SP:"
                )

                novo_ome_anterior = st.text_input(
                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:"
                )

                novo_data_chegada = st.text_input(
                    "Data de chegada na OBM Anteior:"
                )

                novo_movimentado = st.text_input(
                    "Movimentado (apagar antes de atualizar o SP):"
                )

            with c2:

                novo_orgao = st.text_input(
                    "ÓRGÃO:"
                )

                novo_poder = st.text_input(
                    "Poder:"
                )

                novo_onus = st.selectbox(
                    "Ônus para Origem:",
                    [
                        "",
                        "SIM",
                        "NÃO"
                    ]
                )

                novo_inicio_cessao = st.text_input(
                    "Início da Cessão ou requisição:"
                )

            with c3:

                novo_renovacao = st.text_input(
                    "Renovação de cessão - Atos/Portarias/Documentos:"
                )

                novo_doe = st.text_input(
                    "DOE/BGSDS de renovação:"
                )

                novo_sei = st.text_input(
                    "SEI deslig.:"
                )

        # ====================================================
        # LTIP
        # ====================================================
        with tab4:

            c1, c2 = st.columns(2)

            with c1:

                novo_afastamentos = st.text_area(
                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
                    "ININTERRUPTOS, PUBLICADOS EM SP:"
                )

                novo_inicio_ltip = st.text_input(
                    "INÍCIO DA LTIP:"
                )

                novo_termino_ltip = st.text_input(
                    "TÉRMINO DA LTIP (inserir data de apresentação):"
                )

            with c2:

                novo_somatorio_anos = st.text_input(
                    "Somatório LTIP gozada em anos:"
                )

                novo_somatorio_amd = st.text_input(
                    "Somatório LTIP gozada em anos/meses/dias:"
                )

                novo_somatorio_dias = st.text_input(
                    "Somatório de todas LTIP gozadas em dias:"
                )

                novo_total_ltip = st.text_input(
                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:"
                )

        # ====================================================
        # OUTROS
        # ====================================================
        with tab5:

            c1, c2 = st.columns(2)

            with c1:

                novo_ato = st.text_input(
                    "Ato:"
                )

                novo_doc_publicacao = st.text_input(
                    "Doc. Publicação:"
                )

                novo_sp_adicao = st.text_input(
                    "SP da Adição:"
                )

                novo_processo_rr = st.text_input(
                    "Processo RR:"
                )

            with c2:

                novo_suplemento = st.text_input(
                    "Suplemento de Pessoal nº/Ano:"
                )

                novo_data_suplemento = st.text_input(
                    "Data Suplemento de Pessoal:"
                )

                novo_hoje = st.text_input(
                    "Hoje:"
                )

                novo_obs = st.text_area(
                    "OBS:"
                )

        # ====================================================
        # BOTÃO
        # ====================================================
        st.markdown("---")

        salvar = st.form_submit_button(
            "💾 SALVAR NOVO CADASTRO",
            type="primary",
            use_container_width=True
        )


    # ========================================================
    # PROCESSAMENTO DO NOVO CADASTRO
    # ========================================================
    if salvar:

        st.info(
            "⏳ Salvando diretamente no Google Sheets..."
        )

        try:

            # ==================================================
            # VALIDAÇÃO
            # ==================================================
            matricula = str(
                novo_matricula
            ).strip()

            nome = str(
                novo_nome
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


            # ==================================================
            # CONECTAR
            # ==================================================
            client = get_gspread_client()

            spreadsheet = client.open_by_key(
                SHEET_ID
            )

            sheet = spreadsheet.sheet1


            # ==================================================
            # LER CABEÇALHOS DIRETAMENTE DA PLANILHA
            # ==================================================
            headers = sheet.row_values(1)

            if not headers:

                st.error(
                    "❌ A planilha não possui cabeçalhos."
                )

                st.stop()


            # ==================================================
            # LIMPAR CABEÇALHOS
            # ==================================================
            headers_limpos = [
                str(h).strip()
                for h in headers
            ]


            # ==================================================
            # LOCALIZAR COLUNA MATRÍCULA
            # ==================================================
            coluna_matricula = None

            for i, header in enumerate(headers_limpos):

                if header.lower() == "matrícula":

                    coluna_matricula = i + 1

                    break


            if coluna_matricula is None:

                st.error(
                    "❌ Não encontrei a coluna "
                    "'Matrícula' na planilha."
                )

                st.write(
                    "Cabeçalhos encontrados:"
                )

                st.write(headers_limpos)

                st.stop()


            # ==================================================
            # VERIFICAR DUPLICIDADE
            # ==================================================
            valores = sheet.col_values(
                coluna_matricula
            )

            matriculas_existentes = []

            for valor in valores[1:]:

                valor = str(valor).strip()

                if valor:

                    matriculas_existentes.append(
                        valor
                    )


            if matricula in matriculas_existentes:

                st.error(
                    f"❌ A matrícula **{matricula}** "
                    "já existe na planilha."
                )

                st.stop()


            # ==================================================
            # DICIONÁRIO DOS NOVOS DADOS
            # ==================================================
            novos_dados = {

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
                    novo_obs
            }


            # ==================================================
            # MONTAR LINHA EXATAMENTE NA ORDEM DA PLANILHA
            # ==================================================
            nova_linha = []

            for header_original in headers:

                header = str(
                    header_original
                ).strip()

                valor = ""

                # Procura correspondência exata
                if header in novos_dados:

                    valor = novos_dados[header]

                else:

                    # Procura ignorando espaços
                    # e diferença de maiúsculas
                    for chave, valor_chave in novos_dados.items():

                        if (
                            str(chave).strip().lower()
                            ==
                            header.lower()
                        ):

                            valor = valor_chave

                            break


                if valor is None:

                    valor = ""


                nova_linha.append(
                    str(valor)
                )


            # ==================================================
            # VERIFICAÇÃO
            # ==================================================
            if len(nova_linha) != len(headers):

                st.error(
                    "❌ Erro interno: quantidade "
                    "de campos diferente."
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


            # ==================================================
            # GRAVAÇÃO
            # ==================================================
            sheet.append_row(
                nova_linha,
                value_input_option="USER_ENTERED"
            )


            # ==================================================
            # CONFIRMAÇÃO REAL
            # ==================================================
            time.sleep(1)

            # Lê novamente a planilha
            valores_depois = sheet.get_all_values()


            encontrou = False

            for linha in valores_depois[1:]:

                if (
                    len(linha) > coluna_matricula - 1
                    and
                    str(
                        linha[coluna_matricula - 1]
                    ).strip()
                    == matricula
                ):

                    encontrou = True

                    break


            if encontrou:

                st.success(
                    f"✅ CADASTRO SALVO COM SUCESSO!\n\n"
                    f"**Matrícula:** {matricula}\n\n"
                    f"**Nome:** {nome}"
                )

                st.balloons()

                # Limpa cache
                st.cache_data.clear()

                # Mostra o registro salvo
                st.subheader(
                    "✅ Registro gravado na planilha"
                )

                st.dataframe(
                    pd.DataFrame(
                        [nova_linha],
                        columns=headers
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.error(
                    "⚠️ O Google Sheets não confirmou "
                    "a gravação do registro."
                )

                st.warning(
                    "O cadastro não será considerado "
                    "salvo até que apareça na planilha."
                )


        except Exception as erro:

            st.error(
                "❌ ERRO AO SALVAR NO GOOGLE SHEETS"
            )

            st.exception(erro)


# ============================================================
# EDITAR REGISTRO
# ============================================================
with st.expander(
    "✏️ EDITAR REGISTRO EXISTENTE",
    expanded=False
):

    if (
        not df.empty
        and
        "Matrícula" in df.columns
        and
        "Nome" in df.columns
    ):

        opcoes = []

        for _, linha in df.iterrows():

            matricula = texto(
                linha["Matrícula"]
            )

            nome = texto(
                linha["Nome"]
            )

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


            registro = df[
                df["Matrícula"]
                .astype(str)
                .str.strip()
                ==
                matricula_editar
            ]


            if not registro.empty:

                dados = registro.iloc[0].to_dict()

                st.info(
                    f"Editando: **{dados.get('Nome', '')}**"
                )


                with st.form(
                    "form_edicao"
                ):

                    c1, c2, c3 = st.columns(3)


                    with c1:

                        ed_num_funcional = st.text_input(
                            "nº Funcional",
                            value=texto(
                                dados.get(
                                    "nº Funcional",
                                    ""
                                )
                            )
                        )

                        ed_matricula = st.text_input(
                            "Matrícula",
                            value=matricula_editar,
                            disabled=True
                        )

                        ed_cpf_ponto = st.text_input(
                            "CPF.",
                            value=texto(
                                dados.get(
                                    "CPF.",
                                    ""
                                )
                            )
                        )

                        ed_cpf = st.text_input(
                            "CPF",
                            value=texto(
                                dados.get(
                                    "CPF",
                                    ""
                                )
                            )
                        )

                        ed_num_ident = st.text_input(
                            "Nº IDENT.",
                            value=texto(
                                dados.get(
                                    "Nº IDENT.",
                                    ""
                                )
                            )
                        )


                    with c2:

                        ed_nome = st.text_input(
                            "Nome",
                            value=texto(
                                dados.get(
                                    "Nome",
                                    ""
                                )
                            )
                        )

                        ed_nome_guerra = st.text_input(
                            "Nome de Guerra",
                            value=texto(
                                dados.get(
                                    "Nome de Guerra",
                                    ""
                                )
                            )
                        )

                        opcoes_sexo = [
                            "",
                            "MASCULINO",
                            "FEMININO"
                        ]

                        sexo_atual = texto(
                            dados.get(
                                "SEXO",
                                ""
                            )
                        ).upper()

                        if sexo_atual not in opcoes_sexo:
                            sexo_atual = ""

                        ed_sexo = st.selectbox(
                            "SEXO",
                            opcoes_sexo,
                            index=opcoes_sexo.index(
                                sexo_atual
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

                        raca_atual = texto(
                            dados.get(
                                "Raça/Cor",
                                ""
                            )
                        ).upper()

                        if raca_atual not in opcoes_raca:
                            raca_atual = ""

                        ed_raca = st.selectbox(
                            "Raça/Cor",
                            opcoes_raca,
                            index=opcoes_raca.index(
                                raca_atual
                            )
                        )


                    with c3:

                        ed_posto = st.text_input(
                            "Posto/ Grad",
                            value=texto(
                                dados.get(
                                    "Posto/ Grad",
                                    ""
                                )
                            )
                        )

                        ed_fones = st.text_input(
                            "Fones",
                            value=texto(
                                dados.get(
                                    "Fones",
                                    ""
                                )
                            )
                        )

                        ed_ano = st.text_input(
                            "Ano de ingresso",
                            value=texto(
                                dados.get(
                                    "Ano de ingresso",
                                    ""
                                )
                            )
                        )

                        ed_data_praca = st.text_input(
                            "Data de praça",
                            value=texto(
                                dados.get(
                                    "Data de praça",
                                    ""
                                )
                            )
                        )


                    st.markdown("---")

                    # Campos adicionais
                    c1, c2, c3 = st.columns(3)

                    with c1:

                        ed_ome = st.text_input(
                            "OME",
                            value=texto(
                                dados.get(
                                    "OME",
                                    ""
                                )
                            )
                        )

                        ed_ome_qod = st.text_input(
                            "OME QOD",
                            value=texto(
                                dados.get(
                                    "OME QOD",
                                    ""
                                )
                            )
                        )

                        ed_atividade = st.text_input(
                            "Atividade",
                            value=texto(
                                dados.get(
                                    "Atividade",
                                    ""
                                )
                            )
                        )

                        ed_municipio = st.text_input(
                            "Município",
                            value=texto(
                                dados.get(
                                    "Município",
                                    ""
                                )
                            )
                        )

                    with c2:

                        ed_regiao = st.text_input(
                            "Região",
                            value=texto(
                                dados.get(
                                    "Região",
                                    ""
                                )
                            )
                        )

                        ed_tempo_anos = st.text_input(
                            "Tempo de serviço (anos)",
                            value=texto(
                                dados.get(
                                    "Tempo de serviço (anos)",
                                    ""
                                )
                            )
                        )

                        ed_tempo_dias = st.text_input(
                            "Tempo de serviço (dias)",
                            value=texto(
                                dados.get(
                                    "Tempo de serviço (dias)",
                                    ""
                                )
                            )
                        )

                    with c3:

                        ed_fones2 = st.text_input(
                            "Tempo na OBM atual",
                            value=texto(
                                dados.get(
                                    "Tempo na OBM atual",
                                    ""
                                )
                            )
                        )

                        ed_promocao = st.text_input(
                            "Data da última promoção ou Implant. PCNH",
                            value=texto(
                                dados.get(
                                    "Data da última promoção ou Implant. PCNH",
                                    ""
                                )
                            )
                        )

                        ed_principio = st.text_input(
                            "Princípio da última promoção",
                            value=texto(
                                dados.get(
                                    "Princípio da última promoção",
                                    ""
                                )
                            )
                        )


                    st.markdown("---")

                    ed_obs = st.text_area(
                        "OBS",
                        value=texto(
                            dados.get(
                                "OBS",
                                ""
                            )
                        )
                    )


                    atualizar = st.form_submit_button(
                        "🔄 ATUALIZAR REGISTRO",
                        type="primary",
                        use_container_width=True
                    )


                if atualizar:

                    try:

                        client = get_gspread_client()

                        spreadsheet = client.open_by_key(
                            SHEET_ID
                        )

                        sheet = spreadsheet.sheet1


                        headers = sheet.row_values(1)


                        # Localizar matrícula
                        coluna_matricula = None

                        for i, h in enumerate(headers):

                            if (
                                str(h).strip().lower()
                                == "matrícula"
                            ):

                                coluna_matricula = i + 1

                                break


                        if coluna_matricula is None:

                            st.error(
                                "Coluna Matrícula não encontrada."
                            )

                            st.stop()


                        valores = sheet.col_values(
                            coluna_matricula
                        )


                        linha_planilha = None

                        for numero, valor in enumerate(
                            valores,
                            start=1
                        ):

                            if (
                                str(valor).strip()
                                ==
                                matricula_editar
                            ):

                                linha_planilha = numero

                                break


                        if linha_planilha is None:

                            st.error(
                                "Registro não encontrado "
                                "diretamente na planilha."
                            )

                            st.stop()


                        # ==================================================
                        # IMPORTANTE:
                        # COMEÇAMOS COM A LINHA EXISTENTE.
                        # ISSO EVITA APAGAR CAMPOS QUE NÃO ESTÃO NO FORMULÁRIO.
                        # ==================================================
                        linha_existente = sheet.row_values(
                            linha_planilha
                        )


                        while len(linha_existente) < len(headers):

                            linha_existente.append("")


                        dados_edicao = {

                            "nº Funcional":
                                ed_num_funcional,

                            "Matrícula":
                                matricula_editar,

                            "CPF.":
                                ed_cpf_ponto,

                            "CPF":
                                ed_cpf,

                            "Nº IDENT.":
                                ed_num_ident,

                            "Nome":
                                ed_nome,

                            "Nome de Guerra":
                                ed_nome_guerra,

                            "SEXO":
                                ed_sexo,

                            "Raça/Cor":
                                ed_raca,

                            "Posto/ Grad":
                                ed_posto,

                            "Fones":
                                ed_fones,

                            "Ano de ingresso":
                                ed_ano,

                            "Data de praça":
                                ed_data_praca,

                            "OME":
                                ed_ome,

                            "OME QOD":
                                ed_ome_qod,

                            "Atividade":
                                ed_atividade,

                            "Município":
                                ed_municipio,

                            "Região":
                                ed_regiao,

                            "Tempo de serviço (anos)":
                                ed_tempo_anos,

                            "Tempo de serviço (dias)":
                                ed_tempo_dias,

                            "Tempo na OBM atual":
                                ed_fones2,

                            "Data da última promoção ou Implant. PCNH":
                                ed_promocao,

                            "Princípio da última promoção":
                                ed_principio,

                            "OBS":
                                ed_obs
                        }


                        # ==================================================
                        # ALTERAR SOMENTE OS CAMPOS EXISTENTES
                        # ==================================================
                        for i, header in enumerate(headers):

                            header = str(
                                header
                            ).strip()


                            for chave, valor in dados_edicao.items():

                                if (
                                    header.lower()
                                    ==
                                    chave.lower()
                                ):

                                    linha_existente[i] = (
                                        ""
                                        if valor is None
                                        else str(valor)
                                    )

                                    break


                        # ==================================================
                        # ATUALIZAR LINHA
                        # ==================================================
                        sheet.update(
                            f"A{linha_planilha}",
                            [linha_existente[:len(headers)]],
                            value_input_option="USER_ENTERED"
                        )


                        st.cache_data.clear()


                        st.success(
                            f"✅ Registro da matrícula "
                            f"**{matricula_editar}** "
                            "atualizado com sucesso!"
                        )


                        st.info(
                            "🔄 A atualização foi gravada "
                            "diretamente no Google Sheets."
                        )


                    except Exception as erro:

                        st.error(
                            "❌ Erro ao atualizar:"
                        )

                        st.exception(erro)


# ============================================================
# EXCLUSÃO
# ============================================================
with st.expander(
    "🗑️ EXCLUIR REGISTRO",
    expanded=False
):

    if (
        not df.empty
        and
        "Matrícula" in df.columns
        and
        "Nome" in df.columns
    ):

        opcoes_exclusao = []

        for _, linha in df.iterrows():

            matricula = texto(
                linha["Matrícula"]
            )

            nome = texto(
                linha["Nome"]
            )

            if matricula:

                opcoes_exclusao.append(
                    f"{matricula} - {nome}"
                )


        selecionado_exclusao = st.selectbox(
            "Selecione o militar:",
            [""] + opcoes_exclusao,
            key="exclusao_selecao"
        )


        if selecionado_exclusao:

            matricula_exclusao = (
                selecionado_exclusao
                .split(" - ", 1)[0]
                .strip()
            )


            confirmar = st.checkbox(
                "Confirmo que desejo excluir "
                "permanentemente este registro.",
                key="confirmacao_exclusao"
            )


            excluir = st.button(
                "🔴 EXCLUIR REGISTRO",
                type="primary",
                disabled=not confirmar,
                use_container_width=True
            )


            if excluir:

                try:

                    client = get_gspread_client()

                    spreadsheet = client.open_by_key(
                        SHEET_ID
                    )

                    sheet = spreadsheet.sheet1


                    headers = sheet.row_values(1)


                    coluna_matricula = None

                    for i, h in enumerate(headers):

                        if (
                            str(h).strip().lower()
                            == "matrícula"
                        ):

                            coluna_matricula = i + 1

                            break


                    if coluna_matricula is None:

                        st.error(
                            "Coluna Matrícula não encontrada."
                        )

                        st.stop()


                    valores = sheet.col_values(
                        coluna_matricula
                    )


                    linha_excluir = None

                    for numero, valor in enumerate(
                        valores,
                        start=1
                    ):

                        if (
                            str(valor).strip()
                            ==
                            matricula_exclusao
                        ):

                            linha_excluir = numero

                            break


                    if linha_excluir is None:

                        st.error(
                            "Registro não encontrado."
                        )

                    else:

                        sheet.delete_rows(
                            linha_excluir
                        )

                        st.cache_data.clear()

                        st.success(
                            f"✅ Matrícula "
                            f"**{matricula_exclusao}** "
                            "excluída com sucesso."
                        )


                except Exception as erro:

                    st.error(
                        "❌ Erro ao excluir:"
                    )

                    st.exception(erro)
