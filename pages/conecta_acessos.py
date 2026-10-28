import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dados import carregar_dados_acessos

# Carrega os dados (com cache)
df_pizza, df_mes, df_tabela, df_forma = carregar_dados_acessos()

st.header("Acessos às páginas do Conecta Recife", divider="gray")

# --- ÁREA DE FILTROS (Com Moldura) ---

with st.form("filtros_acessos_form"):
    col1, col2, col3, col4, col5 = st.columns([2, 2, 4, 1, 1])
    
    with col1:
        orgao_ext_int = st.selectbox("Órgão", ["All", "Interno", "Externo"])
    with col2:
        orgao = st.selectbox("Órgão", ["All"] + list(df_tabela['Órgão']))
    with col3:
        pesquisa = st.text_input("Pesquisa pela descrição", placeholder="Search")
    with col4:
        ano = st.selectbox("Ano", ["2026", "2025"])
    with col5:
        mes = st.selectbox("Mês", ["All", "Jan", "Fev", "Mar"])
        
    col_submit, col_clear = st.columns([8, 1])
    with col_submit:
        submit_button = st.form_submit_button(label="Aplicar Filtros")

# Lógica de filtragem local
if submit_button:
    if orgao != "All":
        df_tabela = df_tabela[df_tabela['Órgão'] == orgao]

# --- LINHA SUPERIOR DE VISUALIZAÇÕES (Com Molduras) ---
col_graf1, col_graf2 = st.columns([1, 2.5])

with col_graf1:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center; color: #555;'>Proporção App x Web</h6>", unsafe_allow_html=True)
        # Gráfico de Pizza (Proporção App/Web)
        fig_pizza = px.pie(
            df_pizza, 
            values='Acessos', 
            names='Origem', 
            hole=0, 
            color='Origem',
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
        abas = st.tabs(["SERVIÇO", "PROGRAMA", "EVENTO"])
        
        with abas[0]:
            st.markdown("###### Serviços mais acessados")
            st.dataframe(
                df_tabela, 
                column_config={
                    "Órgão": st.column_config.TextColumn("Órgão", width="large"),
                    "Total Acessos": st.column_config.NumberColumn("Total Acessos"),
                    "WEB": st.column_config.NumberColumn("WEB"),
                    "APP": st.column_config.NumberColumn("APP")
                },
                width='stretch', 
                hide_index=True
            )
            st.markdown("**TOTAL:** Total Acessos: **14,402,524** | WEB: **1,904,432** | APP: **12,495,326**")

with col_forma:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center; color: #555;'>Forma de acesso</h6>", unsafe_allow_html=True)
        # Gráfico de Barras Horizontais
        fig_forma = go.Figure(data=[
             go.Bar(name='App', y=df_forma['Forma'], x=df_forma['Acessos_App'], orientation='h', marker_color='#E36B15'),
             go.Bar(name='Web', y=df_forma['Forma'], x=df_forma['Acessos_Web'], orientation='h', marker_color='#0A4B95')
        ])
        fig_forma.update_layout(
            barmode='stack', 
            margin=dict(t=10, b=10, l=10, r=10), 
            height=300,
            showlegend=False
        )
        fig_forma.update_yaxes(autorange="reversed") 
        st.plotly_chart(fig_forma, width='stretch')