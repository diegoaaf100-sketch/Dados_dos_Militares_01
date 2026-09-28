import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DGP - Dados dos Militares",
    layout="wide"
)

# ============================================================
# ESCOPOS PARA A API DO GOOGLE SHEETS
# ============================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ============================================================
# AUTENTICAÇÃO DO USUÁRIO
# ============================================================
def check_password():
    """Valida usuário e senha comparando com [passwords] nos Secrets."""

    def password_entered():
        user = st.session_state.get("username", "").strip()
        pwd = st.session_state.get("password", "").strip()
        passwords_dict = st.secrets.get("passwords", {})

        if user in passwords_dict and str(passwords_dict[user]) == pwd:
            st.session_state["password_correct"] = True

            if "password" in st.session_state:
                del st.session_state["password"]

            if "username" in st.session_state:
                del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Acesso Restrito ao Dashboard")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")

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


# Bloqueia execução se não estiver autenticado
if not check_password():
    st.stop()


# ============================================================
# AUTENTICAÇÃO GOOGLE SHEETS
# ============================================================
def get_gspread_client():
    """Autentica na API do Google usando o bloco
    [gcp_service_account] dos Secrets.
    """

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


# ============================================================
# BARRA LATERAL
# ============================================================
st.sidebar.success("Autenticado com sucesso!")

