import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
from pypfopt  import risk_models
from pypfopt.expected_returns import mean_historical_return
#from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
#import plotly.graph_objects as go


def build_sidebar():
    st.image("https://github.com/gabrielbandeiraggwp/Dashboard_gerenciamento_de_portifolio/blob/main/imagens/LogoSample_ByTailorBrands.jpg")
    ticker_list = pd.read_csv("tickers_ibra.csv", index_col=0)
    tickers = st.multiselect(label="Selecione as Empresas",
     options=ticker_list,
      placeholder='Códigos',
       key = "tickers_selected",
       )
    tickers = [t+".SA" for t in tickers]
    start_date = st.date_input("De", format="DD/MM/YYYY", value=datetime(2023,1,2))
    end_date = st.date_input("Até", format="DD/MM/YYYY", value="today")
    
    

    if tickers:
        prices = yf.download(tickers, start=start_date, end=end_date, multi_level_index=False)["Close"]
        if len(tickers) == 1:
            prices = prices.to_frame()
            prices.columns = [tickers[0].rstrip(".SA")]
                    
        prices.columns = prices.columns.str.rstrip(".SA")
        prices['IBOV'] = yf.download("^BVSP", start=start_date, end=end_date)["Close"]
        return tickers, prices
    return None, None

def build_main(tickers, prices):
    weights = np.ones(len(tickers))/len(tickers)
    prices['portfolio'] = prices.drop("IBOV", axis=1) @ weights
    norm_prices = 100 * prices / prices.iloc[0]
    returns = prices.pct_change()[1:]
    vols = returns.std()*np.sqrt(252)
    rets = (norm_prices.iloc[-1] - 100) / 100
    retornos_p_covariance = returns.drop(["IBOV", "portfolio"], axis=1)
    sample_cov = risk_models.sample_cov(retornos_p_covariance)







    

    mygrid = grid(3 ,3 ,3, 5, 5,  vertical_align="top")
    for t in prices.columns:
        c = mygrid.container(border=True)
        c.subheader(t, divider="blue")
        colA, colB, colC = c.columns(3)
        if t == "portfolio":
            colA.image("https://github.com/gabrielbandeiraggwp/Dashboard_gerenciamento_de_portifolio/blob/main/imagens/pie-chart-dollar-svgrepo-com.svg")
        elif t == "IBOV":
            colA.image("https://github.com/gabrielbandeiraggwp/Dashboard_gerenciamento_de_portifolio/blob/main/imagens/pie-chart-svgrepo-com.svg")
        else:
            colA.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{t}.png', width=85)
        colB.metric(label="retorno", value=f"{rets[t]:.0%}")
        colC.metric(label="volatilidade", value=f"{vols[t]:.0%}")
        style_metric_cards(background_color='rgba(38,181,199,0)')

    col1, col2 = st.columns(2, gap='large')
    with col1:
        #grafico 1
        st.subheader("Desempenho Relativo")
        st.line_chart(norm_prices, height=600)

        st.subheader("Matriz de Covariância")
        fig= px.imshow(sample_cov,text_auto = False)
        st.plotly_chart(fig)

    with col2:
        #grafico 2
        st.subheader("Risco-Retorno")
        fig = px.scatter(
            x=vols,
            y=rets,
            text=vols.index,
            color=rets/vols,
            color_continuous_scale=px.colors.sequential.Bluered_r
        )
        fig.update_traces(
            textfont_color='white', 
            marker=dict(size=45),
            textfont_size=10,                  
        )
        fig.layout.yaxis.title = 'Retorno Total'
        fig.layout.xaxis.title = 'Volatilidade (anualizada)'
        fig.layout.height = 600
        fig.layout.xaxis.tickformat = ".0%"
        fig.layout.yaxis.tickformat = ".0%"        
        fig.layout.coloraxis.colorbar.title = 'Sharpe'
        st.plotly_chart(fig, use_container_width=True)
        #
        st.subheader("Carteira com pesos de minima variância")
        mu = mean_historical_return(prices.drop(["IBOV", "portfolio"], axis = 1))
        prices_ativos = prices.drop(["IBOV", "portfolio"], axis=1)
        S = risk_models.CovarianceShrinkage(prices_ativos).ledoit_wolf()
        ef = EfficientFrontier(mu, S)
        weights_max = ef.max_sharpe()
        st.table(weights_max)
    # colocar grafico da fronteira efciente
    
    
    


        


        
st.set_page_config(page_title = "Pagina inicial", page_icon="🏠", layout = "wide")

with st.sidebar:
    tickers, prices  = build_sidebar()

st.title('Dashboard de gestão de portifólio')
if tickers:
    st.session_state["tickers"] = tickers
    st.session_state["prices"] = prices
    
    
    build_main(tickers, prices)
