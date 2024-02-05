import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
from textblob import TextBlob
from newspaper import Article
import yfinance as yf
import plotly.express as px
import altair as alt

# ---------Funcoes------------
paginaUolBaixada = ""
def buscarMaioresVariacoes():
    global paginaUolBaixada
    url = "https://economia.uol.com.br/cotacoes/"
    response = requests.get(url)
    content = response.content
    site = BeautifulSoup(content, "html.parser")
    paginaUolBaixada = site
    infos = site.findAll("div", class_="ticker-slide")[0].find(class_="ipca")
    tables = site.findAll("table", class_="data-table")
    cont = 0
    contTitle = 0
    contAux = 0
    title = site.findAll("h3", class_="data-table no-gutter")
    jsonGeral = []
    for table in tables:
        if cont>=3 and cont<=5: 
            for tr in table.findAll("tr"):
                empresa = tr.findAll("td")[0].findAll("a")[0].contents[0]
                variacao = tr.findAll("td")[1].findAll("a")[0].contents[0]
                cotacao = tr.findAll("td")[2].findAll("a")[0].contents[0]
                linhaJson = {
                    "empresa": empresa,
                    "variacao": variacao,
                    "cotacao": cotacao,
                    "tipo": title[contTitle].text
                }
                contAux = contAux +1
                if contAux%len(table.findAll("tr")) == 0:
                    contTitle = contTitle + 1
                jsonGeral.append(linhaJson)
        cont = cont + 1
    df = pd.DataFrame(jsonGeral)
    return df

def percorreDfVariacoes(df, pos):
    for index, row in df.iterrows():
        if (pos == 1) and (row['tipo'] == "Maiores altas"):
            dados1 = str(row['empresa']) 
            dados2 = str(row['variacao'])
            dados3 = str(row['cotacao'])
            st.markdown(montaHtmlVariacoes(dados1, dados2, dados3), unsafe_allow_html=True)
            
        elif (pos == 2) and (row['tipo'] == "Maiores baixas"):
            dados1 = str(row['empresa']) 
            dados2 = str(row['variacao'])
            dados3 = str(row['cotacao'])
            st.markdown(montaHtmlVariacoes(dados1, dados2, dados3), unsafe_allow_html=True)
            
        elif (pos == 3) and (row['tipo'] == "Mais negociadas"):
            dados1 = str(row['empresa']) #+ "   → "
            dados2 = str(row['variacao'])
            dados3 = str(row['cotacao'])
            st.markdown(montaHtmlVariacoes(dados1, dados2, dados3), unsafe_allow_html=True)
            
def montaHtmlVariacoes(dados1, dados2, dados3):
    # Definindo a cor com base no valor de dados2
    seta = " → "
    cor_dados2 = 'green' if ("+" in dados2) else 'red'
    return f'<div style="display: flex;">' \
               f'<div style="font-weight: bold; color: #AAAAAA; margin-right: 20px;">{dados1}</div>' \
               f'<div style="font-weight: bold; color: #AAAAAA; margin-right: 15px;">{seta}</div>' \
               f'<div style="color: {cor_dados2}; font-weight: bold; margin-right: 15px;">{dados2}</div>' \
               f'<div style="color: #AAAAAA;">{dados3}</div>' \
               f'</div>'

def percorreDfIndicesEconomicos(df):
    for index, row in df.iterrows():
        dados1 = str(row['item1'])
        dados2 = str(row['item2'])
        dados3 = str(row['item3'])
        st.markdown(montaHtmlIndicesEconomicos(dados1, dados2, dados3), unsafe_allow_html=True)
        
def montaHtmlIndicesEconomicos(dados1, dados2, dados3):
    seta = " → "
    if (dados2 == " "):
        return f'<div style="display: flex;">' \
               f'<div style="font-weight: bold; color: #AAAAAA; margin-right: 10px;">{dados1}</div>' \
               f'<div style="font-weight: bold; color: #AAAAAA; margin-right: 10px;">{seta}</div>' \
               f'<div style="color: #AAAAAA;">{dados3}</div>' \
               f'</div>'
    else:
        cor_dados2 = 'green' if ('+' in dados2) else ('red' if ('-' in dados2) else '#AAAAAA')
        return f'<div style="display: flex;">' \
               f'<div style="font-weight: bold; color: #AAAAAA; margin-right: 10px;">{dados1}</div>' \
               f'<div style="font-weight: bold; color: #AAAAAA; margin-right: 10px;">{seta}</div>' \
               f'<div style="color: {cor_dados2}; font-weight: bold; margin-right: 10px;">{dados2}</div>' \
               f'<div style="color: #AAAAAA;">{dados3}</div>' \
               f'</div>'
        
def retornarAgricolas():
    global paginaUolBaixada
    tables = paginaUolBaixada.findAll("table", class_="data-table")
    df = padronizacao(tables = tables, indexTable = 9)
    return percorreDfIndicesEconomicos(df)
    
def retornarCommodities():
    global paginaUolBaixada
    tables = paginaUolBaixada.findAll("table", class_="data-table")
    df = padronizacao(tables = tables, indexTable = 8)
    return percorreDfIndicesEconomicos(df)