if st.sidebar.button("🚪 Sair / Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

if st.sidebar.button("🔄 Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# CABEÇALHO E LOGOS
# ============================================================
_, col_img1, col_img2, _ = st.columns([2, 1, 1, 2])

with col_img1:
    st.image("images.png", width=140)

with col_img2:
    st.image("11679.png", width=140)

st.markdown(
    "<h1 style='text-align: center;'>DGP - Dados dos Militares</h1>",
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

    df = pd.read_csv(url, header=0)

    df.columns = [
        str(col).strip().replace(":", "-")
        for col in df.columns
    ]

    df = df.fillna("-")

    return df


# ============================================================
# FUNÇÃO PARA MONTAR O FORMULÁRIO
# ============================================================
def formulario_militar(dados=None, prefixo="novo"):
    """
    Cria o formulário de cadastro/edição.

    Se dados=None, cria formulário vazio.
    Se dados for informado, preenche com os dados existentes.
    """

    if dados is None:
        dados = {}

    def valor(coluna):
        valor_atual = dados.get(coluna, "")
        if pd.isna(valor_atual):
            return ""
        return str(valor_atual)

    # ========================================================
    # ABA 1 - IDENTIFICAÇÃO PESSOAL
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

    with tab_pessoal:

        c1, c2, c3 = st.columns(3)

        with c1:
            num_funcional = st.text_input(
                "nº Funcional:",
                value=valor("nº Funcional"),
                key=f"{prefixo}_num_funcional"
            )

            matricula = st.text_input(
                "Matrícula:",
                value=valor("Matrícula"),
                key=f"{prefixo}_matricula"
            )

            cpf_ponto = st.text_input(
                "CPF.:",
                value=valor("CPF."),
                key=f"{prefixo}_cpf_ponto"
            )

            cpf = st.text_input(
                "CPF:",
                value=valor("CPF"),
                key=f"{prefixo}_cpf"
            )

            num_ident = st.text_input(
                "Nº IDENT.:",
                value=valor("Nº IDENT."),
                key=f"{prefixo}_num_ident"
            )

        with c2:
            nome = st.text_input(
                "Nome:",
                value=valor("Nome"),
                key=f"{prefixo}_nome"
            )

            nome_guerra = st.text_input(
                "Nome de Guerra:",
                value=valor("Nome de Guerra"),
                key=f"{prefixo}_nome_guerra"
            )

            sexo_atual = valor("SEXO").upper()

            opcoes_sexo = [
                "",
                "MASCULINO",
                "FEMININO"
            ]

            idx_sexo = (
                opcoes_sexo.index(sexo_atual)
                if sexo_atual in opcoes_sexo
                else 0
            )

            sexo = st.selectbox(
                "SEXO:",
                opcoes_sexo,
                index=idx_sexo,
                key=f"{prefixo}_sexo"
            )

            raca_atual = valor("Raça/Cor").upper()

            opcoes_raca = [
                "",
                "BRANCA",
                "PRETA",
                "PARDA",
                "AMARELA",
                "INDÍGENA"
            ]

            idx_raca = (
                opcoes_raca.index(raca_atual)
                if raca_atual in opcoes_raca
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
                value=valor("Posto/ Grad"),
                key=f"{prefixo}_posto_grad"
            )

            fones = st.text_input(
                "Fones:",
                value=valor("Fones"),
                key=f"{prefixo}_fones"
            )

            ano_ingresso = st.text_input(
                "Ano de ingresso:",
                value=valor("Ano de ingresso"),
                key=f"{prefixo}_ano_ingresso"
            )

            data_praca = st.text_input(
                "Data de praça:",
                value=valor("Data de praça"),
                key=f"{prefixo}_data_praca"
            )

    # ========================================================
    # ABA 2 - LOTAÇÃO & PROMOÇÃO
    # ========================================================
    with tab_lotacao:

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

            tempo_servico_anos = st.text_input(
                "Tempo de serviço (anos):",
                value=valor("Tempo de serviço (anos)"),
                key=f"{prefixo}_tempo_servico_anos"
            )

            tempo_servico_amd = st.text_input(
                "Tempo de serviço (ano, mês, dias):",
                value=valor("Tempo de serviço (ano, mês, dias)"),
                key=f"{prefixo}_tempo_servico_amd"
            )

            tempo_servico_dias = st.text_input(
                "Tempo de serviço (dias):",
                value=valor("Tempo de serviço (dias)"),
                key=f"{prefixo}_tempo_servico_dias"
            )

            tempo_obm_atual = st.text_input(
                "Tempo na OBM atual:",
                value=valor("Tempo na OBM atual"),
                key=f"{prefixo}_tempo_obm_atual"
            )

        with c3:

            data_ult_promocao = st.text_input(
                "Data da última promoção ou Implant. PCNH:",
                value=valor(
                    "Data da última promoção ou Implant. PCNH"
                ),
                key=f"{prefixo}_data_ult_promocao"
            )

            principio_ult_promocao = st.text_input(
                "Princípio da última promoção:",
                value=valor(
                    "Princípio da última promoção"
                ),
                key=f"{prefixo}_principio_promocao"
            )

            tempo_posto_atual_dias = st.text_input(
                "Tempo no Posto/Grad. atual EM DIAS:",
                value=valor(
                    "Tempo no Posto/Grad. atual EM DIAS"
                ),
                key=f"{prefixo}_tempo_posto"
            )

    # ========================================================
    # ABA 3 - CESSÃO & MOVIMENTAÇÃO
    # ========================================================
    with tab_cessao:

        c1, c2, c3 = st.columns(3)

        with c1:

            data_mov_sp = st.text_input(
                "Data da Movimentação em SP:",
                value=valor("Data da Movimentação em SP"),
                key=f"{prefixo}_data_mov_sp"
            )

            ome_anterior = st.text_input(
                "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:",
                value=valor(
                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO"
                ),
                key=f"{prefixo}_ome_anterior"
            )

            data_chegada_obm_anterior = st.text_input(
                "Data de chegada na OBM Anteior:",
                value=valor(
                    "Data de chegada na OBM Anteior"
                ),
                key=f"{prefixo}_data_chegada"
            )

            movimentado = st.text_input(
                "Movimentado (apagar antes de atualizar o SP):",
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

            onus_atual = valor("Ônus para Origem").upper()

            opcoes_onus = [
                "",
                "SIM",
                "NÃO"
            ]

            idx_onus = (
                opcoes_onus.index(onus_atual)
                if onus_atual in opcoes_onus
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
                value=valor(
                    "Início da Cessão ou requisição"
                ),
                key=f"{prefixo}_inicio_cessao"
            )

        with c3:

            renovacao_cessao_atos = st.text_input(
                "Renovação de cessão - Atos/Portarias/Documentos:",
                value=valor(
                    "Renovação de cessão - Atos/Portarias/Documentos"
                ),
                key=f"{prefixo}_renovacao"
            )

            doe_bgsds_renovacao = st.text_input(
                "DOE/BGSDS de renovação:",
                value=valor(
                    "DOE/BGSDS de renovação"
                ),
                key=f"{prefixo}_doe"
            )

            sei_deslig = st.text_input(
                "SEI deslig.:",
                value=valor("SEI deslig."),
                key=f"{prefixo}_sei"
            )

    # ========================================================
    # ABA 4 - LTIP & AFASTAMENTOS
    # ========================================================
    with tab_ltip:

        c1, c2 = st.columns(2)

        with c1:

            afastamentos_sup_90 = st.text_area(
                "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
                "ININTERRUPTOS, PUBLICADOS EM SP:",
                value=valor(
                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
                    "ININTERRUPTOS, PUBLICADOS EM SP"
                ),
                key=f"{prefixo}_afastamentos"
            )

            inicio_ltip = st.text_input(
                "INÍCIO DA LTIP:",
                value=valor("INÍCIO DA LTIP"),
                key=f"{prefixo}_inicio_ltip"
            )

            termino_ltip = st.text_input(
                "TÉRMINO DA LTIP (inserir data de apresentação):",
                value=valor(
                    "TÉRMINO DA LTIP (inserir data de apresentação)"
                ),
                key=f"{prefixo}_termino_ltip"
            )

        with c2:

            somatorio_ltip_anos = st.text_input(
                "Somatório LTIP gozada em anos:",
                value=valor(
                    "Somatório LTIP gozada em anos"
                ),
                key=f"{prefixo}_somatorio_anos"
            )

            somatorio_ltip_amd = st.text_input(
                "Somatório LTIP gozada em anos/meses/dias:",
                value=valor(
                    "Somatório LTIP gozada em anos/meses/dias"
                ),
                key=f"{prefixo}_somatorio_amd"
            )

            somatorio_ltip_dias = st.text_input(
                "Somatório de todas LTIP gozadas em dias:",
                value=valor(
                    "Somatório de todas LTIP gozadas em dias"
                ),
                key=f"{prefixo}_somatorio_dias"
            )

            total_dias_ltip_posto = st.text_input(
                "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:",
                value=valor(
                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad."
                ),
                key=f"{prefixo}_total_ltip"
            )

    # ========================================================
    # ABA 5 - DOCUMENTOS & OBSERVAÇÕES
    # ========================================================
    with tab_outros:

        c1, c2 = st.columns(2)

        with c1:

            ato = st.text_input(
                "Ato:",
                value=valor("Ato"),
                key=f"{prefixo}_ato"
            )

            doc_publicacao = st.text_input(
                "Doc. Publicação:",
                value=valor("Doc. Publicação"),
                key=f"{prefixo}_doc_publicacao"
            )

            sp_adicao = st.text_input(
                "SP da Adição:",
                value=valor("SP da Adição"),
                key=f"{prefixo}_sp_adicao"
            )

            processo_rr = st.text_input(
                "Processo RR:",
                value=valor("Processo RR"),
                key=f"{prefixo}_processo_rr"
            )

        with c2:

            suplemento_pessoal_num_ano = st.text_input(
                "Suplemento de Pessoal nº/Ano:",
                value=valor(
                    "Suplemento de Pessoal nº/Ano"
                ),
                key=f"{prefixo}_suplemento"
            )

            data_suplemento_pessoal = st.text_input(
                "Data Suplemento de Pessoal:",
                value=valor(
                    "Data Suplemento de Pessoal"
                ),
                key=f"{prefixo}_data_suplemento"
            )

            hoje_data = st.text_input(
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
    # RETORNA TODOS OS DADOS
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
        "Data de chegada na OBM Anteior": data_chegada_obm_anterior,
        "Movimentado (apagar antes de atualizar o SP)": movimentado,
        "ÓRGÃO": orgao,
        "Poder": poder,
        "Ônus para Origem": onus_origem,
        "Início da Cessão ou requisição": inicio_cessao,
        "Renovação de cessão - Atos/Portarias/Documentos": renovacao_cessao_atos,
        "DOE/BGSDS de renovação": doe_bgsds_renovacao,
        "SEI deslig.": sei_deslig,
        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP": afastamentos_sup_90,
        "INÍCIO DA LTIP": inicio_ltip,
        "TÉRMINO DA LTIP (inserir data de apresentação)": termino_ltip,
        "Somatório LTIP gozada em anos": somatorio_ltip_anos,
        "Somatório LTIP gozada em anos/meses/dias": somatorio_ltip_amd,
        "Somatório de todas LTIP gozadas em dias": somatorio_ltip_dias,
        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.": total_dias_ltip_posto,
        "Ato": ato,
        "Doc. Publicação": doc_publicacao,
        "SP da Adição": sp_adicao,
        "Processo RR": processo_rr,
        "Suplemento de Pessoal nº/Ano": suplemento_pessoal_num_ano,
        "Data Suplemento de Pessoal": data_suplemento_pessoal,
        "Hoje": hoje_data,
        "OBS": obs,
    }


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
try:

    SHEET_ID = st.secrets["SHEET_ID"]

    # ========================================================
    # CARREGAMENTO INICIAL
    # ========================================================
    df = load_data(SHEET_ID)

    st.subheader("📋 Visualização dos Registros")
    st.dataframe(
        df,
        use_container_width=True
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
            "Preencha os dados abaixo e clique em "
            "**Salvar Novo Cadastro**."
        )

        with st.form(
            "form_novo_cadastro",
            clear_on_submit=False
        ):

            novos_dados = formulario_militar(
                dados=None,
                prefixo="novo"
            )

            btn_salvar = st.form_submit_button(
                "💾 Salvar Novo Cadastro",
                type="primary",
                use_container_width=True
            )

            if btn_salvar:

                try:

                    # ----------------------------------------
                    # VALIDAÇÃO DA MATRÍCULA
                    # ----------------------------------------
                    matricula_nova = (
                        str(
                            novos_dados.get(
                                "Matrícula",
                                ""
                            )
                        )
                        .strip()
                    )

                    nome_novo = (
                        str(
                            novos_dados.get(
                                "Nome",
                                ""
                            )
                        )
                        .strip()
                    )

                    if not matricula_nova:
                        st.error(
                            "❌ A Matrícula é obrigatória."
                        )
                        st.stop()

                    if not nome_novo:
                        st.error(
                            "❌ O Nome é obrigatório."
                        )
                        st.stop()

                    # ----------------------------------------
                    # CONECTA AO GOOGLE SHEETS
                    # ----------------------------------------
                    client = get_gspread_client()

                    sheet = client.open_by_key(
                        SHEET_ID
                    ).sheet1

                    # ----------------------------------------
                    # PEGA CABEÇALHOS REAIS DA PLANILHA
                    # ----------------------------------------
                    headers = sheet.row_values(1)

                    if not headers:
                        st.error(
                            "❌ Não foi possível encontrar "
                            "os cabeçalhos da planilha."
                        )
                        st.stop()

                    # ----------------------------------------
                    # VERIFICA SE MATRÍCULA JÁ EXISTE
                    # ----------------------------------------
                    if "Matrícula" in headers:

                        col_matricula = (
                            headers.index("Matrícula") + 1
                        )

                        valores_matricula = sheet.col_values(
                            col_matricula
                        )

                        matriculas_existentes = [
                            str(v).strip()
                            for v in valores_matricula[1:]
                            if str(v).strip()
                        ]

                        if matricula_nova in matriculas_existentes:
                            st.error(
                                f"❌ A matrícula "
                                f"**{matricula_nova}** "
                                f"já está cadastrada."
                            )
                            st.stop()

                    # ----------------------------------------
                    # MONTA A NOVA LINHA NA MESMA ORDEM
                    # DOS CABEÇALHOS DA PLANILHA
                    # ----------------------------------------
                    nova_linha = [
                        str(
                            novos_dados.get(
                                coluna,
                                ""
                            )
                        )
                        for coluna in headers
                    ]

                    # ----------------------------------------
                    # INSERE A NOVA LINHA
                    # ----------------------------------------
                    sheet.append_row(
                        nova_linha,
                        value_input_option="USER_ENTERED"
                    )

                    # ----------------------------------------
                    # SUCESSO
                    # ----------------------------------------
                    st.success(
                        f"✅ Novo cadastro da Matrícula "
                        f"**{matricula_nova}** salvo "
                        f"com sucesso!"
                    )

                    # Limpa cache
                    st.cache_data.clear()

                    # Atualiza a aplicação
                    st.rerun()

                except Exception as err_novo:

                    st.error(
                        "❌ Erro ao salvar novo cadastro "
                        f"no Google Sheets:\n\n{err_novo}"
                    )

    # ========================================================
    # 2. EDIÇÃO DE REGISTRO
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
                    == matricula_editar
                ]

                if registros.empty:

                    st.error(
                        "❌ Registro não localizado."
                    )

                else:

                    dados_militar = registros.iloc[0].to_dict()

                    st.info(
                        f"Editando informações de: "
                        f"**{dados_militar.get('Nome', '')}** "
                        f"(Matrícula: {matricula_editar})"
                    )

                    with st.form(
                        "form_edicao_militar",
                        clear_on_submit=False
                    ):

                        dados_editados = formulario_militar(
                            dados=dados_militar,
                            prefixo="edicao"
                        )

                        # Matrícula não pode ser alterada
                        dados_editados["Matrícula"] = (
                            matricula_editar
                        )

                        btn_atualizar = (
                            st.form_submit_button(
                                "🔄 Atualizar Registro "
                                "na Planilha",
                                use_container_width=True
                            )
                        )

                        if btn_atualizar:

                            try:

                                client = (
                                    get_gspread_client()
                                )

                                sheet = (
                                    client
                                    .open_by_key(SHEET_ID)
                                    .sheet1
                                )

                                # --------------------------------
                                # LOCALIZA LINHA
                                # --------------------------------
                                cell = sheet.find(
                                    matricula_editar
                                )

                                if cell:

                                    row_idx = cell.row

                                    headers = (
                                        sheet.row_values(1)
                                    )

                                    linha_atualizada = [
                                        str(
                                            dados_editados.get(
                                                col_h,
                                                ""
                                            )
                                        )
                                        for col_h in headers
                                    ]

                                    # Atualiza a linha completa
                                    sheet.update(
                                        f"A{row_idx}",
                                        [linha_atualizada],
                                        value_input_option="USER_ENTERED"
                                    )

                                    st.success(
                                        f"✅ Registro da Matrícula "
                                        f"**{matricula_editar}** "
                                        f"atualizado com sucesso!"
                                    )

                                    st.cache_data.clear()
                                    st.rerun()

                                else:

                                    st.error(
                                        "❌ Registro não localizado "
                                        "para atualização."
                                    )

                            except Exception as err_update:

                                st.error(
                                    "❌ Erro ao atualizar registro: "
                                    f"{err_update}"
                                )

        else:

            st.info(
                "As colunas 'Matrícula' e 'Nome' são "
                "necessárias para utilizar o seletor "
                "de edição."
            )

    # ========================================================
    # 3. EXCLUSÃO DE REGISTRO
    # ========================================================
    with st.expander(
        "🗑️ **Excluir Registro da Planilha**",
        expanded=False
    ):

        st.warning(
            "⚠️ **Atenção:** A exclusão removerá o "
            "registro diretamente da planilha do "
            "Google Sheets e não poderá ser desfeita."
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
                    "🔴 Excluir Registro",
                    type="primary",
                    disabled=not confirmar,
                    key="btn_excluir"
                )

                if btn_excluir:

                    try:

                        client = (
                            get_gspread_client()
                        )

                        sheet = (
                            client
                            .open_by_key(SHEET_ID)
                            .sheet1
                        )

                        cell = sheet.find(
                            matricula_alvo
                        )

                        if cell:

                            sheet.delete_rows(
                                cell.row
                            )

                            st.success(
                                f"✅ Registro da Matrícula "
                                f"**{matricula_alvo}** "
                                f"excluído com sucesso!"
                            )

                            st.cache_data.clear()
                            st.rerun()

                        else:

                            st.error(
                                f"❌ Matrícula "
                                f"{matricula_alvo} "
                                "não foi localizada "
                                "na planilha."
                            )

                    except Exception as err_exc:

                        st.error(
                            "❌ Erro ao excluir registro "
                            "no Google Sheets: "
                            f"{err_exc}"
                        )

        else:

            st.info(
                "As colunas 'Matrícula' e 'Nome' são "
                "necessárias para utilizar o seletor "
                "de exclusão."
            )


# ============================================================
# TRATAMENTO DE ERROS GERAIS
# ============================================================
except KeyError as key_err:

    st.error(
        "❌ Chave de segredo não encontrada "
        f"no `secrets.toml`: {key_err}"
    )

except Exception as e:

    st.error(
        "❌ Ocorreu um erro geral na aplicação: "
        f"{e}"
    )
