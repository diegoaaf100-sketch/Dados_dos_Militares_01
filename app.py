import streamlit as st

st.title("🚨 TESTE NOVA VERSÃO - 28/09/2026")

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="DGP - Teste Google Sheets",
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

    st.title("🔒 Acesso Restrito")

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
                "Usuário ou senha incorretos."
            )

    return False


if not check_password():
    st.stop()


# ============================================================
# CONEXÃO GOOGLE
# ============================================================

def get_google_client():

    try:

        if "gcp_service_account" not in st.secrets:

            raise Exception(
                "O bloco [gcp_service_account] "
                "não foi encontrado nos Secrets."
            )

        credentials = (
            Credentials.from_service_account_info(
                st.secrets[
                    "gcp_service_account"
                ],
                scopes=SCOPES
            )
        )

        client = gspread.authorize(
            credentials
        )

        return client

    except Exception as e:

        raise Exception(
            f"Erro na autenticação Google: {e}"
        )


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "📊 DGP - Teste de Conexão"
)

st.markdown("---")


# ============================================================
# CONFIGURAÇÃO DA PLANILHA
# ============================================================

try:

    SHEET_ID = st.secrets["SHEET_ID"]

except Exception:

    st.error(
        "❌ SHEET_ID não encontrado nos Secrets."
    )

    st.stop()


st.write(
    "### Configuração atual"
)

st.code(
    f"SHEET_ID = {SHEET_ID}"
)

st.info(
    "A aba que será utilizada é: Página1"
)


# ============================================================
# TESTE DE CONEXÃO
# ============================================================

st.markdown("---")

st.subheader(
    "🔌 1. Teste de conexão com o Google"
)

if st.button(
    "🔎 TESTAR CONEXÃO COM GOOGLE SHEETS",
    type="primary",
    use_container_width=True
):

    try:

        st.write(
            "⏳ Autenticando..."
        )

        client = get_google_client()

        st.success(
            "✅ Autenticação Google realizada."
        )

        st.write(
            "⏳ Abrindo a planilha..."
        )

        spreadsheet = client.open_by_key(
            SHEET_ID
        )

        st.success(
            f"✅ Planilha encontrada: "
            f"**{spreadsheet.title}**"
        )

        st.write(
            "### Abas encontradas:"
        )

        abas = spreadsheet.worksheets()

        for aba in abas:

            st.write(
                f"- `{aba.title}`"
            )

        # ----------------------------------------------------
        # ABRE PÁGINA1 EXPLICITAMENTE
        # ----------------------------------------------------

        try:

            sheet = spreadsheet.worksheet(
                "Página1"
            )

            st.success(
                "✅ A aba **Página1** foi encontrada."
            )

        except Exception as e:

            st.error(
                "❌ Não consegui encontrar "
                "a aba Página1."
            )

            st.exception(e)

            st.stop()

        # ----------------------------------------------------
        # INFORMAÇÕES DA ABA
        # ----------------------------------------------------

        st.write(
            "### Informações da aba"
        )

        st.write(
            f"Nome: **{sheet.title}**"
        )

        st.write(
            f"Linhas: **{sheet.row_count}**"
        )

        st.write(
            f"Colunas: **{sheet.col_count}**"
        )

        # ----------------------------------------------------
        # TESTE DE LEITURA
        # ----------------------------------------------------

        st.write(
            "### Teste de leitura"
        )

        valores = sheet.get_all_values()

        st.success(
            f"✅ Leitura funcionando. "
            f"Foram encontradas "
            f"**{len(valores)} linhas**."
        )

        if valores:

            st.write(
                "Primeira linha da planilha:"
            )

            st.code(
                str(valores[0])
            )

        # ----------------------------------------------------
        # TESTE DE ESCRITA
        # ----------------------------------------------------

        st.write(
            "### Teste de escrita"
        )

        st.warning(
            "O botão abaixo vai adicionar "
            "uma linha de TESTE na Página1."
        )

        if st.button(
            "🧪 ESCREVER LINHA DE TESTE",
            type="secondary",
            use_container_width=True,
            key="teste_escrita"
        ):

            try:

                agora = datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S"
                )

                linha_teste = [
                    "TESTE_STREAMLIT",
                    agora,
                    "CONEXÃO DE ESCRITA FUNCIONANDO"
                ]

                sheet.append_row(
                    linha_teste,
                    value_input_option="USER_ENTERED"
                )

                st.success(
                    "🎉 ESCRITA REALIZADA COM SUCESSO!"
                )

                st.info(
                    "Confira agora a aba "
                    "**Página1** no Google Sheets. "
                    "Deve ter aparecido uma nova linha."
                )

            except Exception as e:

                st.error(
                    "❌ A autenticação funciona, "
                    "mas a ESCRITA falhou."
                )

                st.exception(e)

    except Exception as e:

        st.error(
            "❌ NÃO FOI POSSÍVEL CONECTAR "
            "AO GOOGLE SHEETS."
        )

        st.exception(e)


