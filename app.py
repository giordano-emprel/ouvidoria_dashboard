import streamlit as st

st.set_page_config(page_title="Dashboard Conecta Recife", layout="wide")

# Mapeamento das páginas para seus respectivos arquivos
paginas = {
    "Acessos": "pages/conecta_acessos.py",
    "Avaliação da Carta": "pages/conecta_avaliacao_carta.py",
    "Avaliação do Serviço": "pages/conecta_avaliacao_servico.py",
}

# Configuração da barra lateral para navegação
st.sidebar.title("Navegação")
selecao = st.sidebar.radio("CONECTA:", list(paginas.keys()))

# Executa o arquivo da página selecionada
with open(paginas[selecao], encoding="utf-8") as f:
    code = compile(f.read(), paginas[selecao], 'exec')
    exec(code, globals())