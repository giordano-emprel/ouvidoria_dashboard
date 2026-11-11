import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

# ---------------------------------------------------------
# 1. Autenticação e Inicialização do Cliente BigQuery
# ---------------------------------------------------------

@st.cache_resource
def get_bigquery_client():
    # Carrega as credenciais a partir do secrets.toml
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )
    return client

client = get_bigquery_client()

# ---------------------------------------------------------
# 2. Função de Consulta com Cache
# ---------------------------------------------------------

@st.cache_data(ttl=3600)  # Mantém o resultado em cache por 1 hora
def run_query(query: str, params: dict = None) -> pd.DataFrame:
    job_config = bigquery.QueryJobConfig()
    
    if params:
        query_params = []
        for key, value in params.items():
            query_params.append(bigquery.ScalarQueryParameter(key, "STRING", value))
        job_config.query_parameters = query_params

    query_job = client.query(query, job_config=job_config)
    return query_job.to_dataframe()

# ---------------------------------------------------------
# 3. Funções de Carga de Dados
# ---------------------------------------------------------

@st.cache_data
def carregar_dados_acessos_bq():
    sql_query = """
        SELECT *
        FROM `cadastro-unico-pessoa.dashboard_ouvidoria.tb_acessos_agrupados`
    """
    with st.spinner("Carregando dados do BigQuery..."):
        df_acessos = run_query(sql_query)

    return df_acessos

@st.cache_data
def obter_dataframes_acessos(df: pd.DataFrame):

    ##### Dados para o gráfico de pizza (Proporção App/Web)
    dados_pizza = (
        df.groupby('web_ou_app', as_index=False)['quantidade'].sum()
    )

    ##### Dados para o gráfico de barras empilhadas (Acessos por mês)

    dados_mes = pd.DataFrame({
        'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'],
        'App': [1610466, 1537614, 1561591, 1555307, 1321622, 1202491, 1296594, 1182020, 1043188, 50000],
        'Web': [200000, 180000, 190000, 185000, 150000, 140000, 160000, 130000, 110000, 5000]
    })

    ##### Dados para a tabela de Serviços mais acessados
    
    df_tabela = (
        df.groupby(['nome', 'orgao_sigla', 'web_ou_app'])['quantidade']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    # Padroniza nomes das colunas geradas (WEB / APP)
    df_tabela.columns.name = None
    df_tabela = df_tabela.rename(columns=lambda x: str(x).upper() if str(x).lower() in ['web', 'app'] else x)

    # Defesa caso algum filtro zerar WEB ou APP
    for col in ['WEB', 'APP']:
        if col not in df_tabela.columns:
            df_tabela[col] = 0

    # 2. Totalizador e Ordenação
    df_tabela['total_acessos'] = df_tabela['WEB'] + df_tabela['APP']
    df_tabela = df_tabela[['nome', 'orgao_sigla', 'total_acessos', 'WEB', 'APP']].sort_values(by='total_acessos', ascending=False)


    ##### Dados para o gráfico de Forma de acesso
    
    dados_forma = pd.DataFrame({
        'Forma': ['Serviço', 'Destaque', 'Categoria', 'Trilha', '(Blank)'],
        'Acessos_App': [8825639, 2672910, 2525694, 378027, 254],
        'Acessos_Web': [1000000, 500000, 400000, 50000, 10]
    })

    return dados_pizza, dados_mes, df_tabela, dados_forma


@st.cache_data
def carregar_dados_avaliacao_carta():
    """Simula a carga de dados para a tela de Avaliação da Carta."""
    
    # Gráfico de Pizza (Likes vs Dislikes)
    dados_pizza = pd.DataFrame({
        'Avaliação': ['Like', 'Dislike'],
        'Quantidade': [1013, 73506],
        'Cor': ['#1F77B4', '#D62728'] # Azul e Vermelho
    })

    # Gráfico de linha/barras (Avaliações por mês)
    dados_mes = pd.DataFrame({
        'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'],
        'Like': [85, 58, 97, 70, 338, 58, 69, 159, 67, 12],
        'Dislike': [131, 107, 127, 98, 76, 50, 125, 84, 72689, 19]
    })
    
    # Tabela Principal (Hierarquia de Órgãos)
    dados_tabela = pd.DataFrame({
        'ÓRGÃO': [
            'Conviva Mercados e Feiras - Autarquia Municipal',
            'Procuradoria-Geral do Município',
            'Controladoria-Geral do Município',
            'Gabinete de Gerenciamento do ProMorar',
            'Secretaria da Mulher',
            'Secretaria de Desenvolvimento Econômico',
            'Secretaria de Direitos Humanos e Juventude',
            'Urbana - PE'
        ],
        'Dislike': [2, 1, 0, 0, 0, 0, 0, 0],
        'Like': [9, 1, 1, 2, 1, 2, 1, 1],
        '% Dislike': ['18%', '50%', '0%', '0%', '0%', '0%', '0%', '0%'],
        'Total': [11, 2, 1, 2, 1, 2, 1, 1]
    })

    # Tags Negativas
    dados_tags_neg = pd.DataFrame({
        'Tag': [
            '1 - Informação incompleta', 
            '2 - Clareza das informações', 
            '2 - Falta de objetividade', 
            '4 - Informação incorreta', 
            '5 - Linguagem utilizada'
        ],
        'Quantidade': [14680, 14667, 14667, 14631, 14561]
    })

    # Tags Positivas
    dados_tags_pos = pd.DataFrame({
        'Tag': [
            '1 - Clareza das informações',
            '2 - Passo a passo',
            '3 - Objetividade',
            '4 - Agrupamento das informações',
            '5 - Linguagem utilizada'
        ],
        'Quantidade': [195, 94, 86, 79, 26]
    })

    return dados_pizza, dados_mes, dados_tabela, dados_tags_neg, dados_tags_pos

