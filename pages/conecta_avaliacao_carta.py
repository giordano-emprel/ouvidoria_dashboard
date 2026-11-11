import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dados import carregar_dados_avaliacao_carta

# Carrega os dados (com cache)
df_pizza, df_mes, df_tabela, df_tags_neg, df_tags_pos = carregar_dados_avaliacao_carta()

st.header("Avaliação da Carta de Serviços", divider="gray")

# CSS para remover as bordas dos expanders e ajustar o visual
st.markdown(
    """
    <style>
    [data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
        
        # Ordena os dados (Plotly renderiza de baixo para cima)
        df_neg_sorted = df_tags_neg.sort_values('Quantidade', ascending=True)
        
        fig_neg = go.Figure()
        fig_neg.add_trace(go.Bar(
            x=df_neg_sorted['Quantidade'],
            y=df_neg_sorted['Tag'],
            orientation='h',
            # Formata os números no padrão brasileiro (14.680)
            text=df_neg_sorted['Quantidade'].apply(lambda x: f'{x:,}'.replace(',', '.')),
            textposition='inside',
            insidetextanchor='end',
            marker_color='#CC1C00', # Vermelho mais fiel à imagem
            width=0.4 # Define uma grossura menor para a barra
        ))
        
        # Adiciona o nome da tag logo acima de cada barra
        for _, row in df_neg_sorted.iterrows():
            fig_neg.add_annotation(
                x=0,
                y=row['Tag'],
                text=f"<b>{row['Tag']}</b>",
                showarrow=False,
                xanchor='left',
                yanchor='bottom',
                yshift=12, # Desloca o texto para ficar exatamente em cima
                font=dict(size=12, color='black')
            )

        fig_neg.update_layout(
            xaxis_visible=False, 
            yaxis_visible=False, # Oculta o eixo Y padrão ao lado
            margin=dict(t=20, b=0, l=10, r=10), 
            height=300,
            plot_bgcolor='rgba(0,0,0,0)' # Fundo transparente
        )
        st.plotly_chart(fig_neg, width='stretch')

with col_inf2:
    with st.container(border=True):
        st.markdown("<h6 style='text-align: center;'>Tags positivas</h6>", unsafe_allow_html=True)
        
        df_pos_sorted = df_tags_pos.sort_values('Quantidade', ascending=True)
        
        fig_pos = go.Figure()
        fig_pos.add_trace(go.Bar(
            x=df_pos_sorted['Quantidade'],
            y=df_pos_sorted['Tag'],
            orientation='h',
            text=df_pos_sorted['Quantidade'].apply(lambda x: f'{x:,}'.replace(',', '.')),
            textposition='inside',
            insidetextanchor='end',
            marker_color='#0A4B95', # Azul mais fiel à imagem
            width=0.4 
        ))
        
        for _, row in df_pos_sorted.iterrows():
            fig_pos.add_annotation(
                x=0,
                y=row['Tag'],
                text=f"<b>{row['Tag']}</b>",
                showarrow=False,
                xanchor='left',
                yanchor='bottom',
                yshift=12, 
                font=dict(size=12, color='black')
            )

        fig_pos.update_layout(
            xaxis_visible=False, 
            yaxis_visible=False, 
            margin=dict(t=20, b=0, l=10, r=10), 
            height=300,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pos, width='stretch')


# CSS para reduzir o espaço vertical entre os elementos do Streamlit
st.markdown(
    """
    <style>
        /* Reduz o espaçamento padrão (gap) entre elementos dentro de containers */
        [data-testid="stVerticalBlock"] {
            gap: 0.1rem !important;
        }

        [data-testid="stExpander"] {
            border: none !important;
            box-shadow: none !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# st.markdown(
#     """
#     <style>
#     [data-testid="stExpander"] {
#         border: none !important;
#         box-shadow: none !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

df_comentarios = pd.DataFrame(
    [
        {
            "servico": (
                "Acessar o CNH Recife - Inscrições, Consultas e Recursos"
            ),
            "comentario": "Comentário sobre a CNH Recife...",
            "nota": 5.0,
        },
        {
            "servico": (
                "Acessar meus registros de saúde (Minha Saúde Conectada)"
            ),
            "comentario": "Péssimo!",
            "nota": 1.0,
        },
        {
            "servico": "Acessar meu cartão do SUS",
            "comentario": "Só agradecer 🙏",
            "nota": 5.0,
        },
        {
            "servico": (
                "Acessar extrato de débitos e emitir guias para pagamento do"
                " CIM de autônomo"
            ),
            "comentario": "Muito prático",
            "nota": 4.5,
        },
    ]
)

with col_inf3:
    with st.container(border=True):
        col_h1, col_h2 = st.columns([4, 1])
        col_h1.markdown("**Comentários por serviço**")
        col_h2.markdown("**Nota média**")

        # Linha do cabeçalho com margem bem pequena
        st.markdown(
            "<hr style='margin: 4px 0 8px 0; border: none; border-top: 1px solid"
            " #ddd;' />",
            unsafe_allow_html=True,
        )

        with st.container(height=300):
            if not df_comentarios.empty:
                for servico, grupo in df_comentarios.groupby("servico"):
                    media = grupo["nota"].mean()

                    c_exp, c_nota = st.columns([4, 1])
                    with c_exp:
                        with st.expander(servico, expanded=False):
                            for _, linha in grupo.iterrows():
                                st.write(
                                    f"• {linha['comentario']} ({linha['nota']:.2f})"
                                )
                    with c_nota:
                        st.write(f"**{media:.2f}**".replace(".", ","))

                    # Linha divisória customizada (ajuste os pixels de 'margin' se quiser mais perto/distante)
                    st.markdown(
                        "<hr style='border: none; border-top: 1px solid #ccc; margin-top: 0px;"
                        " margin-bottom: 15.5px;' />",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Nenhum comentário encontrado.")