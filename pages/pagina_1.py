

import streamlit as st

import pandas as pd
import quantstats as qs



import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.figure_factory as ff



st.set_page_config(page_title="Página 1", page_icon="📄", layout="wide")
st.title("Resultados da carteira:")
col1, col2 = st.columns(2, gap= 'large', vertical_alignment= "top" )

with col1:
    if "tickers" in st.session_state:
        tickers = st.session_state["tickers"]
        st.markdown("**Tickers selecionados:**")
        for t in tickers:
            st.markdown(f"- {t}")
        if "prices" in st.session_state:
            prices = st.session_state["prices"]
            norm_prices = 100 * prices / prices.iloc[0]
            returns = prices.pct_change().dropna()
            returns = pd.DataFrame(returns)
            #st.write(returns)
            qs.extend_pandas()
            returns = prices.pct_change().dropna()
            portfolio = returns['portfolio']
            IBOV = returns['IBOV']
            qs.extend_pandas()
            rep = qs.reports.metrics(portfolio, benchmark= IBOV,mode = 'full' ,title = "Desempenho da carteira", display = False )
            st.table(rep)    
    else:
        st.warning(" Nenhum ticker selecionado, por favor selecione as  empresa na página inicial.")


with col2: 
    #grafico 1
    cum_returns = (1 + portfolio).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    fig1 = make_subplots(rows = 3, cols =1 , vertical_spacing=0.01, shared_xaxes = True)
    fig1.add_trace(go.Scatter(y=cum_returns, mode='lines', name='Carteira'), row=1, col=1)
    fig1.add_trace(go.Scatter(x=drawdown.index, y=drawdown, fill='tozeroy', fillcolor='rgba(255, 165, 0, 0.3)', line=dict(color='orange', width=1.5), name='Drawdown'), row=2, col=1)
    fig1.add_trace(go.Scatter(x = portfolio.index, y= portfolio, mode='lines', name='Carteira'), row=3, col=1)
    #
    fig1.update_layout(
    height=900, width=800,
    title_text="Análise de Performance da Carteira"
    )
    #
    fig1.update_xaxes(title_text="Data", row=3, col=1)
    fig1.update_yaxes(title_text="Valor acumulado", row=1, col=1)
    fig1.update_yaxes(title_text="Drawdown", row=2, col=1)
    fig1.update_yaxes(title_text="Retorno Diário", row=3, col=1)
    st.plotly_chart(fig1)
    #grafico 2
    yearly_portfolio = (1 + returns).resample('Y').prod() - 1
    yearly_portfolio.index = yearly_portfolio.index.year
    fig2= px.bar(yearly_portfolio, title='Retorno Anual', barmode= 'group', labels= {'Value': 'Retorno (%)', 'index': 'Amo'})
    fig2.update_layout(yaxis_tickformat='0.1%')
    fig2.update_xaxes(title_text="Data")
    st.plotly_chart(fig2)
    #grafico 3
    group_labels = ['distribuição de densidade']
    fig3 = ff.create_distplot([returns['portfolio']],group_labels,show_hist=True, show_curve= True,show_rug=False, bin_size= 0.002 )
    fig3.update_layout(xaxis_title='Percentual', yaxis_title='Ocorrencias', xaxis_tickformat='0.1%', title_text = 'Distribuição dos retornos diários')
    st.plotly_chart(fig3)
    #grafico 4
    group_labels = ['Retornos do portfólio', 'Reornos do IBOV']
    colors = ['rgb(0, 0, 100)', 'rgb(0, 200, 200)']
    monthly_portfolio = (1 + returns).resample('M').prod() - 1
    monthly_portfolio.index = monthly_portfolio.index.month
    fig4 = ff.create_distplot([monthly_portfolio['portfolio'],monthly_portfolio['IBOV']], group_labels, bin_size=0.015, colors=colors, show_rug=False)
    fig4.update_layout(title_text='Distribuição dos retornos mensais')
    st.plotly_chart(fig4)
    #grafico 5

#fig = fig = qs.plots.snapshot(returns, title='Performace da Carteira', show=False)
#st.write(fig)
    




with st.sidebar:
    st.page_link("home.py", label="Home", icon="🏠")

