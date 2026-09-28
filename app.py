# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
try:

    SHEET_ID = st.secrets["SHEET_ID"]

    # ========================================================
    # MENSAGEM DE SUCESSO APÓS RECARREGAMENTO
    # ========================================================
    if "mensagem_sucesso_cadastro" in st.session_state:

        st.success(
            st.session_state["mensagem_sucesso_cadastro"]
        )

        del st.session_state["mensagem_sucesso_cadastro"]

    # ========================================================
    # CARREGAMENTO DOS DADOS
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

    # Controla se o cadastro deve permanecer aberto
    if "novo_cadastro_aberto" not in st.session_state:
        st.session_state["novo_cadastro_aberto"] = False

    if st.button(
        "➕ NOVO CADASTRO",
        use_container_width=True
    ):
        st.session_state["novo_cadastro_aberto"] = True

    with st.expander(
        "➕ **Novo Cadastro de Militar**",
        expanded=st.session_state["novo_cadastro_aberto"]
    ):

        st.info(
            "Preencha os dados abaixo e clique em "
            "**💾 SALVAR NOVO CADASTRO**."
        )

        # ====================================================
        # ABA 1 - IDENTIFICAÇÃO
        # ====================================================

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

                novo_num_funcional = st.text_input(
                    "nº Funcional:",
                    key="novo_num_funcional"
                )

                novo_matricula = st.text_input(
                    "Matrícula:",
                    key="novo_matricula"
                )

                novo_cpf_ponto = st.text_input(
                    "CPF.:",
                    key="novo_cpf_ponto"
                )

                novo_cpf = st.text_input(
                    "CPF:",
                    key="novo_cpf"
                )

                novo_num_ident = st.text_input(
                    "Nº IDENT.:",
                    key="novo_num_ident"
                )

            with c2:

                novo_nome = st.text_input(
                    "Nome:",
                    key="novo_nome"
                )

                novo_nome_guerra = st.text_input(
                    "Nome de Guerra:",
                    key="novo_nome_guerra"
                )

                novo_sexo = st.selectbox(
                    "SEXO:",
                    ["", "MASCULINO", "FEMININO"],
                    key="novo_sexo"
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
                    key="novo_raca"
                )

            with c3:

                novo_posto_grad = st.text_input(
                    "Posto/ Grad:",
                    key="novo_posto_grad"
                )

                novo_fones = st.text_input(
                    "Fones:",
                    key="novo_fones"
                )

                novo_ano_ingresso = st.text_input(
                    "Ano de ingresso:",
                    key="novo_ano_ingresso"
                )

                novo_data_praca = st.text_input(
                    "Data de praça:",
                    key="novo_data_praca"
                )

        # ====================================================
        # ABA 2 - LOTAÇÃO
        # ====================================================

        with tab_lotacao:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_ome = st.text_input(
                    "OME:",
                    key="novo_ome"
                )

                novo_ome_qod = st.text_input(
                    "OME QOD:",
                    key="novo_ome_qod"
                )

                novo_atividade = st.text_input(
                    "Atividade:",
                    key="novo_atividade"
                )

                novo_municipio = st.text_input(
                    "Município:",
                    key="novo_municipio"
                )

                novo_regiao = st.text_input(
                    "Região:",
                    key="novo_regiao"
                )

            with c2:

                novo_tempo_servico_anos = st.text_input(
                    "Tempo de serviço (anos):",
                    key="novo_tempo_servico_anos"
                )

                novo_tempo_servico_amd = st.text_input(
                    "Tempo de serviço (ano, mês, dias):",
                    key="novo_tempo_servico_amd"
                )

                novo_tempo_servico_dias = st.text_input(
                    "Tempo de serviço (dias):",
                    key="novo_tempo_servico_dias"
                )

                novo_tempo_obm_atual = st.text_input(
                    "Tempo na OBM atual:",
                    key="novo_tempo_obm_atual"
                )

            with c3:

                novo_data_ult_promocao = st.text_input(
                    "Data da última promoção ou Implant. PCNH:",
                    key="novo_data_ult_promocao"
                )

                novo_principio_ult_promocao = st.text_input(
                    "Princípio da última promoção:",
                    key="novo_principio_ult_promocao"
                )

                novo_tempo_posto_atual_dias = st.text_input(
                    "Tempo no Posto/Grad. atual EM DIAS:",
                    key="novo_tempo_posto_atual_dias"
                )

        # ====================================================
        # ABA 3 - CESSÃO
        # ====================================================

        with tab_cessao:

            c1, c2, c3 = st.columns(3)

            with c1:

                novo_data_mov_sp = st.text_input(
                    "Data da Movimentação em SP:",
                    key="novo_data_mov_sp"
                )

                novo_ome_anterior = st.text_input(
                    "OME ANTERIOR AO ÚLTIMO SP PUBLICADO:",
                    key="novo_ome_anterior"
                )

                novo_data_chegada = st.text_input(
                    "Data de chegada na OBM Anteior:",
                    key="novo_data_chegada"
                )

                novo_movimentado = st.text_input(
                    "Movimentado (apagar antes de atualizar o SP):",
                    key="novo_movimentado"
                )

            with c2:

                novo_orgao = st.text_input(
                    "ÓRGÃO:",
                    key="novo_orgao"
                )

                novo_poder = st.text_input(
                    "Poder:",
                    key="novo_poder"
                )

                novo_onus = st.selectbox(
                    "Ônus para Origem:",
                    ["", "SIM", "NÃO"],
                    key="novo_onus"
                )

                novo_inicio_cessao = st.text_input(
                    "Início da Cessão ou requisição:",
                    key="novo_inicio_cessao"
                )

            with c3:

                novo_renovacao = st.text_input(
                    "Renovação de cessão - Atos/Portarias/Documentos:",
                    key="novo_renovacao"
                )

                novo_doe = st.text_input(
                    "DOE/BGSDS de renovação:",
                    key="novo_doe"
                )

                novo_sei = st.text_input(
                    "SEI deslig.:",
                    key="novo_sei"
                )

        # ====================================================
        # ABA 4 - LTIP
        # ====================================================

        with tab_ltip:

            c1, c2 = st.columns(2)

            with c1:

                novo_afastamentos = st.text_area(
                    "Processo RR e AFASTAMENTOS SUP. A 90 DIAS "
                    "ININTERRUPTOS, PUBLICADOS EM SP:",
                    key="novo_afastamentos"
                )

                novo_inicio_ltip = st.text_input(
                    "INÍCIO DA LTIP:",
                    key="novo_inicio_ltip"
                )

                novo_termino_ltip = st.text_input(
                    "TÉRMINO DA LTIP (inserir data de apresentação):",
                    key="novo_termino_ltip"
                )

            with c2:

                novo_somatorio_anos = st.text_input(
                    "Somatório LTIP gozada em anos:",
                    key="novo_somatorio_anos"
                )

                novo_somatorio_amd = st.text_input(
                    "Somatório LTIP gozada em anos/meses/dias:",
                    key="novo_somatorio_amd"
                )

                novo_somatorio_dias = st.text_input(
                    "Somatório de todas LTIP gozadas em dias:",
                    key="novo_somatorio_dias"
                )

                novo_total_ltip = st.text_input(
                    "TOTAL DIAS EM LTIP no MESMO Posto/Grad.:",
                    key="novo_total_ltip"
                )

        # ====================================================
        # ABA 5 - DOCUMENTOS
        # ====================================================

        with tab_outros:

            c1, c2 = st.columns(2)

            with c1:

                novo_ato = st.text_input(
                    "Ato:",
                    key="novo_ato"
                )

                novo_doc_publicacao = st.text_input(
                    "Doc. Publicação:",
                    key="novo_doc_publicacao"
                )

                novo_sp_adicao = st.text_input(
                    "SP da Adição:",
                    key="novo_sp_adicao"
                )

                novo_processo_rr = st.text_input(
                    "Processo RR:",
                    key="novo_processo_rr"
                )

            with c2:

                novo_suplemento = st.text_input(
                    "Suplemento de Pessoal nº/Ano:",
                    key="novo_suplemento"
                )

                novo_data_suplemento = st.text_input(
                    "Data Suplemento de Pessoal:",
                    key="novo_data_suplemento"
                )

                novo_hoje = st.text_input(
                    "Hoje:",
                    key="novo_hoje"
                )

                novo_obs = st.text_area(
                    "OBS:",
                    key="novo_obs"
                )

        # ====================================================
        # MONTAGEM DOS DADOS
        # ====================================================

        novos_dados = {
            "nº Funcional": novo_num_funcional,
            "Matrícula": novo_matricula,
            "CPF.": novo_cpf_ponto,
            "CPF": novo_cpf,
            "Nº IDENT.": novo_num_ident,
            "Nome": novo_nome,
            "Nome de Guerra": novo_nome_guerra,
            "SEXO": novo_sexo,
            "Raça/Cor": novo_raca,
            "Posto/ Grad": novo_posto_grad,
            "Fones": novo_fones,
            "Ano de ingresso": novo_ano_ingresso,
            "Data de praça": novo_data_praca,
            "OME": novo_ome,
            "OME QOD": novo_ome_qod,
            "Atividade": novo_atividade,
            "Município": novo_municipio,
            "Região": novo_regiao,
            "Tempo de serviço (anos)": novo_tempo_servico_anos,
            "Tempo de serviço (ano, mês, dias)": novo_tempo_servico_amd,
            "Tempo de serviço (dias)": novo_tempo_servico_dias,
            "Tempo na OBM atual": novo_tempo_obm_atual,
            "Data da última promoção ou Implant. PCNH": novo_data_ult_promocao,
            "Princípio da última promoção": novo_principio_ult_promocao,
            "Tempo no Posto/Grad. atual EM DIAS": novo_tempo_posto_atual_dias,
            "Data da Movimentação em SP": novo_data_mov_sp,
            "OME ANTERIOR AO ÚLTIMO SP PUBLICADO": novo_ome_anterior,
            "Data de chegada na OBM Anteior": novo_data_chegada,
            "Movimentado (apagar antes de atualizar o SP)": novo_movimentado,
            "ÓRGÃO": novo_orgao,
            "Poder": novo_poder,
            "Ônus para Origem": novo_onus,
            "Início da Cessão ou requisição": novo_inicio_cessao,
            "Renovação de cessão - Atos/Portarias/Documentos": novo_renovacao,
            "DOE/BGSDS de renovação": novo_doe,
            "SEI deslig.": novo_sei,
            "Processo RR e AFASTAMENTOS SUP. A 90 DIAS ININTERRUPTOS, PUBLICADOS EM SP": novo_afastamentos,
            "INÍCIO DA LTIP": novo_inicio_ltip,
            "TÉRMINO DA LTIP (inserir data de apresentação)": novo_termino_ltip,
            "Somatório LTIP gozada em anos": novo_somatorio_anos,
            "Somatório LTIP gozada em anos/meses/dias": novo_somatorio_amd,
            "Somatório de todas LTIP gozadas em dias": novo_somatorio_dias,
            "TOTAL DIAS EM LTIP no MESMO Posto/Grad.": novo_total_ltip,
            "Ato": novo_ato,
            "Doc. Publicação": novo_doc_publicacao,
            "SP da Adição": novo_sp_adicao,
            "Processo RR": novo_processo_rr,
            "Suplemento de Pessoal nº/Ano": novo_suplemento,
            "Data Suplemento de Pessoal": novo_data_suplemento,
            "Hoje": novo_hoje,
            "OBS": novo_obs,
        }

        # ====================================================
        # BOTÃO SALVAR
        # ====================================================

        st.markdown("---")

        salvar_novo = st.button(
            "💾 SALVAR NOVO CADASTRO",
            type="primary",
            use_container_width=True,
            key="salvar_novo_cadastro"
        )

        if salvar_novo:

            try:

                # ============================================
                # VALIDAÇÃO
                # ============================================

                matricula_nova = str(
                    novos_dados.get("Matrícula", "")
                ).strip()

                nome_novo = str(
                    novos_dados.get("Nome", "")
                ).strip()

                if not matricula_nova:

                    st.error(
                        "❌ Informe a **Matrícula** antes de salvar."
                    )

                elif not nome_novo:

                    st.error(
                        "❌ Informe o **Nome** antes de salvar."
                    )

                else:

                    with st.spinner(
                        "💾 Salvando cadastro no Google Sheets..."
                    ):

                        # ====================================
                        # CONEXÃO
                        # ====================================

                        client = get_gspread_client()

                        spreadsheet = client.open_by_key(
                            SHEET_ID
                        )

                        sheet = spreadsheet.sheet1

                        # ====================================
                        # CABEÇALHOS
                        # ====================================

                        headers = sheet.row_values(1)

                        if not headers:

                            raise Exception(
                                "A primeira linha da planilha "
                                "não possui cabeçalhos."
                            )

                        # ====================================
                        # VERIFICA MATRÍCULA
                        # ====================================

                        if "Matrícula" not in headers:

                            raise Exception(
                                "A coluna 'Matrícula' não foi "
                                "encontrada na primeira linha "
                                "da planilha."
                            )

                        coluna_matricula = (
                            headers.index("Matrícula") + 1
                        )

                        valores_matricula = sheet.col_values(
                            coluna_matricula
                        )

                        matriculas_existentes = {
                            str(valor).strip()
                            for valor in valores_matricula[1:]
                            if str(valor).strip()
                        }

                        if matricula_nova in matriculas_existentes:

                            raise Exception(
                                f"A matrícula "
                                f"{matricula_nova} já existe "
                                f"na planilha."
                            )

                        # ====================================
                        # MONTA A LINHA
                        # ====================================

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

                        # ====================================
                        # GARANTE MESMA QUANTIDADE DE COLUNAS
                        # ====================================

                        if len(nova_linha) != len(headers):

                            raise Exception(
                                "Quantidade de dados diferente "
                                "da quantidade de colunas."
                            )

                        # ====================================
                        # GRAVA
                        # ====================================

                        sheet.append_row(
                            nova_linha,
                            value_input_option="USER_ENTERED"
                        )

                        # ====================================
                        # CONFIRMA DIRETAMENTE NA PLANILHA
                        # ====================================

                        valores_depois = sheet.col_values(
                            coluna_matricula
                        )

                        matriculas_depois = {
                            str(valor).strip()
                            for valor in valores_depois[1:]
                        }

                        if matricula_nova not in matriculas_depois:

                            raise Exception(
                                "O Google Sheets não confirmou "
                                "a gravação da matrícula."
                            )

                    # ========================================
                    # SALVAMENTO CONFIRMADO
                    # ========================================

                    st.session_state[
                        "mensagem_sucesso_cadastro"
                    ] = (
                        "🎉 **NOVO CADASTRO SALVO COM SUCESSO!**\n\n"
                        f"**Matrícula:** {matricula_nova}\n\n"
                        f"**Nome:** {nome_novo}"
                    )

                    # Fecha o formulário
                    st.session_state[
                        "novo_cadastro_aberto"
                    ] = False

                    # Limpa o cache
                    st.cache_data.clear()

                    # Recarrega a página
                    st.rerun()

            except Exception as erro:

                st.error(
                    "❌ **O cadastro NÃO foi salvo.**"
                )

                st.exception(erro)

    # ========================================================
    # 2. EDIÇÃO
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

                if not registros.empty:

                    dados_militar = (
                        registros.iloc[0].to_dict()
                    )

                    st.info(
                        f"Editando: **{dados_militar.get('Nome', '')}** "
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

                        dados_editados["Matrícula"] = (
                            matricula_editar
                        )

                        btn_atualizar = st.form_submit_button(
                            "🔄 ATUALIZAR REGISTRO",
                            use_container_width=True
                        )

                        if btn_atualizar:

                            try:

                                client = get_gspread_client()

                                sheet = (
                                    client
                                    .open_by_key(SHEET_ID)
                                    .sheet1
                                )

                                cell = sheet.find(
                                    matricula_editar
                                )

                                if not cell:

                                    st.error(
                                        "❌ Registro não localizado."
                                    )

                                else:

                                    row_idx = cell.row

                                    headers = (
                                        sheet.row_values(1)
                                    )

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
                                        f"A{row_idx}",
                                        [linha_atualizada],
                                        value_input_option="USER_ENTERED"
                                    )

                                    st.cache_data.clear()

                                    st.success(
                                        f"✅ Registro da matrícula "
                                        f"**{matricula_editar}** "
                                        f"atualizado com sucesso!"
                                    )

                                    st.rerun()

                            except Exception as erro:

                                st.error(
                                    "❌ Erro ao atualizar registro."
                                )

                                st.exception(erro)

        else:

            st.info(
                "As colunas 'Matrícula' e 'Nome' são "
                "necessárias para edição."
            )

    # ========================================================
    # 3. EXCLUSÃO
    # ========================================================

    with st.expander(
        "🗑️ **Excluir Registro da Planilha**",
        expanded=False
    ):

        st.warning(
            "⚠️ A exclusão removerá o registro "
            "diretamente do Google Sheets."
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
                    key="btn_excluir"
                )

                if btn_excluir:

                    try:

                        client = get_gspread_client()

                        sheet = (
                            client
                            .open_by_key(SHEET_ID)
                            .sheet1
                        )

                        cell = sheet.find(
                            matricula_alvo
                        )

                        if not cell:

                            st.error(
                                f"❌ Matrícula "
                                f"{matricula_alvo} não encontrada."
                            )

                        else:

                            sheet.delete_rows(
                                cell.row
                            )

                            st.cache_data.clear()

                            st.success(
                                f"✅ Registro da matrícula "
                                f"**{matricula_alvo}** "
                                f"excluído com sucesso!"
                            )

                            st.rerun()

                    except Exception as erro:

                        st.error(
                            "❌ Erro ao excluir registro."
                        )

                        st.exception(erro)

        else:

            st.info(
                "As colunas 'Matrícula' e 'Nome' são "
                "necessárias para exclusão."
            )


# ============================================================
# TRATAMENTO DE ERROS
# ============================================================

except KeyError as erro:

    st.error(
        "❌ Chave de segredo não encontrada "
        f"no secrets.toml: {erro}"
    )

except Exception as erro:

    st.error(
        "❌ Ocorreu um erro geral na aplicação."
    )

    st.exception(erro)
