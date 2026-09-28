# continuação da montagem do dicionário de edição
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

                                # Prepara a linha ordenada conforme o cabeçalho original
                                linha_atualizada = [
                                    str(novos_dados_map.get(col_h, "")) for col_h in headers
                                ]

                                # Atualiza o intervalo da linha correspondente na planilha
                                range_nome = f"A{row_idx}:{chr(64 + len(headers))}{row_idx}"
                                sheet.update(range_nome, [linha_atualizada])

                                st.success(
                                    f"✅ Registro do militar **{e_nome}** atualizado com sucesso!"
                                )
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(
                                    f"❌ Matrícula {matricula_editar} não encontrada no Google Sheets."
                                )

                        except Exception as err_edit:
                            st.error(f"❌ Erro ao atualizar registro no Google Sheets: {err_edit}")
        else:
            st.info(
                "As colunas 'Matrícula' e 'Nome' são necessárias para utilizar o seletor de edição."
            )

    # ==============================================================================
    # 5. FILTROS E EXIBIÇÃO DA TABELA DE DADOS
    # ==============================================================================
    st.subheader("📊 Consulta e Filtragem de Dados")

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        busca_nome = st.text_input("🔍 Buscar por Nome ou Nome de Guerra:")
        if busca_nome and "Nome" in df.columns:
            df_filtrado = df_filtrado[
                df_filtrado["Nome"].str.contains(busca_nome, case=False, na=False)
                | df_filtrado["Nome de Guerra"].str.contains(
                    busca_nome, case=False, na=False
                )
            ]

    with col_f2:
        if "OME" in df.columns:
            omes_disponiveis = ["Todas"] + sorted(
                [str(x) for x in df["OME"].unique() if str(x) != "-"]
            )
            ome_selecionada = st.selectbox("🏢 Filtrar por OME:", omes_disponiveis)
            if ome_selecionada != "Todas":
                df_filtrado = df_filtrado[df_filtrado["OME"] == ome_selecionada]

    with col_f3:
        if "Posto/ Grad" in df.columns:
            postos_disponiveis = ["Todos"] + sorted(
                [str(x) for x in df["Posto/ Grad"].unique() if str(x) != "-"]
            )
            posto_selecionado = st.selectbox(
                "🎖️ Filtrar por Posto/Graduação:", postos_disponiveis
            )
            if posto_selecionado != "Todos":
                df_filtrado = df_filtrado[
                    df_filtrado["Posto/ Grad"] == posto_selecionado
                ]

    # Exibição de métricas rápidas
    m1, m2 = st.columns(2)
    m1.metric("Total de Militares Cadastrados", len(df))
    m2.metric("Registros Exibidos no Filtro", len(df_filtrado))

    # Tabela com dataframe filtrado
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

except Exception as err_main:
    st.error(f"❌ Erro crítico ao carregar a aplicação: {err_main}")