def retornarInflacao():
    global paginaUolBaixada
    tables = paginaUolBaixada.findAll("table", class_="data-table")
    df = padronizacao(tables = tables, indexTable = 7)
    return percorreDfIndicesEconomicos(df)

def retornarGerais():
    global paginaUolBaixada
    tables = paginaUolBaixada.findAll("table", class_="data-table")
    df = padronizacao(tables = tables, indexTable = 6)
    return percorreDfIndicesEconomicos(df)

def padronizacao(tables, indexTable):
    cont = 0
    linha = ""
    jsonGeral = []
    if indexTable == 9:
        for table in tables:
            if cont == indexTable:
                for tr in table.findAll("tr"):
                    try:
                        item1 = tr.findAll("td")[0].get_text().strip()
                        item2 = " "
                        item3 = tr.findAll("td")[1].get_text().strip()
                        linhaJson = {
                            "item1": item1,
                            "item2": item2,
                            "item3": item3,
                        }
                        jsonGeral.append(linhaJson)
                    except:
                        print("erro na linha de inflacao")
            cont = cont + 1
        df = pd.DataFrame(jsonGeral)
        df = df.iloc[1:]
        return df
    else:
        for table in tables:
            if cont == indexTable:
                for tr in table.findAll("tr"):
                    try:
                        item1 = tr.findAll("td")[0].get_text().strip()
                        item2 = tr.findAll("td")[1].get_text().strip()
                        item3 = tr.findAll("td")[2].get_text().strip()
                        linhaJson = {
                            "item1": item1,
                            "item2": item2,
                            "item3": item3,
                        }
                        jsonGeral.append(linhaJson)
                    except:
                        print("erro na linha de inflacao")
            cont = cont + 1
        df = pd.DataFrame(jsonGeral)
        df = df.iloc[1:]
        return df

