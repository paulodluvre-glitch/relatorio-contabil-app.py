import streamlit as st

# --- A REGRA DE OURO: ISSO AQUI TEM QUE SER A PRIMEIRA COISA ---
st.set_page_config(page_title="Gerador de Relatórios Contábeis", layout="wide")

import pandas as pd
import numpy as np
import io
import re
from datetime import datetime

# ==============================================================================
# ESTILOS CSS
# ==============================================================================
st.markdown("""
<style>
    .main-header {font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;}
    .sub-header {font-size: 18px; font-weight: bold; color: #16a085; margin-top: 20px;}
    .stButton>button {width: 100%; background-color: #f0f2f6; font-weight: bold;}
    .box {background:#e8f6f3; padding:15px; margin:10px 0; border-radius: 5px; border-left: 5px solid #16a085;}
    
    /* Estilos das Metas e Status */
    .status-box {padding: 12px; margin-bottom: 8px; border-radius: 4px; border: 1px solid #ccc; font-size: 0.95em;}
    
    .status-atual {background-color: #d4edda; color: #155724; border-color: #c3e6cb;} /* Verde - No Prazo */
    .status-atraso {background-color: #fff3cd; color: #856404; border-color: #ffeeba;} /* Amarelo - Atrasado */
    .status-anterior {background-color: #e2e3e5; color: #383d41; border-color: #d6d8db;} /* Cinza/Azul - Competência Antiga */
    .status-pendente {background-color: #f8d7da; color: #721c24; border-color: #f5c6cb;} /* Vermelho - Pendente */
    .status-info {background-color: #fdfdfe; color: #818182; border-color: #fdfdfe;} /* Neutro */

    small {color: #555; font-weight: normal; font-style: italic;}
    h3 {margin-top: 20px; margin-bottom: 10px; color: #2c3e50; border-left: 5px solid #2c3e50; padding-left: 10px;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CONFIGURAÇÕES GERAIS
# ==============================================================================

MAPA_MESES = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def limpar_e_converter_dados_colados(texto_dados):
    if not texto_dados: return []
    try:
        texto_limpo = texto_dados.replace('%', '').replace('\n', ' ').strip()
        partes = texto_limpo.split()
        valores = []
        for p in partes:
            valor_float = float(p.replace(',', '.'))
            if valor_float > 1.0: valor_float = valor_float / 100.0
            valores.append(valor_float)
        return valores
    except:
        return []

def ordenar_colunas_meses(colunas):
    def get_date_key(col_name):
        try:
            parts = str(col_name).split('/')
            if len(parts) == 2:
                mes_nome = parts[0].strip().lower()
                ano = int(parts[1])
                mes_num = MAPA_MESES.get(mes_nome, 0)
                return pd.Timestamp(year=ano, month=mes_num, day=1)
        except: return pd.Timestamp.max
        return pd.Timestamp.max
    return sorted(colunas, key=get_date_key)

def parse_comp(c):
    try:
        parts = c.split('/')
        m_nome = parts[0].lower()
        ano = int(parts[1])
        return ano, MAPA_MESES.get(m_nome, 0)
    except: return 9999, 99

def format_pct(x):
    if pd.isna(x) or x == "": return "-"
    if isinstance(x, str): return x
    try: return f"{int(float(x) * 100)}%"
    except: return x

def carregar_arquivos_iniciais(uploaded_files):
    lista_dfs = []
    for file in uploaded_files:
        try:
            lista_dfs.append(pd.read_excel(file))
        except: pass
    return lista_dfs

# ==============================================================================
# PÁGINA 1: GERAR BASE
# ==============================================================================
def page_gerar_base():
    st.markdown('<div class="main-header">1. Gerar Base de Dados Consolidada</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Selecione os arquivos Excel (.xlsx)", accept_multiple_files=True, type=['xlsx', 'xls'])

    col1, col2 = st.columns(2)
    with col1:
        label_semana_atual = st.text_input("Rótulo Semana Atual (ex: 12.01 A 18.01)", "12.01 A 18.01")
        label_semana_passada = st.text_input("Rótulo Semana Passada (ex: 05.01 A 11.01)", "05.01 A 11.01")
    with col2:
        dados_excel_colados = st.text_area("Cole as porcentagens (Semana Anterior)", height=100)

    dfs_pre_carregados = []
    responsaveis_selecionados = []
    
    if uploaded_files:
        with st.spinner("Lendo arquivos..."):
            dfs_pre_carregados = carregar_arquivos_iniciais(uploaded_files)
            if dfs_pre_carregados:
                df_temp_nomes = pd.concat(dfs_pre_carregados, ignore_index=True)
                if 'Responsável' in df_temp_nomes.columns:
                    lista_dinamica = sorted(df_temp_nomes['Responsável'].dropna().astype(str).str.strip().unique())
                    st.success(f"Detectados {len(lista_dinamica)} responsáveis.")
                    responsaveis_selecionados = st.multiselect("Filtrar Responsáveis", options=lista_dinamica, default=lista_dinamica)

    if st.button("Processar Base", type="primary"):
        if not dfs_pre_carregados:
            st.error("Nenhum arquivo válido.")
            return
        
        try:
            df_final = pd.concat(dfs_pre_carregados, ignore_index=True)
            if responsaveis_selecionados:
                lista_norm = [x.strip().lower() for x in responsaveis_selecionados]
                df_final = df_final[df_final['Responsável'].astype(str).str.strip().str.lower().isin(lista_norm)]
            
            if 'Competência' in df_final.columns: df_final['Mês_competência'] = df_final['Competência']
            df_final['Tarefa Concluída'] = df_final['Status'].astype(str).str.strip().str.upper().apply(lambda x: 1 if x in ['CONCLUIDO', 'DESCONSIDERADO'] else 0)
            df_final['total de tarefas'] = 1
            
            grupos = df_final.groupby(['Responsável', 'Mês_competência'])
            df_final['Total de tarefas por competencia e colaborador'] = grupos['total de tarefas'].transform('sum')
            df_final['Total de tarefas concluídas por competencia e colaborador'] = grupos['Tarefa Concluída'].transform('sum')
            df_final['Percentual de tarefas concluidas por competencia e colaborador'] = (
                df_final['Total de tarefas concluídas por competencia e colaborador'] / 
                df_final['Total de tarefas por competencia e colaborador']
            )
            
            df_quadro = df_final.pivot_table(index='Responsável', columns='Mês_competência', values='Percentual de tarefas concluidas por competencia e colaborador', aggfunc='mean')
            colunas_meses = ordenar_colunas_meses(df_quadro.columns.tolist())
            df_quadro = df_quadro[colunas_meses].reset_index()
            
            valores_passada = limpar_e_converter_dados_colados(dados_excel_colados)
            linha_atual = {'Responsável': f"Total mensal ({label_semana_atual})"}
            linha_passada = {'Responsável': f"Total mensal - Semana passada ({label_semana_passada})"}
            linha_cresc = {'Responsável': "Crescimento em pontos percentuais (p.p)"}
            
            for i, mes in enumerate(colunas_meses):
                mask = df_final['Mês_competência'] == mes
                t = df_final.loc[mask, 'total de tarefas'].sum() if mask.any() else 0
                c = df_final.loc[mask, 'Tarefa Concluída'].sum() if mask.any() else 0
                linha_atual[mes] = c/t if t>0 else 0
                
                val_passado = valores_passada[i] if i < len(valores_passada) else 0.0
                linha_passada[mes] = val_passado
                linha_cresc[mes] = linha_atual[mes] - val_passado
            
            rows = pd.DataFrame([linha_atual, linha_passada, linha_cresc])
            df_quadro = pd.concat([df_quadro, rows], ignore_index=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_final.to_excel(writer, sheet_name='Contabil atualizado', index=False)
                df_quadro.to_excel(writer, sheet_name='Quadro Mensal', index=False)
            
            st.success("Base Gerada!")
            st.download_button("📥 Baixar BASE_DE_DADOS_PARA_IA.xlsx", output.getvalue(), "BASE_DE_DADOS_PARA_IA.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e: st.error(f"Erro: {e}")

# ==============================================================================
# PÁGINA 2: RELATÓRIO DESEMPENHO (4 CATEGORIAS: PRAZO, ATRASO, ANTERIOR, PENDENTE)
# ==============================================================================
def page_relatorio_desempenho():
    st.markdown('<div class="main-header">2. Relatório de Desempenho</div>', unsafe_allow_html=True)
    base_file = st.file_uploader("Upload da Base (Gerada na etapa 1)", type=['xlsx'], key='base1')
    
    st.markdown("### Arquivo de Metas")
    st.info("Pode subir o Excel ou o CSV.")
    metas_file = st.file_uploader("Upload Arquivo de Metas (.xlsx, .xls, .csv)", type=['xlsx', 'xls', 'csv'])
    
    col1, col2 = st.columns(2)
    d_inicio = col1.date_input("Início Período", datetime.now())
    d_fim = col2.date_input("Fim Período", datetime.now())

    lista_filtro_html = []
    
    if base_file:
        try:
            df_temp = pd.read_excel(base_file, sheet_name='Quadro Mensal')
            mask_lixo = df_temp['Responsável'].astype(str).str.contains("Total|Crescimento", case=False, na=False)
            nomes_base = sorted(df_temp[~mask_lixo]['Responsável'].dropna().unique())
            st.info(f"Colaboradores encontrados na base: {len(nomes_base)}")
            lista_filtro_html = st.multiselect("Quem deve aparecer no relatório HTML?", options=nomes_base, default=nomes_base)
        except: pass

    if st.button("Gerar HTML Desempenho", type="primary"):
        if not base_file: return
        try:
            # 1. PROCESSAR ARQUIVO DE METAS
            df_metas = pd.DataFrame()
            tem_metas = False
            col_resp = None
            col_emp = None
            col_data = None
            col_obs = None

            if metas_file:
                try:
                    if metas_file.name.endswith('.csv'):
                        df_metas = pd.read_csv(metas_file, sep=None, engine='python')
                    else:
                        df_metas = pd.read_excel(metas_file)
                    
                    df_metas.columns = [c.strip() for c in df_metas.columns]
                    cols_lower = {c.lower(): c for c in df_metas.columns}
                    
                    col_resp = cols_lower.get(next((c for c in cols_lower if 'respons' in c), None))
                    col_emp = cols_lower.get(next((c for c in cols_lower if 'empresa' in c or 'cliente' in c), None))
                    col_data = cols_lower.get(next((c for c in cols_lower if 'data' in c or 'meta' in c), None))
                    col_obs = cols_lower.get(next((c for c in cols_lower if 'observ' in c), None))
                    
                    if col_resp and col_emp:
                        df_metas[col_resp] = df_metas[col_resp].astype(str).str.strip().str.lower()
                        df_metas[col_emp] = df_metas[col_emp].astype(str).str.strip().str.lower()
                        tem_metas = True
                    else:
                        st.warning("Não encontrei as colunas 'Responsável' e 'Empresa' no arquivo de metas.")

                except Exception as e:
                    st.error(f"Erro ao ler arquivo de metas: {e}")

            # 2. QUADRO MENSAL E IDENTIFICAÇÃO DA ÚLTIMA COMPETÊNCIA
            df_q = pd.read_excel(base_file, sheet_name='Quadro Mensal')
            cols_comp = [c for c in df_q.columns if '/' in str(c)]
            
            # Ordena as competências cronologicamente
            cols_comp_ordenadas = ordenar_colunas_meses(cols_comp)
            ultima_competencia = cols_comp_ordenadas[-1] if cols_comp_ordenadas else None
            ultima_competencia_norm = str(ultima_competencia).strip().lower()

            mask_tot = df_q['Responsável'].astype(str).str.contains("Total mensal", case=False, na=False)
            mask_diff = df_q['Responsável'].astype(str).str.contains("Crescimento", case=False, na=False)
            
            df_colabs = df_q[~mask_tot & ~mask_diff].copy()
            if lista_filtro_html:
                df_colabs = df_colabs[df_colabs['Responsável'].isin(lista_filtro_html)]
            
            df_colabs['Responsável'] = df_colabs['Responsável'].astype(str).str.title()
            df_colabs = df_colabs.sort_values('Responsável')
            
            rows_tot = df_q[mask_tot].copy()
            if not rows_tot.empty:
                rows_tot['Responsável'] = ["STATUS POR MÊS", "SEMANA ANTERIOR"][:len(rows_tot)]
            
            df_final = pd.concat([df_colabs, rows_tot], ignore_index=True)
            df_final = df_final[['Responsável'] + cols_comp]
            
            for c in cols_comp: df_final[c] = df_final[c].apply(format_pct)
            html_table = df_final.to_html(index=False, classes='table', border=0, escape=False)
            
            insight = ""
            if mask_diff.any():
                row_g = df_q[mask_diff].iloc[0]
                melhoras = [f"<b>{c.split('/')[0]}</b> (+{int(row_g[c]*100)} p.p.)" for c in cols_comp if pd.notna(row_g[c]) and row_g[c] > 0]
                if melhoras: 
                    txt_m = ", ".join(melhoras[:-1]) + " e " + melhoras[-1] if len(melhoras) > 1 else melhoras[0]
                    insight = f"<div class='box'><strong>Insight:</strong> Melhoras em: {txt_m}</div>"
            
            # 3. DETALHAMENTO COM 4 CATEGORIAS
            df_c = pd.read_excel(base_file, sheet_name='Contabil atualizado')
            df_c['Data de Conclusão'] = pd.to_datetime(df_c['Data de Conclusão'], errors='coerce')
            
            # Filtra tarefas CONCLUÍDAS no PERÍODO
            mask_t = (df_c['Status'].astype(str).str.upper() == 'CONCLUIDO') & \
                     (df_c['Data de Conclusão'] >= pd.Timestamp(d_inicio)) & \
                     (df_c['Data de Conclusão'] <= pd.Timestamp(d_fim))
            
            if lista_filtro_html:
                mask_t = mask_t & df_c['Responsável'].isin(lista_filtro_html)

            df_tasks = df_c[mask_t].copy()
            
            html_tasks = ""
            colabs_tasks = sorted(list(set(df_tasks['Responsável'].dropna().unique()) | set(lista_filtro_html)))
            colabs_tasks = [c for c in colabs_tasks if str(c) != 'nan']

            for colab in colabs_tasks:
                nome_formatado = str(colab).title()
                sub = df_tasks[df_tasks['Responsável'] == colab].copy()
                
                # --- PREPARA METAS DO COLABORADOR ---
                dict_metas_dates = {} # {empresa: data_meta_timestamp}
                
                if tem_metas:
                    minhas_metas = df_metas[df_metas[col_resp] == str(colab).lower().strip()].copy()
                    
                    if not minhas_metas.empty and col_data:
                        minhas_metas[col_data] = pd.to_datetime(minhas_metas[col_data], errors='coerce')
                        # Filtra meta dentro do range
                        mask_p = (minhas_metas[col_data] >= pd.Timestamp(d_inicio)) & \
                                 (minhas_metas[col_data] <= pd.Timestamp(d_fim))
                        minhas_metas = minhas_metas[mask_p]

                    if not minhas_metas.empty:
                        for idx, row in minhas_metas.iterrows():
                            e_nome = str(row[col_emp]).strip().lower()
                            # Guarda info completa
                            dt_meta_ts = row[col_data] if col_data and pd.notna(row[col_data]) else None
                            obs = str(row[col_obs]) if col_obs and pd.notna(row[col_obs]) else ""
                            
                            dict_metas_dates[e_nome] = {
                                'dt_obj': dt_meta_ts, 
                                'obs': obs
                            }
                
                # --- CLASSIFICAÇÃO DAS ENTREGAS ---
                lista_concluidas_prazo = []
                lista_concluidas_atraso = []
                lista_concluidas_anteriores = []
                lista_pendentes = []

                # A. Processar o que foi FEITO
                # Agrupar por empresa para evitar repetição se entregou 2 competencias da mesma
                if not sub.empty:
                    # Vamos iterar por linha para ter precisão na data de conclusão
                    tarefas_agrupadas = {} # {empresa: [lista_de_infos_das_entregas]}
                    
                    for idx, row in sub.iterrows():
                        emp = str(row['Cliente']).strip().lower()
                        comp = str(row['Mês_competência']).strip().lower()
                        dt_conclusao = row['Data de Conclusão']
                        
                        if emp not in tarefas_agrupadas: tarefas_agrupadas[emp] = []
                        tarefas_agrupadas[emp].append({'comp': comp, 'dt_conc': dt_conclusao})
                    
                    empresas_feitas_nomes = sorted(list(tarefas_agrupadas.keys()))

                    for emp in empresas_feitas_nomes:
                        entregas = tarefas_agrupadas[emp]
                        
                        # Verifica se alguma entrega é da competencia atual
                        is_atual = False
                        comps_str = []
                        max_dt_conclusao_atual = None # Para comparar atraso
                        
                        for ent in entregas:
                            c_dt = parse_comp(ent['comp'])
                            ult_dt = parse_comp(ultima_competencia_norm)
                            
                            nm_display = ent['comp'].title()
                            
                            if c_dt == ult_dt:
                                is_atual = True
                                comps_str.append(f"<b>{nm_display}</b>")
                                # Pega a data de conclusao dessa competencia especifica
                                max_dt_conclusao_atual = ent['dt_conc']
                            else:
                                comps_str.append(nm_display)
                        
                        txt_emp = f"{emp.upper()} <small>({', '.join(comps_str)})</small>"
                        
                        if is_atual:
                            # Agora decide se é PRAZO ou ATRASO
                            # Busca meta
                            meta_info = dict_metas_dates.get(emp)
                            
                            is_atrasado = False
                            if meta_info and meta_info['dt_obj'] and max_dt_conclusao_atual:
                                # Se concluiu DEPOIS da meta -> Atraso
                                if max_dt_conclusao_atual > meta_info['dt_obj']:
                                    is_atrasado = True
                                    # Adiciona info do atraso
                                    dt_meta_str = meta_info['dt_obj'].strftime('%d/%m')
                                    dt_conc_str = max_dt_conclusao_atual.strftime('%d/%m')
                                    txt_emp += f" <small style='color:#a71d2a'>(Entregue: {dt_conc_str} | Meta: {dt_meta_str})</small>"

                            if is_atrasado:
                                lista_concluidas_atraso.append(txt_emp)
                            else:
                                lista_concluidas_prazo.append(txt_emp)
                        else:
                            lista_concluidas_anteriores.append(txt_emp)

                # B. Processar PENDENTES (que estão na meta mas não foram feitas)
                empresas_meta_nomes = list(dict_metas_dates.keys())
                # Lista de nomes que foram feitos (independente da competencia, se fez, não ta pendente)
                # OBS: A regra pode ser rigorosa: "se fez competencia antiga mas nao a atual, ta pendente a atual?"
                # Por enquanto, vou considerar: se o nome da empresa apareceu nas tarefas concluidas, não é pendente total.
                # Se quiser rigoroso (tem meta mas entregou só competencia velha), mudamos. 
                # Vou manter a logica: Se entregou algo, ta na lista de cima. Se não entregou NADA, ta pendente.
                
                feitas_flat = [str(cl).strip().lower() for cl in sub['Cliente'].unique()]
                
                pendentes_nomes = [e for e in empresas_meta_nomes if e not in feitas_flat]
                
                for p in pendentes_nomes:
                    info = dict_metas_dates.get(p, {})
                    txt = p.upper()
                    extras = []
                    if info.get('dt_obj'): extras.append(f"Meta: {info['dt_obj'].strftime('%d/%m')}")
                    if info.get('obs'): extras.append(f"{info['obs']}")
                    if extras: txt += f" <small>({', '.join(extras)})</small>"
                    lista_pendentes.append(txt)

                # --- MONTAGEM DO HTML ---
                blocos = []
                
                # 1. Verde: Prazo
                if lista_concluidas_prazo:
                    blocos.append(f"<div class='status-box status-atual'>✅ <b>Concluídas (No Prazo):</b><br>" + "<br>".join(lista_concluidas_prazo) + "</div>")
                
                # 2. Amarelo: Atraso
                if lista_concluidas_atraso:
                    blocos.append(f"<div class='status-box status-atraso'>⚠️ <b>Concluídas (Com Atraso):</b><br>" + "<br>".join(lista_concluidas_atraso) + "</div>")

                # 3. Azul: Anterior
                if lista_concluidas_anteriores:
                    blocos.append(f"<div class='status-box status-anterior'>☑️ <b>Concluídas (Competências Anteriores):</b><br>" + "<br>".join(lista_concluidas_anteriores) + "</div>")

                # 4. Vermelho: Pendente
                if lista_pendentes:
                    blocos.append(f"<div class='status-box status-pendente'>❌ <b>Pendentes no Período:</b><br>" + "<br>".join(lista_pendentes) + "</div>")
                
                # Mensagem de Sucesso Total (Se tinha metas, não tem pendencia e entregou algo atual)
                if tem_metas and not lista_pendentes and (lista_concluidas_prazo or lista_concluidas_atraso):
                    if not lista_concluidas_atraso: # Só parabeniza se não teve atraso tb
                         blocos.append("<div class='status-box status-atual'>🌟 <b>Todas as metas do período foram atingidas no prazo!</b></div>")

                if not blocos:
                     blocos.append("<div class='status-box status-info'>Sem atividades registradas ou metas para este período.</div>")

                # Tabela
                if not sub.empty:
                    sub = sub[['Cliente', 'Mês_competência', 'Data de Conclusão']]
                    sub['Data de Conclusão'] = sub['Data de Conclusão'].dt.strftime('%d/%m/%Y')
                    sub['_sort'] = sub['Mês_competência'].apply(parse_comp)
                    sub = sub.sort_values(['_sort', 'Cliente']).drop(columns=['_sort'])
                    tabela_html = sub.to_html(index=False, classes='table')
                else:
                    tabela_html = ""

                html_tasks += f"<h3>{nome_formatado}</h3>{''.join(blocos)}{tabela_html}<br><hr>"
            
            css = """<style>
            body{font-family:sans-serif;margin:20px; color:#333} 
            table{width:100%;border-collapse:collapse; margin-top:10px; margin-bottom:20px} 
            td,th{border:1px solid #ddd;padding:8px;text-align:center; font-size: 0.85em} 
            th{background-color:#f8f9fa}
            td:first-child{text-align:left; font-weight:bold; color:#2c3e50}
            .box{background:#e8f6f3;padding:15px;margin:10px 0;border:1px solid #16a085; border-radius:4px} 
            
            .status-box {padding: 12px; margin-bottom: 8px; border-radius: 4px; border: 1px solid #ccc; font-size: 0.95em;}
            .status-atual {background-color: #d4edda; color: #155724; border-color: #c3e6cb;}
            .status-atraso {background-color: #fff3cd; color: #856404; border-color: #ffeeba;}
            .status-anterior {background-color: #e2e3e5; color: #383d41; border-color: #d6d8db;}
            .status-pendente {background-color: #f8d7da; color: #721c24; border-color: #f5c6cb;}
            .status-info {background-color: #fff3cd; color: #856404; border-color: #ffeeba;}
            
            small {color: #555; font-weight: normal;}
            h3 {margin-top: 20px; margin-bottom: 10px; color: #2c3e50; border-left: 5px solid #2c3e50; padding-left: 10px;}
            </style>"""
            
            final_html = f"""<html><head><meta charset='utf-8'>{css}</head><body>
            <h1>Relatório Desempenho ({d_inicio.strftime('%d/%m')} a {d_fim.strftime('%d/%m')})</h1>
            <h2>1. Visão Geral</h2>
            {html_table} {insight} <hr> 
            <h2>2. Detalhamento de Entregas e Metas</h2>
            {html_tasks}</body></html>"""
            
            st.success("Relatório HTML Gerado!")
            st.download_button("📥 Baixar Relatório HTML", final_html, f"Relatorio_Desempenho_{d_inicio.strftime('%d-%m')}.html", mime="text/html")
        except Exception as e: st.error(f"Erro: {e}")

# ==============================================================================
# PÁGINA 3: RELATÓRIO STATUS
# ==============================================================================
def page_relatorio_status():
    st.markdown('<div class="main-header">3. Relatório Status (Dono Atual)</div>', unsafe_allow_html=True)
    base_file = st.file_uploader("Upload da Base", type=['xlsx'], key='base2')
    
    colabs_alvo = []
    
    if base_file:
        try:
            df_preview = pd.read_excel(base_file, sheet_name='Contabil atualizado')
            df_preview.columns = [c.strip() for c in df_preview.columns]
            
            if 'Cliente' in df_preview.columns and 'Responsável' in df_preview.columns:
                lista_donos = sorted(df_preview['Responsável'].dropna().astype(str).str.strip().unique())
                st.info(f"Colaboradores encontrados: {len(lista_donos)}")
                colabs_alvo = st.multiselect("Selecione os Colaboradores", options=lista_donos, default=lista_donos)
        except Exception as e:
            st.warning(f"Erro ao ler lista de nomes: {e}")

    if st.button("Gerar HTML Status", type="primary"):
        if not base_file: return
        try:
            df = pd.read_excel(base_file, sheet_name='Contabil atualizado')
            df.columns = [c.strip() for c in df.columns]
            df = df[['Cliente', 'Responsável', 'Mês_competência', 'Data de Conclusão']].copy()
            df['Responsável'] = df['Responsável'].str.strip()
            df['Data de Conclusão'] = pd.to_datetime(df['Data de Conclusão'], errors='coerce')

            def conv_data(x):
                try: 
                    pts = str(x).replace('-','/').split('/')
                    return datetime(int(pts[1]), MAPA_MESES.get(pts[0].lower().strip(),0), 1)
                except: return None
            
            df['Data_Sort'] = df['Mês_competência'].apply(conv_data)
            df.dropna(subset=['Data_Sort'], inplace=True)
            
            mapa_donos = df.sort_values(['Cliente', 'Data_Sort']).groupby('Cliente')['Responsável'].last().to_dict()
            df['Dono'] = df['Cliente'].map(mapa_donos)
            
            df_final = df.groupby(['Cliente','Mês_competência','Data_Sort','Dono'], as_index=False)['Data de Conclusão'].max()
            df_final['Icone'] = df_final['Data de Conclusão'].apply(lambda x: "✔" if pd.notna(x) else "✖")
            
            if colabs_alvo: 
                df_final = df_final[df_final['Dono'].isin(colabs_alvo)]
            
            css = """<style>
            body{font-family:sans-serif; margin:20px} 
            table{border-collapse:collapse;width:100%; font-size:11px; margin-bottom:20px} 
            td,th{border:1px solid #ccc;padding:4px;text-align:center} 
            th{background:#f0f0f0} 
            td:first-child{text-align:left;font-weight:bold;width:200px}
            h2{border-bottom:2px solid #eee; margin-top:20px}
            </style>"""
            
            html = f"<html><head><meta charset='utf-8'>{css}</head><body><h1>Relatório Status (Dono Atual)</h1>"
            
            meses_unicos = df_final[['Mês_competência','Data_Sort']].drop_duplicates().sort_values('Data_Sort')
            meses = meses_unicos['Mês_competência'].tolist()
            
            for dono in sorted(df_final['Dono'].unique()):
                piv = df_final[df_final['Dono']==dono].pivot_table(index='Cliente', columns='Mês_competência', values='Icone', aggfunc='first')
                cols = [m for m in meses if m in piv.columns]
                if not cols: continue
                html += f"<h2>{dono} ({len(piv)} Empresas)</h2><table><thead><tr><th>Empresa</th>" + "".join([f"<th>{m}</th>" for m in cols]) + "</tr></thead><tbody>"
                for cli, row in piv[cols].fillna('-').iterrows():
                    html += f"<tr><td>{cli}</td>" + "".join([f"<td style='color:{'green' if x=='✔' else 'red'}; background-color:{'#fff' if x=='✔' else '#fff0f0'}'>{x}</td>" for x in row]) + "</tr>"
                html += "</tbody></table>"
            
            html += "</body></html>"
            st.success("Relatório de Status Gerado!")
            st.download_button("📥 Baixar Relatório Status", html, "Relatorio_Status.html", mime="text/html")
            
        except Exception as e: st.error(f"Erro: {e}")

# ==============================================================================
# NAVEGAÇÃO
# ==============================================================================
st.sidebar.title("Menu")
paginas = {
    "1. Gerar Base de Dados": page_gerar_base,
    "2. Relatório Desempenho": page_relatorio_desempenho,
    "3. Relatório Status": page_relatorio_status
}
escolha = st.sidebar.radio("Ir para:", list(paginas.keys()))
paginas[escolha]()