# ============================================================
# TESTE MANUAL DE CADASTRO
# ============================================================

st.markdown("---")

st.subheader(
    "📝 2. Teste de novo cadastro"
)

st.info(
    "Este teste grava diretamente na Página1. "
    "Não depende do restante da Dashboard."
)

teste_matricula = st.text_input(
    "Matrícula de teste",
    key="teste_matricula"
)

teste_nome = st.text_input(
    "Nome de teste",
    key="teste_nome"
)

if st.button(
    "💾 GRAVAR CADASTRO DE TESTE",
    type="primary",
    use_container_width=True
):

    if not teste_matricula.strip():

        st.error(
            "Informe uma matrícula."
        )

        st.stop()

    if not teste_nome.strip():

        st.error(
            "Informe um nome."
        )

        st.stop()

    try:

        st.write(
            "⏳ Conectando..."
        )

        client = get_google_client()

        st.write(
            "⏳ Abrindo planilha..."
        )

        spreadsheet = client.open_by_key(
            SHEET_ID
        )

        st.write(
            f"✅ Planilha: "
            f"**{spreadsheet.title}**"
        )

        st.write(
            "⏳ Abrindo Página1..."
        )

        sheet = spreadsheet.worksheet(
            "Página1"
        )

        st.write(
            "✅ Página1 aberta."
        )

        # ----------------------------------------------------
        # CABEÇALHOS
        # ----------------------------------------------------

        headers = sheet.row_values(1)

        if not headers:

            st.error(
                "❌ Página1 não possui cabeçalho."
            )

            st.stop()

        st.write(
            f"✅ Encontradas "
            f"**{len(headers)} colunas**."
        )

        st.write(
            "Cabeçalhos:"
        )

        st.write(headers)

        # ----------------------------------------------------
        # MONTA LINHA
        # ----------------------------------------------------

        nova_linha = []

        for header in headers:

            header_limpo = str(
                header
            ).strip()

            if header_limpo == "Matrícula":

                valor = teste_matricula

            elif header_limpo == "Nome":

                valor = teste_nome

            else:

                valor = ""

            nova_linha.append(
                valor
            )

        st.write(
            "### Linha que será gravada"
        )

        st.write(
            nova_linha
        )

        # ----------------------------------------------------
        # GRAVA
        # ----------------------------------------------------

        st.write(
            "⏳ Gravando..."
        )

        sheet.append_row(
            nova_linha,
            value_input_option="USER_ENTERED"
        )

        st.success(
            "🎉 CADASTRO GRAVADO!"
        )

        st.write(
            f"Matrícula: **{teste_matricula}**"
        )

        st.write(
            f"Nome: **{teste_nome}**"
        )

        st.info(
            "Agora abra o Google Sheets e "
            "verifique a aba Página1."
        )

    except Exception as e:

        st.error(
            "❌ ERRO AO GRAVAR."
        )

        st.exception(e)


# ============================================================
# LEITURA ATUAL DA PLANILHA
# ============================================================

st.markdown("---")

st.subheader(
    "📋 3. Dados atuais da Página1"
)

if st.button(
    "🔄 LER PÁGINA1 AGORA",
    use_container_width=True
):

    try:

        client = get_google_client()

        spreadsheet = client.open_by_key(
            SHEET_ID
        )

        sheet = spreadsheet.worksheet(
            "Página1"
        )

        valores = sheet.get_all_values()

        if valores:

            df = pd.DataFrame(
                valores[1:],
                columns=valores[0]
            )

            st.success(
                f"✅ Página1 possui "
                f"{len(df)} registros."
            )

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.warning(
                "A Página1 está vazia."
            )

    except Exception as e:

        st.error(
            "❌ Erro ao ler Página1."
        )

        st.exception(e)
