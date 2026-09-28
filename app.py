import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(
    page_title="Teste Google Sheets",
    layout="wide"
)

st.title("🧪 Teste de Gravação no Google Sheets")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def conectar():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    return client


st.write("### 1. Testando conexão")

if st.button(
    "🔌 TESTAR CONEXÃO",
    type="primary"
):

    try:

        client = conectar()

        st.success(
            "✅ Autenticação com Google realizada."
        )

        sheet_id = st.secrets["SHEET_ID"]

        st.write(
            "SHEET_ID encontrado."
        )

        spreadsheet = client.open_by_key(
            sheet_id
        )

        st.success(
            f"✅ Planilha aberta: "
            f"**{spreadsheet.title}**"
        )

        worksheets = spreadsheet.worksheets()

        st.write(
            "Abas encontradas:"
        )

        for ws in worksheets:

            st.write(
                f"- {ws.title}"
            )


        sheet = spreadsheet.sheet1

        st.success(
            f"✅ Primeira aba: "
            f"**{sheet.title}**"
        )


        headers = sheet.row_values(1)

        st.write(
            "Cabeçalhos encontrados:"
        )

        st.write(headers)


        st.write("---")

        st.write(
            "### 2. Testando ESCRITA"
        )


        ultima_linha = len(
            sheet.get_all_values()
        ) + 1


        horario = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )


        dados_teste = [
            "TESTE_DASHBOARD",
            horario,
            "GRAVAÇÃO FUNCIONANDO"
        ]


        st.write(
            f"Linha que será utilizada: "
            f"**{ultima_linha}**"
        )

        st.write(
            "Dados:"
        )

        st.write(
            dados_teste
        )


        # ----------------------------------------------------
        # ESCRITA DIRETA
        # ----------------------------------------------------

        sheet.update(
            f"A{ultima_linha}:C{ultima_linha}",
            [dados_teste],
            value_input_option="USER_ENTERED"
        )


        st.success(
            "✅ COMANDO DE ESCRITA EXECUTADO."
        )


        # ----------------------------------------------------
        # LEITURA IMEDIATA
        # ----------------------------------------------------

        linha_lida = sheet.row_values(
            ultima_linha
        )


        st.write(
            "### 3. Resultado da leitura"
        )

        st.write(
            linha_lida
        )


        if (
            len(linha_lida) >= 3
            and linha_lida[0]
            == "TESTE_DASHBOARD"
        ):

            st.success(
                "🎉 FUNCIONOU!"
            )

            st.success(
                "O Dashboard CONSEGUE escrever "
                "na sua planilha Google."
            )

        else:

            st.error(
                "❌ A escrita foi chamada, "
                "mas a leitura não encontrou "
                "os dados esperados."
            )


    except Exception as erro:

        st.error(
            "❌ A GRAVAÇÃO FALHOU."
        )

        st.exception(erro)
