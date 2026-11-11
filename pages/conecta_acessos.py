import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dados import obter_dataframes_acessos, carregar_dados_acessos_bq

# Carrega os dados (com cache)
df_acessos = carregar_dados_acessos_bq()

st.header("Acessos às páginas do Conecta Recife", divider="gray")

st.markdown("""
    <style>

    /* Remove as bordas e contornos do botão do popover */
    button[data-testid="stPopoverButton"] {
        border: none !important;       /* Remove a bordas padrões */
    }

    /* Changes all popover trigger buttons to purple */
    button[data-testid="stPopoverButton"] {
        background-color: #f0f2f6 !important;
        color: #4b4d58 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. FORMULÁRIO DE FILTROS
# ---------------------------------------------------------

lista_orgaos = [orgao for orgao in df_acessos['orgao_nome'].unique() if isinstance(orgao, str) and orgao.strip() != '']
lista_anos = sorted([ano for ano in df_acessos['ano'].unique()])

with st.form("filtros_acessos_form"):
    col1, col2, col3, col4, col5 = st.columns([2, 2, 4, 1.5, 1.5], vertical_alignment="bottom")
    
    with col1:
        st.markdown("Tipo do órgão") 
        orgao_tipo = st.selectbox("Tipo do órgão", ["Todos", "Prefeitura", "Externo"], label_visibility="collapsed")
    with col2:
        st.markdown("Nome do órgão") 
        with st.popover("Selecionar", width='stretch'):
            orgaos_selecionados = [o for o in lista_orgaos if st.checkbox(o, key=f"orgao_{o}")]
    with col3:
        st.markdown("Pesquisa por nome")
        pesquisa = st.text_input(label="Pesquisa por nome", placeholder="Procurar", label_visibility="collapsed")
    with col4:
        st.markdown("Ano") 
        with st.popover("Selecionar", width='stretch'):
            anos_selecionados = [a for a in lista_anos if st.checkbox(a, key=f"ano_{a}")]
    with col5:
        st.markdown("Mês") 
        with st.popover("Selecionar", width='stretch'):
            meses_lista = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            meses_selecionados = [m for m in meses_lista if st.checkbox(m, key=f"mes_{m}")]
            
    col_submit, col_clear = st.columns([8, 1])
    with col_submit:
        submit_button = st.form_submit_button(label="Aplicar Filtros")

# Lógica de filtragem local
if submit_button:
    mask_acessos = pd.Series(True, index=df_acessos.index)
    
    if orgao_tipo != "Todos":
        mask_acessos &= (df_acessos['orgao_tipo'] == orgao_tipo)
        
    if orgaos_selecionados:
        mask_acessos &= df_acessos['orgao_nome'].isin(orgaos_selecionados)
        
    if pesquisa.strip():
        mask_acessos &= df_acessos['nome'].str.contains(pesquisa.strip(), case=False, na=False)
        
    if anos_selecionados:
        mask_acessos &= df_acessos['ano'].isin(anos_selecionados)
    
    # Nova lógica para múltiplos Meses
    if meses_selecionados:
        meses_map = {"Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4, "Mai": 5, "Jun": 6, 
                     "Jul": 7, "Ago": 8, "Set": 9, "Out": 10, "Nov": 11, "Dez": 12}
        meses_int = [meses_map[m] for m in meses_selecionados]
        mask_acessos &= df_acessos['mes'].isin(meses_int)
        
    df_acessos_filtrado = df_acessos[mask_acessos]

    df_acessos = df_acessos_filtrado

# ---------------------------------------------------------
# 3. CONSTRUÇÃO DOS GRÁFICOS
# ---------------------------------------------------------

df_pizza, df_mes, df_tabela, df_forma = obter_dataframes_acessos(df_acessos)

# --- LINHA SUPERIOR DE VISUALIZAÇÕES (Com Molduras) ---
col_graf1, col_graf2 = st.columns([1, 2.5])

with col_graf1:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center; color: #555;'>Proporção App x Web</h6>", unsafe_allow_html=True)
        # Gráfico de Pizza (Proporção App/Web)
        fig_pizza = px.pie(
            df_pizza, 
            values='quantidade', 
            names='web_ou_app', 
            hole=0, 
            color='web_ou_app',
            color_discrete_map={'app': '#E36B15', 'web': '#0A4B95'}
        )
        fig_pizza.update_traces(textinfo='label+percent', textposition='inside')
        fig_pizza.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=230)
        st.plotly_chart(fig_pizza, width='stretch')

with col_graf2:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center; color: #555;'>Total acessos por mês</h6>", unsafe_allow_html=True)
        # Gráfico de Barras Empilhadas
        fig_mes = go.Figure(data=[
            go.Bar(name='App', x=df_mes['Mês'], y=df_mes['App'], marker_color='#E36B15'),
            go.Bar(name='Web', x=df_mes['Mês'], y=df_mes['Web'], marker_color='#0A4B95')
        ])
        fig_mes.update_layout(
            barmode='stack', 
            margin=dict(t=10, b=20, l=10, r=10), 
            height=230,
            showlegend=False,
            xaxis=dict(title="2026")
        )
        st.plotly_chart(fig_mes, width='stretch')

# --- ÁREA INFERIOR (Tabela e Forma de Acesso) (Com Molduras) ---
col_tab, col_forma = st.columns([2.5, 1])

with col_tab:
    with st.container(border=True):
        abas = st.tabs(["Todos", "Serviço", "Programa", "Evento"])
        
        with abas[1]:
            # Divide o topo da aba em duas colunas: título (esquerda) e seletor (direita)
            col_titulo, col_seletor = st.columns([4, 1])
            
            with col_titulo:
                st.markdown("###### Serviços mais acessados")

            #""" VERSÃO COM SELETOR ÓRGÃO/OBJETO 
            with col_seletor:
                # O label_visibility="collapsed" esconde o rótulo do radio para economizar espaço
                visao_selecionada = st.radio(
                    "Visão", 
                    options=["Órgão", "Objeto"], 
                    label_visibility="collapsed"
                )
            
            # Condicional que renderiza a tabela com base na seleção do radio button
            if visao_selecionada == "Órgão":
                st.dataframe(
                    df_tabela, 
                    column_config={
                        "nome": st.column_config.TextColumn("Serviço", width="large"),
                        "orgao_sigla": st.column_config.TextColumn("Órgão", width="small"),
                        "total_acessos": st.column_config.NumberColumn("Total Acessos"),
                        "WEB": st.column_config.NumberColumn("WEB"),
                        "APP": st.column_config.NumberColumn("APP")
                    },
                    width='stretch', # 'use_container_width' substitui o 'width="stretch"' nas versões mais recentes
                    hide_index=True
                )
            else:
                st.dataframe(
                    df_tabela, 
                    column_config={
                        "nome": st.column_config.TextColumn("Serviço", width="large"),
                        "orgao_sigla": st.column_config.TextColumn("Órgão", width="small"),
                        "total_acessos": st.column_config.NumberColumn("Total Acessos", format="%d"),
                        "WEB": st.column_config.NumberColumn("WEB", format="%d"),
                        "APP": st.column_config.NumberColumn("APP", format="%d")
                    },
                    width='stretch',
                    hide_index=True
                )

                # 3. Totais do rodapé
                tot_acessos = f"{df_tabela['total_acessos'].sum():,}".replace(',', '.')
                tot_web = f"{df_tabela['WEB'].sum():,}".replace(',', '.')
                tot_app = f"{df_tabela['APP'].sum():,}".replace(',', '.')
                    
                st.markdown(f"**TOTAL**  →  Total Acessos: **{tot_acessos}** | WEB: **{tot_web}** | APP: **{tot_app}**")
            #"""  
    
            # # 4. Exibição no Streamlit
            # st.dataframe(
            #     df_tabela, 
            #     column_config={
            #         "nome": st.column_config.TextColumn("Serviço", width="large"),
            #         "orgao_sigla": st.column_config.TextColumn("Órgão", width="small"),
            #         "total_acessos": st.column_config.NumberColumn("Total Acessos", format="%d"),
            #         "WEB": st.column_config.NumberColumn("WEB", format="%d"),
            #         "APP": st.column_config.NumberColumn("APP", format="%d")
            #     },
            #     width='stretch',
            #     hide_index=True
            # )
            # # 3. Totais do rodapé
            # tot_acessos = f"{df_tabela['total_acessos'].sum():,}".replace(',', '.')
            # tot_web = f"{df_tabela['WEB'].sum():,}".replace(',', '.')
            # tot_app = f"{df_tabela['APP'].sum():,}".replace(',', '.')
                
            # st.markdown(f"**TOTAL**  →  Total Acessos: **{tot_acessos}** | WEB: **{tot_web}** | APP: **{tot_app}**")
            
with col_forma:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center; color: #555;'>Forma de acesso</h6>", unsafe_allow_html=True)
        
        # Ordena para manter a sequência original (Serviço, Destaque, Categoria, Trilha, Blank)
        df_forma_sorted = df_forma.iloc[::-1].copy()
        
        fig_forma = go.Figure()
        
        # Barra Laranja (App)
        fig_forma.add_trace(go.Bar(
            name='App',
            y=df_forma_sorted['Forma'],
            x=df_forma_sorted['Acessos_App'],
            orientation='h',
            marker_color='#E36B15',
            width=0.35
        ))
        
        # Barra Azul (Web)
        fig_forma.add_trace(go.Bar(
            name='Web',
            y=df_forma_sorted['Forma'],
            x=df_forma_sorted['Acessos_Web'],
            orientation='h',
            marker_color='#0A4B95',
            width=0.35
        ))
        
        # Adiciona o nome da categoria ACIMA da barra e o total acumulado À DIREITA
        for _, row in df_forma_sorted.iterrows():
            total_acessos = row['Acessos_App'] + row['Acessos_Web']
            total_formatado = f"{total_acessos:,}".replace(',', '.')
            
            # Texto da categoria (em cima da barra)
            fig_forma.add_annotation(
                x=0,
                y=row['Forma'],
                text=f"<b>{row['Forma']}</b>",
                showarrow=False,
                xanchor='left',
                yanchor='bottom',
                yshift=10,
                font=dict(size=12, color='black')
            )
            
            # Valor total (à direita da barra empilhada)
            fig_forma.add_annotation(
                x=total_acessos,
                y=row['Forma'],
                text=f" {total_formatado}",
                showarrow=False,
                xanchor='left',
                yanchor='middle',
                font=dict(size=11, color='black')
            )

        fig_forma.update_layout(
            barmode='stack',
            xaxis_visible=False,
            yaxis_visible=False,
            margin=dict(t=20, b=10, l=10, r=60), # r=60 para dar espaço ao texto do total à direita
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_forma, width='stretch')