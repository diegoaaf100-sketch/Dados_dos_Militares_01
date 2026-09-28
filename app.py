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


def get_worksheet():

    SHEET_ID = st.secrets["SHEET_ID"]

    client = get_gspread_client()

    spreadsheet = client.open_by_key(SHEET_ID)

    worksheet = spreadsheet.worksheet(NOME_ABA)

    return client, spreadsheet, worksheet


# ============================================================
# CARREGAR DADOS
# ============================================================
@st.cache_data(ttl=5)
def load_data(sheet_id):

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv&gid="
    )

    # Descobre o gid diretamente pelo gspread
    client = get_gspread_client()

    spreadsheet = client.open_by_key(sheet_id)

    worksheet = spreadsheet.worksheet(NOME_ABA)

    gid = worksheet.id

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv&gid={gid}"
    )

    df = pd.read_csv(url, dtype=str)

    df.columns = [
        str(col).strip().replace(":", "-")
        for col in df.columns
    ]

    df = df.fillna("")

    return df


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

    load_data.clear()
    st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================
col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

with col2:

    try:
        st.image("images.png", width=140)
    except:
        pass

with col3:

    try:
        st.image("11679.png", width=140)
    except:
        pass


st.markdown(
    "<h1 style='text-align:center;'>DGP - Dados dos Militares</h1>",
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# DIAGNÓSTICO DA CONEXÃO
# ============================================================
with st.expander(
    "🔌 TESTE DE CONEXÃO COM GOOGLE SHEETS",
    expanded=True
):

    st.info(
        f"Planilha configurada através do SHEET_ID | "
        f"Aba configurada: **{NOME_ABA}**"
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:

        testar_conexao = st.button(
            "🔌 Testar Conexão",
            use_container_width=True,
            key="teste_conexao"
        )

    with col_b:

        testar_leitura = st.button(
            "📖 Testar Leitura",
            use_container_width=True,
            key="teste_leitura"
        )

    with col_c:

        testar_escrita = st.button(
            "✍️ Testar Escrita",
            use_container_width=True,
            key="teste_escrita"
        )


    # ========================================================
    # TESTAR CONEXÃO
    # ========================================================
    if testar_conexao:

        try:

            with st.spinner("Conectando ao Google Sheets..."):

                client, spreadsheet, worksheet = get_worksheet()

            st.success("✅ CONEXÃO REALIZADA COM SUCESSO!")

            st.write(
                f"**Planilha:** {spreadsheet.title}"
            )

            st.write(
                f"**Aba:** {worksheet.title}"
            )

            st.write(
                f"**ID da aba:** {worksheet.id}"
            )

        except Exception as erro:

            st.error("❌ FALHA NA CONEXÃO")

            st.exception(erro)


    # ========================================================
    # TESTAR LEITURA
    # ========================================================
    if testar_leitura:

        try:

            with st.spinner("Lendo Google Sheets..."):

                client, spreadsheet, worksheet = get_worksheet()

                valores = worksheet.get_all_values()

            st.success("✅ LEITURA FUNCIONANDO!")

            st.write(
                f"Planilha: **{spreadsheet.title}**"
            )

            st.write(
                f"Aba: **{worksheet.title}**"
            )

            st.write(
                f"Linhas encontradas: **{len(valores)}**"
            )

            if valores:

                st.write(
                    f"Colunas encontradas: **{len(valores[0])}**"
                )

                st.write(
                    "Cabeçalhos encontrados:"
                )

                st.code(
                    " | ".join(valores[0])
                )

            else:

                st.warning(
                    "A aba está vazia."
                )

        except Exception as erro:

            st.error("❌ ERRO NA LEITURA")

            st.exception(erro)


    # ========================================================
    # TESTAR ESCRITA
    # ========================================================
    if testar_escrita:

        try:

            with st.spinner(
                "Testando permissão de escrita..."
            ):

                client, spreadsheet, worksheet = get_worksheet()

                # Guarda quantidade atual de linhas
                quantidade_antes = len(
                    worksheet.get_all_values()
                )

                # Registro temporário
                teste = [
                    "TESTE_STREAMLIT",
                    "TESTE_CONEXAO",
                    "NÃO É CADASTRO REAL"
                ]

                worksheet.append_row(
                    teste,
                    value_input_option="RAW"
                )

                # Lê novamente
                valores_depois = worksheet.get_all_values()

                quantidade_depois = len(
                    valores_depois
                )

                # Remove a linha de teste
                if quantidade_depois > quantidade_antes:

                    worksheet.delete_rows(
                        quantidade_depois
                    )

            st.success(
                "✅ ESCRITA FUNCIONANDO!"
            )

            st.info(
                "O sistema conseguiu escrever e remover "
                "uma linha de teste na aba Página1."
            )

        except Exception as erro:

            st.error(
                "❌ A ESCRITA NO GOOGLE SHEETS FALHOU!"
            )

            st.exception(erro)

            st.warning(
                "Se a leitura funcionar e a escrita falhar, "
                "o problema provavelmente está na permissão "
                "de edição da conta de serviço."
            )


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================
try:

    SHEET_ID = st.secrets["SHEET_ID"]

    df = load_data(SHEET_ID)

except Exception as erro:

    st.error(
        "❌ Não foi possível carregar os dados."
    )

    st.exception(erro)

    st.stop()


# ============================================================
# VISUALIZAÇÃO
# ============================================================
st.subheader("📋 Visualização dos Registros")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

st.markdown("---")


# ============================================================
# LISTA COMPLETA DE CAMPOS
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
def valor_dado(dados, campo):

    if dados is None:
        return ""

    valor = dados.get(campo, "")

    if valor is None:
        return ""

    try:

        if pd.isna(valor):
            return ""

    except:
        pass

    return str(valor)


# ============================================================
# FORMULÁRIO
# ============================================================
def criar_formulario(dados=None, prefixo="novo"):

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

    campos_tab1 = [
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
    ]

    campos_tab2 = [
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
    ]

    campos_tab3 = [
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
    ]

    campos_tab4 = [
        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP",
        "INÍCIO DA LTIP",
        "TÉRMINO DA LTIP (inserir data de apresentação)",
        "Somatório LTIP gozada em anos",
        "Somatório LTIP gozada em anos/meses/dias",
        "Somatório de todas LTIP gozadas em dias",
        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.",
    ]

    campos_tab5 = [
        "Ato",
        "Doc. Publicação",
        "SP da Adição",
        "Processo RR",
        "Suplemento de Pessoal nº/Ano",
        "Data Suplemento de Pessoal",
        "Hoje",
        "OBS",
    ]


    # ========================================================
    # FUNÇÃO INTERNA DE CAMPO
    # ========================================================
    def criar_campo(campo):

        chave = f"{prefixo}_{campo}"

        valor = valor_dado(
            dados,
            campo
        )

        if campo == "SEXO":

            opcoes = [
                "",
                "MASCULINO",
                "FEMININO"
            ]

            valor_upper = valor.upper()

            indice = (
                opcoes.index(valor_upper)
                if valor_upper in opcoes
                else 0
            )

            resultado[campo] = st.selectbox(
                "SEXO:",
                opcoes,
                index=indice,
                key=chave
            )

        elif campo == "Raça/Cor":

            opcoes = [
                "",
                "BRANCA",
                "PRETA",
                "PARDA",
                "AMARELA",
                "INDÍGENA"
            ]

            valor_upper = valor.upper()

            indice = (
                opcoes.index(valor_upper)
                if valor_upper in opcoes
                else 0
            )

            resultado[campo] = st.selectbox(
                "Raça/Cor:",
                opcoes,
                index=indice,
                key=chave
            )

        elif campo == "Ônus para Origem":

            opcoes = [
                "",
                "SIM",
                "NÃO"
            ]

            valor_upper = valor.upper()

            indice = (
                opcoes.index(valor_upper)
                if valor_upper in opcoes
                else 0
            )

            resultado[campo] = st.selectbox(
                "Ônus para Origem:",
                opcoes,
                index=indice,
                key=chave
            )

        elif campo == "OBS":

            resultado[campo] = st.text_area(
                "OBS:",
                value=valor,
                key=chave
            )

        elif campo == (
            "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
            "ININTERRUPTOS, PUBLICADOS EM SP"
        ):

            resultado[campo] = st.text_area(
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP:",
                value=valor,
                key=chave
            )

        else:

            resultado[campo] = st.text_input(
                f"{campo}:",
                value=valor,
                key=chave
            )


    # ========================================================
    # ABA 1
    # ========================================================
    with tab1:

        col1, col2, col3 = st.columns(3)

        for i, campo in enumerate(campos_tab1):

            if i < 5:
                with col1:
                    criar_campo(campo)

            elif i < 9:
                with col2:
                    criar_campo(campo)

            else:
                with col3:
                    criar_campo(campo)


    # ========================================================
    # ABA 2
    # ========================================================
    with tab2:

        col1, col2, col3 = st.columns(3)

        for i, campo in enumerate(campos_tab2):

            if i < 5:
                with col1:
                    criar_campo(campo)

            elif i < 9:
                with col2:
                    criar_campo(campo)

            else:
                with col3:
                    criar_campo(campo)


    # ========================================================
    # ABA 3
    # ========================================================
    with tab3:

        col1, col2, col3 = st.columns(3)

        for i, campo in enumerate(campos_tab3):

            if i < 4:
                with col1:
                    criar_campo(campo)

            elif i < 8:
                with col2:
                    criar_campo(campo)

            else:
                with col3:
                    criar_campo(campo)


    # ========================================================
    # ABA 4
    # ========================================================
    with tab4:

        col1, col2 = st.columns(2)

        for i, campo in enumerate(campos_tab4):

            if i < 3:
                with col1:
                    criar_campo(campo)

            else:
                with col2:
                    criar_campo(campo)


    # ========================================================
    # ABA 5
    # ========================================================
    with tab5:

        col1, col2 = st.columns(2)

        for i, campo in enumerate(campos_tab5):

            if i < 4:
                with col1:
                    criar_campo(campo)

            else:
                with col2:
                    criar_campo(campo)


    return resultado


# ============================================================
# NOVO CADASTRO
# ============================================================
with st.expander(
    "➕ NOVO CADASTRO DE MILITAR",
    expanded=False
):

    st.info(
        "Preencha os dados. "
        "Os campos **Matrícula** e **Nome** são obrigatórios."
    )

    with st.form(
        "form_novo_cadastro",
        clear_on_submit=False
    ):

        novos_dados = criar_formulario(
            dados=None,
            prefixo="novo"
        )

        st.markdown("---")

        salvar_novo = st.form_submit_button(
            "💾 SALVAR NOVO CADASTRO",
            type="primary",
            use_container_width=True
        )


    # ========================================================
    # SALVAMENTO
    # ========================================================
    if salvar_novo:

        matricula = str(
            novos_dados.get("Matrícula", "")
        ).strip()

        nome = str(
            novos_dados.get("Nome", "")
        ).strip()


        if not matricula:

            st.error(
                "❌ A Matrícula é obrigatória."
            )

        elif not nome:

            st.error(
                "❌ O Nome é obrigatório."
            )

        else:

            try:

                with st.spinner(
                    "Salvando cadastro diretamente no Google Sheets..."
                ):

                    client, spreadsheet, worksheet = get_worksheet()

                    # ----------------------------------------
                    # CABEÇALHOS REAIS DA PLANILHA
                    # ----------------------------------------
                    headers = worksheet.row_values(1)

                    if not headers:

                        raise Exception(
                            "A primeira linha da aba Página1 "
                            "não possui cabeçalhos."
                        )


                    # ----------------------------------------
                    # VERIFICA MATRÍCULA
                    # ----------------------------------------
                    if "Matrícula" not in headers:

                        raise Exception(
                            "A coluna 'Matrícula' não foi encontrada "
                            "na primeira linha da aba Página1."
                        )


                    # ----------------------------------------
                    # PROCURA MATRÍCULAS EXISTENTES
                    # ----------------------------------------
                    indice_matricula = (
                        headers.index("Matrícula") + 1
                    )

                    valores_matricula = worksheet.col_values(
                        indice_matricula
                    )

                    matriculas_existentes = [
                        str(v).strip()
                        for v in valores_matricula[1:]
                        if str(v).strip()
                    ]


                    if matricula in matriculas_existentes:

                        raise Exception(
                            f"A matrícula {matricula} "
                            "já existe na planilha."
                        )


                    # ----------------------------------------
                    # MONTA LINHA EXATAMENTE NA ORDEM DA PLANILHA
                    # ----------------------------------------
                    nova_linha = []

                    for header in headers:

                        valor = novos_dados.get(
                            header,
                            ""
                        )

                        if valor is None:
                            valor = ""

                        nova_linha.append(
                            str(valor)
                        )


                    # ----------------------------------------
                    # GARANTE TAMANHO
                    # ----------------------------------------
                    if len(nova_linha) != len(headers):

                        raise Exception(
                            f"Quantidade de dados diferente. "
                            f"Headers={len(headers)}, "
                            f"Dados={len(nova_linha)}"
                        )


                    # ----------------------------------------
                    # SALVA
                    # ----------------------------------------
                    worksheet.append_row(
                        nova_linha,
                        value_input_option="USER_ENTERED"
                    )


                    # ----------------------------------------
                    # CONFIRMA LENDO NOVAMENTE
                    # ----------------------------------------
                    todas_linhas = worksheet.get_all_values()

                    if not todas_linhas:

                        raise Exception(
                            "A planilha ficou sem dados após a gravação."
                        )


                    headers_confirmacao = todas_linhas[0]

                    indice_mat_confirmacao = (
                        headers_confirmacao.index("Matrícula")
                    )

                    indice_nome_confirmacao = (
                        headers_confirmacao.index("Nome")
                    )


                    registro_confirmado = None

                    for linha in todas_linhas[1:]:

                        if (
                            len(linha)
                            > indice_mat_confirmacao
                        ):

                            if (
                                str(
                                    linha[indice_mat_confirmacao]
                                ).strip()
                                == matricula
                            ):

                                registro_confirmado = linha
                                break


                    if registro_confirmado is None:

                        raise Exception(
                            "O Google Sheets não encontrou "
                            "a matrícula após a gravação."
                        )


                    nome_gravado = ""

                    if len(registro_confirmado) > indice_nome_confirmacao:

                        nome_gravado = str(
                            registro_confirmado[
                                indice_nome_confirmacao
                            ]
                        ).strip()


                    # ----------------------------------------
                    # CONFIRMAÇÃO FINAL
                    # ----------------------------------------
                    st.success(
                        "🎉 CADASTRO GRAVADO COM SUCESSO!"
                    )

                    st.write(
                        f"**Matrícula gravada:** {matricula}"
                    )

                    st.write(
                        f"**Nome gravado:** {nome_gravado}"
                    )

                    if nome_gravado != nome:

                        st.warning(
                            "⚠️ A matrícula foi encontrada, "
                            "mas o nome gravado é diferente "
                            "do nome informado."
                        )

                    else:

                        st.success(
                            "✅ Matrícula e Nome foram "
                            "confirmados diretamente no Google Sheets."
                        )


                # --------------------------------------------
                # LIMPA CACHE
                # --------------------------------------------
                load_data.clear()


                # --------------------------------------------
                # BOTÃO PARA RECARREGAR
                # --------------------------------------------
                if st.button(
                    "🔄 Atualizar Dashboard após salvar",
                    use_container_width=True,
                    key="recarregar_pos_salvar"
                ):

                    st.rerun()


            except Exception as erro:

                st.error(
                    "❌ O CADASTRO NÃO FOI SALVO."
                )

                st.error(
                    str(erro)
                )

                st.exception(erro)


# ============================================================
# EDITAR CADASTRO
# ============================================================
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
            "não foram encontradas."
        )

    else:

        opcoes = []

        for _, linha in df.iterrows():

            matricula = str(
                linha.get("Matrícula", "")
            ).strip()

            nome = str(
                linha.get("Nome", "")
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
                df["Matrícula"].astype(str).str.strip()
                == matricula_editar
            ]


            if not registros.empty:

                dados_existentes = (
                    registros.iloc[0].to_dict()
                )


                st.info(
                    f"Editando: "
                    f"**{dados_existentes.get('Nome', '')}**"
                )


                with st.form(
                    "form_edicao",
                    clear_on_submit=False
                ):

                    dados_editados = criar_formulario(
                        dados=dados_existentes,
                        prefixo="editar"
                    )

                    st.markdown("---")

                    atualizar = st.form_submit_button(
                        "💾 SALVAR ALTERAÇÕES",
                        type="primary",
                        use_container_width=True
                    )


                if atualizar:

                    try:

                        with st.spinner(
                            "Atualizando Google Sheets..."
                        ):

                            client, spreadsheet, worksheet = (
                                get_worksheet()
                            )


                            headers = worksheet.row_values(1)


                            # --------------------------------
                            # LOCALIZA A MATRÍCULA
                            # --------------------------------
                            if "Matrícula" not in headers:

                                raise Exception(
                                    "Coluna Matrícula não encontrada."
                                )


                            indice_mat = (
                                headers.index("Matrícula")
                                + 1
                            )


                            valores = worksheet.col_values(
                                indice_mat
                            )


                            linha_encontrada = None


                            for numero_linha, valor in enumerate(
                                valores,
                                start=1
                            ):

                                if numero_linha == 1:
                                    continue

                                if (
                                    str(valor).strip()
                                    == matricula_editar
                                ):

                                    linha_encontrada = numero_linha
                                    break


                            if linha_encontrada is None:

                                raise Exception(
                                    "Matrícula não encontrada "
                                    "na aba Página1."
                                )


                            # --------------------------------
                            # MONTA LINHA
                            # --------------------------------
                            linha = []

                            for header in headers:

                                valor = dados_editados.get(
                                    header,
                                    ""
                                )

                                if valor is None:
                                    valor = ""

                                linha.append(
                                    str(valor)
                                )


                            # --------------------------------
                            # ATUALIZA
                            # --------------------------------
                            worksheet.update(
                                f"A{linha_encontrada}",
                                [linha],
                                value_input_option="USER_ENTERED"
                            )


                            # --------------------------------
                            # CONFIRMA
                            # --------------------------------
                            dados_confirmados = (
                                worksheet.row_values(
                                    linha_encontrada
                                )
                            )


                            indice_nome = (
                                headers.index("Nome")
                            )

                            nome_confirmado = ""

                            if (
                                len(dados_confirmados)
                                > indice_nome
                            ):

                                nome_confirmado = (
                                    dados_confirmados[
                                        indice_nome
                                    ]
                                )


                        st.success(
                            "✅ ALTERAÇÃO SALVA COM SUCESSO!"
                        )

                        st.write(
                            f"**Matrícula:** "
                            f"{matricula_editar}"
                        )

                        st.write(
                            f"**Nome na planilha:** "
                            f"{nome_confirmado}"
                        )

                        load_data.clear()


                    except Exception as erro:

                        st.error(
                            "❌ ERRO AO ATUALIZAR."
                        )

                        st.exception(erro)


# ============================================================
# EXCLUIR
# ============================================================
with st.expander(
    "🗑️ EXCLUIR REGISTRO",
    expanded=False
):

    if (
        "Matrícula" in df.columns
        and "Nome" in df.columns
    ):

        opcoes_exclusao = []

        for _, linha in df.iterrows():

            matricula = str(
                linha["Matrícula"]
            ).strip()

            nome = str(
                linha["Nome"]
            ).strip()

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


            confirmar = st.checkbox(
                "Confirmo que desejo excluir permanentemente.",
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

                    with st.spinner(
                        "Excluindo registro..."
                    ):

                        client, spreadsheet, worksheet = (
                            get_worksheet()
                        )


                        headers = worksheet.row_values(1)


                        indice_mat = (
                            headers.index("Matrícula")
                            + 1
                        )


                        valores = worksheet.col_values(
                            indice_mat
                        )


                        linha_encontrada = None


                        for numero_linha, valor in enumerate(
                            valores,
                            start=1
                        ):

                            if numero_linha == 1:
                                continue

                            if (
                                str(valor).strip()
                                == matricula_excluir
                            ):

                                linha_encontrada = numero_linha
                                break


                        if linha_encontrada is None:

                            raise Exception(
                                "Matrícula não encontrada."
                            )


                        worksheet.delete_rows(
                            linha_encontrada
                        )


                    load_data.clear()


                    st.success(
                        f"✅ Matrícula "
                        f"{matricula_excluir} "
                        f"excluída com sucesso."
                    )


                except Exception as erro:

                    st.error(
                        "❌ ERRO AO EXCLUIR."
                    )

                    st.exception(erro)
