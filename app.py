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

    st.subheader("📋 Visualização dos Registros")
    st.dataframe(df, use_container_width=True)
    st.markdown("---")

    # ==============================================================================
    # 2. SEÇÃO DE EDIÇÃO DE REGISTROS
    # ==============================================================================
    with st.expander("✏️ **Editar Registro Existente**", expanded=False):
        if "Matrícula" in df.columns and "Nome" in df.columns:
            opcoes_militares_edicao = df.apply(
                lambda r: f"{r['Matrícula']} - {r['Nome']}", axis=1
            ).tolist()

            militar_selecionado_edicao = st.selectbox(
                "Selecione o militar que deseja editar:",
                [""] + opcoes_militares_edicao,
                key="seletor_militar_edicao",
            )

            if militar_selecionado_edicao:
                matricula_editar = militar_selecionado_edicao.split(" - ")[0].strip()
                dados_militar = df[df["Matrícula"].astype(str) == matricula_editar].iloc[0]

                st.info(f"Editando informações de: **{dados_militar.get('Nome', '')}** (Matrícula: {matricula_editar})")

                with st.form("form_edicao_militar", clear_on_submit=False):
                    tab_ed_pessoal, tab_ed_lotacao, tab_ed_cessao, tab_ed_ltip, tab_ed_outros = st.tabs([
                        "👤 Identificação & Pessoal",
                        "🏢 Lotação & Promoção",
                        "🔄 Cessão & Movimentação",
                        "⏳ LTIP & Afastamentos",
                        "📝 Documentos & Observações",
                    ])

                    # --- ABA 1: IDENTIFICAÇÃO PESSOAL ---
                    with tab_ed_pessoal:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            e_num_funcional = st.text_input("nº Funcional:", value=str(dados_militar.get("nº Funcional", "")))
                            e_matricula = st.text_input("Matrícula:", value=str(dados_militar.get("Matrícula", "")), disabled=True)
                            e_cpf_ponto = st.text_input("CPF.:", value=str(dados_militar.get("CPF.", "")))
                            e_cpf = st.text_input("CPF:", value=str(dados_militar.get("CPF", "")))
                            e_num_ident = st.text_input("Nº IDENT.:", value=str(dados_militar.get("Nº IDENT.", "")))
                        with c2:
                            e_nome = st.text_input("Nome:", value=str(dados_militar.get("Nome", "")))
                            e_nome_guerra = st.text_input("Nome de Guerra:", value=str(dados_militar.get("Nome de Guerra", "")))

                            sexo_atual = str(dados_militar.get("SEXO", "")).upper()
                            opcoes_sexo = ["", "MASCULINO", "FEMININO"]
                            idx_sexo = opcoes_sexo.index(sexo_atual) if sexo_atual in opcoes_sexo else 0
                            e_sexo = st.selectbox("SEXO:", opcoes_sexo, index=idx_sexo)

                            raca_atual = str(dados_militar.get("Raça/Cor", "")).upper()
                            opcoes_raca = ["", "BRANCA", "PRETA", "PARDA", "AMARELA", "INDÍGENA"]
                            idx_raca = opcoes_raca.index(raca_atual) if raca_atual in opcoes_raca else 0
                            e_raca_cor = st.selectbox("Raça/Cor:", opcoes_raca, index=idx_raca)
                        with c3:
                            e_posto_grad = st.text_input("Posto/ Grad:", value=str(dados_militar.get("Posto/ Grad", "")))
                            e_fones = st.text_input("Fones:", value=str(dados_militar.get("Fones", "")))
                            e_ano_ingresso = st.text_input("Ano de ingresso:", value=str(dados_militar.get("Ano de ingresso", "")))
                            e_data_praca = st.text_input("Data de praça:", value=str(dados_militar.get("Data de praça", "")))

                    # --- ABA 2: LOTAÇÃO & PROMOÇÃO ---
                    with tab_ed_lotacao:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            e_ome = st.text_input("OME:", value=str(dados_militar.get("OME", "")))
                            e_ome_qod = st.text_input("OME QOD:", value=str(dados_militar.get("OME QOD", "")))
                            e_atividade = st.text_input("Atividade:", value=str(dados_militar.get("Atividade", "")))
                            e_municipio = st.text_input("Município:", value=str(dados_militar.get("Município", "")))
                            e_regiao = st.text_input("Região:", value=str(dados_militar.get("Região", "")))
                        with c2:
                            e_tempo_servico_anos = st.text_input("Tempo de serviço (anos):", value=str(dados_militar.get("Tempo de serviço (anos)", "")))
                            e_tempo_servico_amd = st.text_input("Tempo de serviço (ano, mês, dias):", value=str(dados_militar.get("Tempo de serviço (ano, mês, dias)", "")))
                            e_tempo_servico_dias = st.text_input("Tempo de serviço (dias):", value=str(dados_militar.get("Tempo de serviço (dias)", "")))
                            e_tempo_obm_atual = st.text_input("Tempo na OBM atual:", value=str(dados_militar.get("Tempo na OBM atual", "")))
                        with c3:
                            e_data_ult_promocao = st.text_input("Data da última promoção ou Implant. PCNH:", value=str(dados_militar.get("Data da última promoção ou Implant. PCNH", "")))
                            e_principio_ult_promocao = st.text_input("Princípio da última promoção:", value=str(dados_militar.get("Princípio da última promoção", "")))
                            e_tempo_posto_atual_dias = st.text_input("Tempo no Posto/Grad. atual EM DIAS:", value=str(dados_militar.get("Tempo no Posto/Grad. atual EM DIAS", "")))

                    # --- ABA 3: CESSÃO & MOVIMENTAÇÃO ---
                    with tab_ed_cessao:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            e_data_mov_sp = st.text_input("Data da Movimentação em SP:", value=str(dados_militar.get("Data da Movimentação em SP", "")))
                            e_ome_anterior = st.text_input("OME ANTERIOR AO ÚLTIMO SP PUBLICADO:", value=str(dados_militar.get("OME ANTERIOR AO ÚLTIMO SP PUBLICADO", "")))
                            e_data_chegada_obm_anterior = st.text_input("Data de chegada na OBM Anteior:", value=str(dados_militar.get("Data de chegada na OBM Anteior", "")))
                            e_movimentado = st.text_input("Movimentado (apagar antes de atualizar o SP):", value=str(dados_militar.get("Movimentado (apagar antes de atualizar o SP)", "")))
                        with c2:
                            e_orgao = st.text_input("ÓRGÃO:", value=str(dados_militar.get("ÓRGÃO", "")))
                            e_poder = st.text_input("Poder:", value=str(dados_militar.get("Poder", "")))

                            onus_atual = str(dados_militar.get("Ônus para Origem", "")).upper()
                            opcoes_onus = ["", "SIM", "NÃO"]
                            idx_onus = opcoes_onus.index(onus_atual) if onus_atual in opcoes_onus else 0
                            e_onus_origem = st.selectbox("Ônus para Origem:", opcoes_onus, index=idx_onus)

                            e_inicio_cessao = st.text_input("Início da Cessão ou requisição:", value=str(dados_militar.get("Início da Cessão ou requisição", "")))
                        with c3:
                            e_renovacao_cessao_atos = st.text_input("Renovação de cessão - Atos/Portarias/Documentos:", value=str(dados_militar.get("Renovação de cessão - Atos/Portarias/Documentos", "")))
                            e_doe_bgsds_renovacao = st.text_input("DOE/BGSDS de renovação:", value=str(dados_militar.get("DOE/BGSDS de renovação", "")))
                            e_sei_deslig = st.text_input("SEI deslig.:", value=str(dados_militar.get("SEI deslig.", "")))

                    # --- ABA 4: LTIP & AFASTAMENTOS ---
                    with tab_ed_ltip:
                        c1, c2 = st.columns(2)
                        with c1:
                            e_afastamentos_sup_90 = st.text_area("Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP:", value=str(dados_militar.get("Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP", "")))
                            e_inicio_ltip = st.text_input("INÍCIO DA LTIP:", value=str(dados_militar.get("INÍCIO DA LTIP", "")))
                            e_termino_ltip = st.text_input("TÉRMINO DA LTIP (inserir data de apresentação):", value=str(dados_militar.get("TÉRMINO DA LTIP (inserir data de apresentação)", "")))
                        with c2:
                            e_somatorio_ltip_anos = st.text_input("Somatório LTIP gozada em anos:", value=str(dados_militar.get("Somatório LTIP gozada em anos", "")))
                            e_somatorio_ltip_amd = st.text_input("Somatório LTIP gozada em anos/meses/dias:", value=str(dados_militar.get("Somatório LTIP gozada em anos/meses/dias", "")))
                            e_somatorio_ltip_dias = st.text_input("Somatório de todas LTIP gozadas em dias:", value=str(dados_militar.get("Somatório de todas LTIP gozadas em dias", "")))
                            e_total_dias_ltip_posto = st.text_input("TOTAL DIAS EM LTIP no MESMO Posto/Grad.:", value=str(dados_militar.get("TOTAL DIAS EM LTIP no MESMO Posto/Grad.", "")))

                    # --- ABA 5: DOCUMENTOS & OBSERVAÇÕES ---
                    with tab_ed_outros:
                        c1, c2 = st.columns(2)
                        with c1:
                            e_ato = st.text_input("Ato:", value=str(dados_militar.get("Ato", "")))
                            e_doc_publicacao = st.text_input("Doc. Publicação:", value=str(dados_militar.get("Doc. Publicação", "")))
                            e_sp_adicao = st.text_input("SP da Adição:", value=str(dados_militar.get("SP da Adição", "")))
                            e_processo_rr = st.text_input("Processo RR:", value=str(dados_militar.get("Processo RR", "")))
                        with c2:
                            e_suplemento_pessoal_num_ano = st.text_input("Suplemento de Pessoal nº/Ano:", value=str(dados_militar.get("Suplemento de Pessoal nº/Ano", "")))
                            e_data_suplemento_pessoal = st.text_input("Data Suplemento de Pessoal:", value=str(dados_militar.get("Data Suplemento de Pessoal", "")))
                            e_hoje_data = st.text_input("Hoje:", value=str(dados_militar.get("Hoje", "")))
                            e_obs = st.text_area("OBS:", value=str(dados_militar.get("OBS", "")))

                    btn_atualizar = st.form_submit_button("🔄 Atualizar Registro na Planilha")

                    if btn_atualizar:
                        try:
                            client = get_gspread_client()
                            sheet = client.open_by_key(SHEET_ID).sheet1
                            cell = sheet.find(matricula_editar)

                            if cell:
                                row_idx = cell.row
                                headers = sheet.row_values(1)

                                novos_dados_map = {
                                    "nº Funcional": e_num_funcional,
                                    "Matrícula": e_matricula,
                                    "CPF.": e_cpf_ponto,
                                    "CPF": e_cpf,
                                    "Nº IDENT.": e_num_ident,
                                    "Nome": e_nome,
                                    "Nome de Guerra": e_nome_guerra,
                                    "SEXO": e_sexo,
                                    "Raça/Cor": e_raca_cor,
                                    "Posto/ Grad": e_posto_grad,
                                    "Fones": e_fones,
                                    "Ano de ingresso": e_ano_ingresso,
                                    "Data de praça": e_data_praca,
                                    "OME": e_ome,
                                    "OME QOD": e_ome_qod,
                                    "Atividade": e_atividade,
                                    "Município": e_municipio,
                                    "Região": e_regiao,
                                    "Tempo de serviço (anos)": e_tempo_servico_anos,
                                    "Tempo de serviço (ano, mês, dias)": e_tempo_servico_amd,
                                    "Tempo de serviço (dias)": e_tempo_servico_dias,
                                    "Tempo na OBM atual": e_tempo_obm_atual,
                                    "Data da última promoção ou Implant. PCNH": e_data_ult_promocao,
                                    "Princípio da última promoção": e_principio_ult_promocao,
                                    "Tempo no Posto/Grad. atual EM DIAS": e_tempo_posto_atual_dias,
                                    "Data da Movimentação em SP": e_data_mov_sp,
                                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO": e_ome_anterior,
                                    "Data de chegada na OBM Anteior": e_data_chegada_obm_anterior,
                                    "Movimentado (apagar antes de atualizar o SP)": e_movimentado,
                                    "ÓRGÃO": e_orgao,
                                    "Poder": e_poder,
                                    "Ônus para Origem": e_onus_origem,
                                    "Início da Cessão ou requisição": e_inicio_cessao,
                                    "Renovação de cessão - Atos/Portarias/Documentos": e_renovacao_cessao_atos,
                                    "DOE/BGSDS de renovação": e_doe_bgsds_renovacao,
                                    "SEI deslig.": e_sei_deslig,
                                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP": e_afastamentos_sup_90,
                                    "INÍCIO DA LTIP": e_inicio_ltip,
                                    "TÉRMINO DA LTIP (inserir data de apresentação)": e_termino_ltip,
                                    "Somatório LTIP gozada em anos": e_somatorio_ltip_anos,
                                    "Somatório LTIP gozada em anos/meses/dias": e_somatorio_ltip_amd,
                                    "Somatório de todas LTIP gozadas em dias": e_somatorio_ltip_dias,
                                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.": e_total_dias_ltip_posto,
                                    "Ato": e_ato,
                                    "Doc. Publicação": e_doc_publicacao,
                                    "SP da Adição": e_sp_adicao,
                                    "Processo RR": e_processo_rr,
                                    "Suplemento de Pessoal nº/Ano": e_suplemento_pessoal_num_ano,
                                    "Data Suplemento de Pessoal": e_data_suplemento_pessoal,
                                    "Hoje": e_hoje_data,
                                    "OBS": e_obs,
                                }

                                linha_atualizada = [
                                    str(novos_dados_map.get(col_h, "")) for col_h in headers
                                ]

                                sheet.update(f"A{row_idx}", [linha_atualizada])
                                st.success(f"✅ Registro da Matrícula **{matricula_editar}** atualizado com sucesso!")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Registro não localizado para atualização.")

                        except Exception as err_update:
                            st.error(f"❌ Erro ao atualizar registro: {err_update}")
        else:
            st.info("As colunas 'Matrícula' e 'Nome' são necessárias para utilizar o seletor de edição.")

    # ==============================================================================
    # 3. SEÇÃO DE EXCLUSÃO DE REGISTROS
    # ==============================================================================
    with st.expander("🗑️ **Excluir Registro da Planilha**", expanded=False):
        st.warning(
            "⚠️ **Atenção:** A exclusão removerá o registro diretamente da planilha do Google Sheets e não poderá ser desfeita."
        )

        if "Matrícula" in df.columns and "Nome" in df.columns:
            opcoes_militares = df.apply(
                lambda r: f"{r['Matrícula']} - {r['Nome']}", axis=1
            ).tolist()
            militar_selecionado = st.selectbox(
                "Selecione o militar que deseja excluir:",
                [""] + opcoes_militares,
            )

            if militar_selecionado:
                matricula_alvo = militar_selecionado.split(" - ")[0].strip()
                registro_alvo = df[df["Matrícula"].astype(str) == matricula_alvo]

                st.write("**Dados do registro selecionado:**")
                st.dataframe(registro_alvo, use_container_width=True)

                confirmar = st.checkbox(
                    "Confirmo que desejo excluir permanentemente este registro."
                )
                btn_excluir = st.button(
                    "🔴 Excluir Registro", type="primary", disabled=not confirmar
                )

                if btn_excluir:
                    try:
                        client = get_gspread_client()
                        sheet = client.open_by_key(SHEET_ID).sheet1
                        cell = sheet.find(matricula_alvo)

                        if cell:
                            sheet.delete_rows(cell.row)
                            st.success(
                                f"✅ Registro da Matrícula **{matricula_alvo}** excluído com sucesso!"
                            )
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(
                                f"❌ Matrícula {matricula_alvo} não foi localizada na planilha."
                            )

                    except Exception as err_exc:
                        st.error(f"❌ Erro ao excluir registro no Google Sheets: {err_exc}")
        else:
            st.info("As colunas 'Matrícula' e 'Nome' são necessárias para utilizar o seletor de exclusão.")

except KeyError as key_err:
    st.error(f"❌ Chave de segredo não encontrada no `secrets.toml`: {key_err}")
except Exception as e:
    st.error(f"❌ Ocorreu um erro geral na aplicação: {e}")
