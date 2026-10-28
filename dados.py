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
# 2. Funções de Carga de Dados
# ---------------------------------------------------------

@st.cache_data
def carregar_dados_avaliacao_carta_bq():
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

@st.cache_data
def carregar_dados_acessos():
    """Simula a carga de dados de acessos com cache para eficiência."""
    # Dados para o gráfico de pizza (Proporção App/Web)
    dados_pizza = pd.DataFrame({
        'Origem': ['app', 'web'],
        'Acessos': [87, 13]
    })

    # Dados para o gráfico de barras empilhadas (Acessos por mês)
    dados_mes = pd.DataFrame({
        'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'],
        'App': [1610466, 1537614, 1561591, 1555307, 1321622, 1202491, 1296594, 1182020, 1043188, 50000],
        'Web': [200000, 180000, 190000, 185000, 150000, 140000, 160000, 130000, 110000, 5000]
    })
    
    # Dados para a tabela principal (Serviços mais acessados)
    dados_tabela = pd.DataFrame({
        'Órgão': [
            'Secretaria de Assistência Social e Combate à Fome',
            'Secretaria de Saúde',
            'Secretaria de Esportes',
            'Controladoria-Geral do Município',
            'Secretaria de Trabalho e Qualificação Profissional'
        ],
        'Total Acessos': [2704564, 2483106, 2249450, 1974668, 1071784],
        'WEB': [362524, 211060, 100142, 7165, 63007],
        'APP': [2342040, 2272046, 2149308, 1967503, 1008777]
    })

    # Dados para o gráfico de barras horizontais (Forma de acesso)
    dados_forma = pd.DataFrame({
        'Forma': ['Serviço', 'Destaque', 'Categoria', 'Trilha', '(Blank)'],
        'Acessos_App': [8825639, 2672910, 2525694, 378027, 254],
        'Acessos_Web': [1000000, 500000, 400000, 50000, 10]
    })

    return dados_pizza, dados_mes, dados_tabela, dados_forma