def resumeNoticiaMl(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    analysis = TextBlob(article.text)
    polarity = analysis.polarity
    texto = ""
    texto = texto + str(article.summary) + "\n"
    texto = texto + "\nPolaridade: " + str(round(polarity, 3)) + " "
    if polarity > 0:
        texto = texto + "Sentimento: Positivo"
    elif polarity < 0:
        texto = texto + "Sentimento: Negativo"
    else:
        texto = texto + "Sentimento: Neutro"
    return texto

def imagemNoticia(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    imagem = article.top_image
    exibir_imagem_da_internet(imagem)

def exibir_imagem_da_internet(image_url):
    st.image(image_url)

def requisicaoHttp(url):
    response = requests.get(url)
    content = response.content
    site = BeautifulSoup(content, "html.parser")
    return site

def buscarNoticias():
    urlValor = "https://valor.globo.com/"
    urlInvesting = "https://www.investing.com/"
    urlInfoMoney = "https://www.infomoney.com.br/"
    
    listaUrl = [urlInfoMoney, urlInvesting, urlValor]
    listaNoticias = []
    numNoticias = 15
    
    for url in listaUrl:
        site = requisicaoHttp(url)
        cont = 0
                    
        if "infomoney" in url:
            div = site.findAll("div", class_="row mt-5 default_Big")[0]
            for title in div.findAll("a"):
                try:
                    titulo = title["title"]
                    link = title["href"]
                    # Verificar se a notícia já existe na lista
                    if [titulo, link] not in listaNoticias:
                        listaNoticias.append([titulo, link])
                except:
                    print("erro infomoney")
                cont += 1
                if cont == numNoticias:
                    break

    return listaNoticias
        
def exibeNoticias(list):
    for noticia in list:
        titulo, link = noticia
        col1, col2 = st.columns([1, 3])  # Defina a proporção de largura das colunas

        with col1:
            # Adicione a lógica para obter e exibir a imagem aqui
            imagemNoticia(link)

        with col2:
            st.subheader(f"[{titulo}]({link})")
            resumoNoticia = resumeNoticiaMl(link)
            textoNegrito = "<strong>" + "Resumo gerado por Machine Learning: " + "</strong>"
            st.markdown(textoNegrito, unsafe_allow_html=True)
            st.write(resumoNoticia)
            st.write("------------------------------")

def escolheTicker():
    ticker = st.text_input("Ticker", value="AAPL")
    data_inicio = st.date_input("Data de início",  datetime(2024, 1, 1))
    data_fim = st.date_input("Data final")
    listaInfo = [ticker, data_inicio, data_fim]
    return listaInfo

def exibeGrafico(lista):
    info = yf.download(lista[0], start=lista[1], end=lista[2])
    ultimo_valor = info['Adj Close'].iloc[-1]
    penultimo_valor = info['Adj Close'].iloc[-2]
    if info.empty:
        st.write("##")
        st.write("##")
        st.warning(f"Ocorreu um erro durante o download dos dados de {lista[0]}")
    else:
        grafico = px.line(info, x=info.index, y="Adj Close", title=lista[0])
        grafico.update_layout(
            title_x=0.5,
            title_font=dict(size=24),
            xaxis=dict(title=None, title_font=dict(size=18)),
            yaxis=dict(title="  ", title_font=dict(size=18), tickfont=dict(size=14)),
            plot_bgcolor='rgba(40, 140, 240, 0.2)', 
            height=500,  # Altura desejada em pixels
            width=850  
        )
        if ultimo_valor > penultimo_valor:
            grafico.update_traces(line=dict(color='green'))
        elif ultimo_valor < penultimo_valor:
            grafico.update_traces(line=dict(color='red'))
        else: 
            grafico.update_traces(line=dict(color='blue'))
        st.plotly_chart(grafico)
    
def plot_ibov_last_12h():
    ibov_data = yf.download("^BVSP", period="1d", interval="1m")
    last_12h_data = ibov_data.loc[datetime.now() - timedelta(hours=12):]
    ultimo_valor = ibov_data['Adj Close'].iloc[-1]
    penultimo_valor = ibov_data['Adj Close'].iloc[-2]
    if last_12h_data.empty:
        last_12h_data = ibov_data.loc[datetime.now() - timedelta(hours=24):]
        ultimo_valor = ibov_data['Adj Close'].dropna().iloc[-1]
        penultimo_valor = ibov_data['Adj Close'].dropna().iloc[-2]
        if last_12h_data.empty:
            last_12h_data = ibov_data.loc[datetime.now() - timedelta(days=3):]
            ultimo_valor = ibov_data['Adj Close'].dropna().iloc[-1]
            penultimo_valor = ibov_data['Adj Close'].dropna().iloc[-2]
    y_min = last_12h_data['Close'].min() - 500
    y_max = last_12h_data['Close'].max() + 500
    if ultimo_valor > penultimo_valor:
        colorLine = "green"
    elif ultimo_valor < penultimo_valor:
        colorLine = "red"
    else:
        colorLine = "blue"
    chart = alt.Chart(last_12h_data.reset_index()).mark_line().encode(
        x='Datetime:T',
        y=alt.Y('Close:Q', scale=alt.Scale(domain=[y_min, y_max])),
        color=alt.value(colorLine)
    ).properties(
        width=300,
        height=200
    ).configure_axis(
        titleFontSize=0   
    )
    return chart

# Basic page configuration
st.set_page_config(page_title="Dashboard Financeiro", page_icon=":bar_chart:", layout="wide")

# ------ Header ------
with st.container():
    # criando data
    data_atual = datetime.now()
    dia_da_semana = data_atual.weekday()
    mes = data_atual.month
    nomes_dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    nomes_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    nome_mes = nomes_meses[mes - 1]
    nome_dia_da_semana = nomes_dias_semana[dia_da_semana]
    data_formatada = data_atual.strftime(f"{nome_dia_da_semana}, %d de {nome_mes}/%Y - %H:%M")
    st.subheader(f"{data_formatada}")
    st.title("Dashboard de Informações Financeiras")
    st.write("Esse dashboard foi desenvolvido utilizando webscrapping, streamlit e algumas outras ferramentas do python para faciliar o dia a dia de uma pessoa que trabalhe com o mercado financeiro.")
    st.write("Feito por [Lucas Caúla](https://www.linkedin.com/in/lucas-ca%C3%BAla-b17169215/?originalSubdomain=br)")

# ------ Maiores Variacoes ------  
with st.container():
    st.write("---")
    st.title("Bolsa de Valores")
    df = buscarMaioresVariacoes()
    left_column, middleLeft_column, middleRight_column, right_column = st.columns(4)
    with left_column:
        st.header("Maiores altas")
        percorreDfVariacoes(df, 1)
    with middleLeft_column:
        st.header("Maiores baixas")
        percorreDfVariacoes(df, 2)
    with middleRight_column:
        st.header("Mais negociadas")
        percorreDfVariacoes(df, 3)
    with right_column:
        st.header("Bovespa")
        fig = plot_ibov_last_12h()
        st.altair_chart(fig)

# ------ Indices Economicos ------
with st.container():
    st.write("---")
    st.title("Índices Econômicos")
    left_column, middleLeft_column, middleRight_column, right_column = st.columns(4)
    with left_column:
        st.header("Gerais")
        #st.write("##")
        retornarGerais()
    with middleLeft_column:
        st.header("Inflação")
        #st.write("##")
        retornarInflacao()
    with middleRight_column:
        st.header("Commodities")
        #st.write("##")
        retornarCommodities()
    with right_column:
        st.header("Produtos agrícolas")
        #st.write("##")
        retornarAgricolas()

# ------ Noticias ------
with st.container():
    st.write("---")
    st.title("Notícias do Dia")
    st.write("##")
    listaNoticias = buscarNoticias()
    exibeNoticias(list= listaNoticias)

# ------ stock monitor ------
with st.container():
    st.write("---")
    st.title("Stock Monitor")
    #st.write("##")
    left_column, right_column = st.columns([1,2])
    with left_column:
        st.write("##")
        st.write("##")
        lista = escolheTicker()
    with right_column:
        exibeGrafico(lista)


