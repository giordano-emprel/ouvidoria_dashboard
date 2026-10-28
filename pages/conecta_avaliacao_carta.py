import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dados import carregar_dados_avaliacao_carta

# Carrega os dados (com cache)
df_pizza, df_mes, df_tabela, df_tags_neg, df_tags_pos = carregar_dados_avaliacao_carta()

st.header("Avaliação da Carta de Serviços", divider="gray")

# --- ÁREA DE FILTROS (Com Moldura) ---

with st.form("filtros_carta_form"):
    col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 1, 1])
    
    with col1:
        orgao_ext_int = st.selectbox("Órgão", ["All", "Interno", "Externo"])
    with col2:
        orgao = st.selectbox("Órgão", ["All"] + list(df_tabela['ÓRGÃO']))
    with col3:
        objeto = st.selectbox("Objeto", ["All"])
    with col4:
        ano = st.selectbox("Ano", ["2026", "2025"])
    with col5:
        mes = st.selectbox("Mês", ["All", "Jan", "Fev", "Mar"])
        
    col_submit, col_clear = st.columns([8, 1])
    with col_submit:
        submit_button = st.form_submit_button(label="Aplicar Filtros")

if submit_button:
    if orgao != "All":
        df_tabela = df_tabela[df_tabela['ÓRGÃO'] == orgao]

# --- LINHA SUPERIOR DE VISUALIZAÇÕES (Com Molduras) ---
col_sup1, col_sup2 = st.columns([1, 2.5])

with col_sup1:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center; color: #555;'>Avaliação Geral</h6>", unsafe_allow_html=True)
        # Gráfico de Pizza (Likes vs Dislikes)
        fig_pizza = px.pie(
            df_pizza, 
            values='Quantidade', 
            names='Avaliação', 
            hole=0, 
            color='Avaliação',
            color_discrete_map={'Like':'#1F77B4', 'Dislike':'#D62728'}
        )
        fig_pizza.update_traces(textinfo='label+value+percent', textposition='outside')
        fig_pizza.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=230)
        st.plotly_chart(fig_pizza, width='stretch')

with col_sup2:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center; color: #555;'>Total de avaliações por mês</h6>", unsafe_allow_html=True)
        # Gráfico combinado
        fig_mes = go.Figure()
        fig_mes.add_trace(go.Bar(x=df_mes['Mês'], y=df_mes['Dislike'], name='Dislike', marker_color='#D62728'))
        fig_mes.add_trace(go.Scatter(x=df_mes['Mês'], y=df_mes['Like'], name='Like', mode='lines+markers', line=dict(color='#1F77B4')))
        
        fig_mes.update_layout(
            barmode='group',
            margin=dict(t=10, b=20, l=10, r=10),
            height=230,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(title="2026")
        )
        st.plotly_chart(fig_mes, width='stretch')

# --- TABELA PRINCIPAL (Com Moldura) ---
with st.container(border=True):
    abas = st.tabs(["ÓRGÃO", "SERVIÇO", "CATEGORIA", "GRUPO", "PÚBLICO ALVO"])

    with abas[0]:
        df_exibicao = df_tabela.copy()
        
        st.dataframe(
            df_exibicao,
            column_config={
                "ÓRGÃO": st.column_config.TextColumn("ÓRGÃO", width="large"),
                "Dislike": st.column_config.NumberColumn("👎 Dislike"),
                "Like": st.column_config.NumberColumn("👍 Like"),
                "% Dislike": st.column_config.TextColumn("% Dislike"),
                "Total": st.column_config.NumberColumn("Total")
            },
            width='stretch',
            hide_index=True
        )
        
        st.markdown(f"**TOTAL:** Dislike: **73,506** | Like: **1,013** | % Dislike: **99%** | Total: **74,519**")

# --- LINHA INFERIOR (TAGS E COMENTÁRIOS) (Com Molduras) ---
col_inf1, col_inf2, col_inf3 = st.columns([1, 1, 2])

with col_inf1:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center;'>Tags negativas</h6>", unsafe_allow_html=True)
        fig_neg = px.bar(df_tags_neg, x='Quantidade', y='Tag', orientation='h', text='Quantidade')
        fig_neg.update_traces(marker_color='#D62728', textposition='inside')
        fig_neg.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_visible=False, margin=dict(t=0, b=0, l=0, r=0), height=280)
        st.plotly_chart(fig_neg, width='stretch')

with col_inf2:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center;'>Tags positivas</h6>", unsafe_allow_html=True)
        fig_pos = px.bar(df_tags_pos, x='Quantidade', y='Tag', orientation='h', text='Quantidade')
        fig_pos.update_traces(marker_color='#1F77B4', textposition='inside')
        fig_pos.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_visible=False, margin=dict(t=0, b=0, l=0, r=0), height=280)
        st.plotly_chart(fig_pos, width='stretch')

with col_inf3:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center;'>Comentários por serviço</h6>", unsafe_allow_html=True)
        
        with st.container(height=280):
            with st.expander("Acessar o CNH Recife - Inscrições, Consultas e Recursos", expanded=False):
                st.write("Comentário sobre a CNH Recife...")
                
            with st.expander("Acessar meus registros de saúde (Minha Saúde Conectada)", expanded=True):
                st.write("Péssimo!")
                
            with st.expander("Acessar meu cartão do SUS", expanded=True):
                st.write("Só agradecer 🙏")
                
            with st.expander("Acessar extrato de débitos e emitir guias para pagamento do CIM de autônomo", expanded=False):
                st.write("Sem comentários no momento.")
                
            with st.expander("Acessar extrato de débitos e emitir guias para pagamento das taxas de empresa", expanded=False):
                st.write("Sem comentários no momento.")