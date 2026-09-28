import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DGP - Dados dos Militares", layout="wide")

# --- ESCOPOS PARA A API DO GOOGLE SHEETS ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# --- FUNÇÃO DE AUTENTICAÇÃO DO USUÁRIO ---
def check_password():
    """Valida usuário e senha comparando com o bloco [passwords] nos Secrets."""

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
        st.button("Entrar", on_click=password_entered)

        if "password_correct" in st.session_state and not st.session_state[
            "password_correct"
        ]:
            st.error("😕 Usuário ou senha incorretos.")

    return False


# Bloqueia a execução se não estiver autenticado
if not check_password():
    st.stop()


# --- FUNÇÃO DE AUTENTICAÇÃO COM O GOOGLE SHEETS (GSPREAD) ---
def get_gspread_client():
    """Autentica na API do Google usando o bloco [gcp_service_account] dos Secrets."""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(credentials)


# --- BARRA LATERAL (LOGOUT E REFRESH) ---
st.sidebar.success("Autenticado com sucesso!")
if st.sidebar.button("🚪 Sair / Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

if st.sidebar.button("🔄 Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()

# --- CABEÇALHO E LOGOS ---
_, col_img1, col_img2, _ = st.columns([2, 1, 1, 2])
with col_img1:
    st.image("images.png", width=140)
with col_img2:
    st.image("11679.png", width=140)

st.markdown(
    "<h1 style='text-align: center;'> DGP - Dados dos Militares</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")


# --- FUNÇÃO DE CARREGAMENTO DOS DADOS ---
@st.cache_data(ttl=5)
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url, header=0)
    df.columns = [str(col).strip().replace(":", "-") for col in df.columns]
    df = df.fillna("-")
    return df


try:
    SHEET_ID = st.secrets["SHEET_ID"]

    # ==============================================================================
    # 1. CARREGAMENTO INICIAL DO DATAFRAME
    # ==============================================================================
    df = load_data(SHEET_ID)

   # ==============================================================================
    # 2. FORMULÁRIO DE CADASTRO DE NOVOS REGISTROS (SEM ENCAPSULAMENTO PROBLEMATICO)
    # ==============================================================================
    st.subheader("➕ Cadastrar Novo Militar")

    tab_pessoal, tab_lotacao, tab_cessao, tab_ltip, tab_outros = st.tabs([
        "👤 Identificação & Pessoal",
        "🏢 Lotação & Promoção",
        "🔄 Cessão & Movimentação",
        "⏳ LTIP & Afastamentos",
        "📝 Documentos & Observações",
    ])

    # --- ABA 1: IDENTIFICAÇÃO PESSOAL ---
    with tab_pessoal:
        c1, c2, c3 = st.columns(3)
        with c1:
            num_funcional = st.text_input("nº Funcional:", key="add_num_funcional")
            matricula = st.text_input("Matrícula *:", key="add_matricula")
            cpf_ponto = st.text_input("CPF.:", key="add_cpf_ponto")
            cpf = st.text_input("CPF:", key="add_cpf")
            num_ident = st.text_input("Nº IDENT.:", key="add_num_ident")
        with c2:
            nome = st.text_input("Nome:", key="add_nome")
            nome_guerra = st.text_input("Nome de Guerra:", key="add_nome_guerra")
            sexo = st.selectbox("SEXO:", ["", "MASCULINO", "FEMININO"], key="add_sexo")
            raca_cor = st.selectbox(
                "Raça/Cor:",
                ["", "BRANCA", "PRETA", "PARDA", "AMARELA", "INDÍGENA"],
                key="add_raca_cor"
            )
        with c3:
            posto_grad = st.text_input("Posto/ Grad:", key="add_posto_grad")
            fones = st.text_input("Fones:", key="add_fones")
            ano_ingresso = st.text_input("Ano de ingresso:", key="add_ano_ingresso")
            data_praca = st.date_input("Data de praça:", value=None, key="add_data_praca")

    # --- ABA 2: LOTAÇÃO & PROMOÇÃO ---
    with tab_lotacao:
        c1, c2, c3 = st.columns(3)
        with c1:
            ome = st.text_input("OME:", key="add_ome")
            ome_qod = st.text_input("OME QOD:", key="add_ome_qod")
            atividade = st.text_input("Atividade:", key="add_atividade")
            municipio = st.text_input("Município:", key="add_municipio")
            regiao = st.text_input("Região:", key="add_regiao")
        with c2:
            tempo_servico_anos = st.text_input("Tempo de serviço (anos):", key="add_tempo_servico_anos")
            tempo_servico_amd = st.text_input("Tempo de serviço (ano, mês, dias):", key="add_tempo_servico_amd")
            tempo_servico_dias = st.text_input("Tempo de serviço (dias):", key="add_tempo_servico_dias")
            tempo_obm_atual = st.text_input("Tempo na OBM atual:", key="add_tempo_obm_atual")
        with c3:
            data_ult_promocao = st.date_input("Data da última promoção:", value=None, key="add_data_ult_promocao")
            principio_ult_promocao = st.text_input("Princípio da última promoção:", key="add_principio_ult_promocao")
            tempo_posto_atual_dias = st.text_input("Tempo no Posto/Grad. atual EM DIAS:", key="add_tempo_posto_atual_dias")

    # --- ABA 3: CESSÃO & MOVIMENTAÇÃO ---
    with tab_cessao:
        c1, c2, c3 = st.columns(3)
        with c1:
            data_mov_sp = st.date_input("Data da Movimentação em SP:", value=None, key="add_data_mov_sp")
            ome_anterior = st.text_input("OME ANTERIOR AO ÚLTIMO SP PUBLICADO:", key="add_ome_anterior")
            data_chegada_obm_anterior = st.date_input("Data de chegada na OBM Anteior:", value=None, key="add_data_chegada_obm_anterior")
            movimentado = st.text_input("Movimentado:", key="add_movimentado")
        with c2:
            orgao = st.text_input("ÓRGÃO:", key="add_orgao")
            poder = st.text_input("Poder:", key="add_poder")
            onus_origem = st.selectbox("Ônus para Origem:", ["", "SIM", "NÃO"], key="add_onus_origem")
            inicio_cessao = st.date_input("Início da Cessão ou requisição:", value=None, key="add_inicio_cessao")
        with c3:
            renovacao_cessao_atos = st.text_input("Renovação de cessão - Atos:", key="add_renovacao_cessao_atos")
            doe_bgsds_renovacao = st.text_input("DOE/BGSDS de renovação:", key="add_doe_bgsds_renovacao")
            sei_deslig = st.text_input("SEI deslig.:", key="add_sei_deslig")

    # --- ABA 4: LTIP & AFASTAMENTOS ---
    with tab_ltip:
        c1, c2 = st.columns(2)
        with c1:
            afastamentos_sup_90 = st.text_area("AFASTAMENTOS SUP. A 90 DIAS:", key="add_afastamentos_sup_90")
            inicio_ltip = st.date_input("INÍCIO DA LTIP:", value=None, key="add_inicio_ltip")
            termino_ltip = st.date_input("TÉRMINO DA LTIP:", value=None, key="add_termino_ltip")
        with c2:
            somatorio_ltip_anos = st.text_input("Somatório LTIP em anos:", key="add_somatorio_ltip_anos")
            somatorio_ltip_amd = st.text_input("Somatório LTIP em anos/meses/dias:", key="add_somatorio_ltip_amd")
            somatorio_ltip_dias = st.number_input("Somatório LTIP em dias:", min_value=0, step=1, key="add_somatorio_ltip_dias")
            total_dias_ltip_posto = st.number_input("TOTAL DIAS EM LTIP no MESMO Posto:", min_value=0, step=1, key="add_total_dias_ltip_posto")

    # --- ABA 5: DOCUMENTOS & OBSERVAÇÕES ---
    with tab_outros:
        c1, c2 = st.columns(2)
        with c1:
            ato = st.text_input("Ato:", key="add_ato")
            doc_publicacao = st.text_input("Doc. Publicação:", key="add_doc_publicacao")
            sp_adicao = st.text_input("SP da Adição:", key="add_sp_adicao")
            processo_rr = st.text_input("Processo RR:", key="add_processo_rr")
        with c2:
            suplemento_pessoal_num_ano = st.text_input("Suplemento de Pessoal nº/Ano:", key="add_suplemento_pessoal_num_ano")
            data_suplemento_pessoal = st.date_input("Data Suplemento de Pessoal:", value=None, key="add_data_suplemento_pessoal")
            hoje_data = st.date_input("Hoje:", value=None, key="add_hoje_data")
            obs = st.text_area("OBS:", key="add_obs")

    st.markdown("---")
    # Botão comum do Streamlit (sem st.form nem st.expander travando o ciclo)
    btn_salvar = st.button("💾 Salvar Registro Completo na Planilha", type="primary")

    if btn_salvar:
        if not matricula.strip():
            st.error("❌ O campo **Matrícula** é obrigatório para cadastrar um novo militar.")
        else:
            try:
                with st.spinner("Conectando ao Google Sheets e salvando..."):
                    client = get_gspread_client()
                    spreadsheet = client.open_by_key(SHEET_ID)
                    
                    # Acessa a primeira aba da planilha
                    sheet = spreadsheet.sheet1

                    # Pega a primeira linha da planilha (cabeçalhos originais)
                    headers_brutos = sheet.row_values(1)
                    
                    if not headers_brutos:
                        st.error("❌ A planilha parece estar vazia ou a linha 1 de cabeçalho não foi encontrada.")
                        st.stop()

                    # Mapeamento completo dos inputs
                    dados_input = {
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
                        "Data de praça": data_praca.strftime("%d/%m/%Y") if data_praca else "",
                        "OME": ome,
                        "OME QOD": ome_qod,
                        "Atividade": atividade,
                        "Município": municipio,
                        "Região": regiao,
                        "Tempo de serviço (anos)": tempo_servico_anos,
                        "Tempo de serviço (ano, mês, dias)": tempo_servico_amd,
                        "Tempo de serviço (dias)": tempo_servico_dias,
                        "Tempo na OBM atual": tempo_obm_atual,
                        "Data da última promoção ou Implant. PCNH": data_ult_promocao.strftime("%d/%m/%Y") if data_ult_promocao else "",
                        "Princípio da última promoção": principio_ult_promocao,
                        "Tempo no Posto/Grad. atual EM DIAS": tempo_posto_atual_dias,
                        "Data da Movimentação em SP": data_mov_sp.strftime("%d/%m/%Y") if data_mov_sp else "",
                        "OME ANTERIOR AO ÚLTIMO SP PUBLICADO": ome_anterior,
                        "Data de chegada na OBM Anteior": data_chegada_obm_anterior.strftime("%d/%m/%Y") if data_chegada_obm_anterior else "",
                        "Movimentado (apagar antes de atualizar o SP)": movimentado,
                        "ÓRGÃO": orgao,
                        "Poder": poder,
                        "Ônus para Origem": onus_origem,
                        "Início da Cessão ou requisição": inicio_cessao.strftime("%d/%m/%Y") if inicio_cessao else "",
                        "Renovação de cessão - Atos/Portarias/Documentos": renovacao_cessao_atos,
                        "DOE/BGSDS de renovação": doe_bgsds_renovacao,
                        "SEI deslig.": sei_deslig,
                        "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP": afastamentos_sup_90,
                        "INÍCIO DA LTIP": inicio_ltip.strftime("%d/%m/%Y") if inicio_ltip else "",
                        "TÉRMINO DA LTIP (inserir data de apresentação)": termino_ltip.strftime("%d/%m/%Y") if termino_ltip else "",
                        "Somatório LTIP gozada em anos": somatorio_ltip_anos,
                        "Somatório LTIP gozada em anos/meses/dias": somatorio_ltip_amd,
                        "Somatório de todas LTIP gozadas em dias": str(somatorio_ltip_dias) if somatorio_ltip_dias else "0",
                        "TOTAL DIAS EM LTIP no MESMO Posto/Grad.": str(total_dias_ltip_posto) if total_dias_ltip_posto else "0",
                        "Ato": ato,
                        "Doc. Publicação": doc_publicacao,
                        "SP da Adição": sp_adicao,
                        "Processo RR": processo_rr,
                        "Suplemento de Pessoal nº/Ano": suplemento_pessoal_num_ano,
                        "Data Suplemento de Pessoal": data_suplemento_pessoal.strftime("%d/%m/%Y") if data_suplemento_pessoal else "",
                        "Hoje": hoje_data.strftime("%d/%m/%Y") if hoje_data else "",
                        "OBS": obs,
                    }

                    # Monta a linha mantendo EXATAMENTE a ordem das colunas do Google Sheets
                    linha_para_inserir = []
                    for h in headers_brutos:
                        col_chave = str(h).strip()
                        val = dados_input.get(col_chave, "")
                        linha_para_inserir.append(str(val))

                    # Inserção direta
                    sheet.append_row(linha_para_inserir, value_input_option="USER_ENTERED")

                    st.success(f"✅ Militar **{nome}** (Matrícula: {matricula}) cadastrado e salvo na planilha com sucesso!")
                    st.cache_data.clear()

            except gspread.exceptions.APIError as api_err:
                st.error(f"❌ Erro da API do Google Sheets: {api_err}")
            except Exception as err_add:
                st.error(f"❌ Erro ao adicionar novo registro: {err_add}")
