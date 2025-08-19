# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 11:58:24 2025

@author: bixot
"""


import os
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
import quantstats as qs

qs.extend_pandas()
st.set_page_config(layout="wide")
st.title('Gerenciamento de Portfolio')

def build_sidebar():
    st.image("imagens/LogoSample_ByTailorBrands.jpg")
    ticker_lista = pd.read_csv("tickers_ibra.csv", index_col=0)
    tickers = st.multiselect(label="Selecione as empresas:",
                            options=ticker_lista,
                            placeholder='codigos')
    tickers = [t+".SA" for t in tickers]
    data_inicial = st.date_input("De", format="DD/MM/YYYY",
                               value=datetime(2023,1,1))
    data_final = st.date_input("Até", format="DD/MM/YYYY",
                             value="today")
    
    if not tickers:
        st.warning("Nenhum ticker selecionado. Por favor, selecione os tickers.")
        return [], pd.DataFrame()

    try:
        # Baixa dados dos tickers e do IBOV
        precos = yf.download(tickers, start=data_inicial, end=data_final)["Close"]
        precos['IBOV'] = yf.download("^BVSP", start=data_inicial, end=data_final)["Close"]
        
        # Remove .SA dos nomes das colunas
        precos.columns = precos.columns.str.rstrip(".SA")
        
        # Preenche valores faltantes
        precos = precos.ffill()
        
        return [t.rstrip(".SA") for t in tickers], precos
    
    except Exception as e:
        st.error(f"Erro ao baixar os dados: {e}")
        return [], pd.DataFrame()

def build_main(tickers, precos):
    if precos.empty or not tickers:
        st.warning("Dados insuficientes para análise.")
        return
    
    try:
        # Cálculo dos pesos (igualitário por padrão)
        pesos = np.ones(len(tickers)) / len(tickers)
        
        # Verifica se todas as colunas dos tickers existem no DataFrame
        valid_tickers = [t for t in tickers if t in precos.columns]
        
        if not valid_tickers:
            st.error("Nenhum ticker válido encontrado nos dados.")
            return
            
        # Cálculo do portfólio
        precos['Portfolio'] = precos[valid_tickers].dot(pesos[:len(valid_tickers)])
        
        # Normalização dos preços
        norm_precos = 100 * precos.div(precos.iloc[0])
        
        # Cálculos de retorno e volatilidade
        returns = precos.pct_change().dropna()
        volatilidade = returns.std() * np.sqrt(252)
        rets = (norm_precos.iloc[-1] - 100) / 100
        
        # Exibição dos cards de métricas
        my_grid = grid(5, 5, 5, 5, 5, 5, vertical_align="top")
        for t in norm_precos.columns:
            c = my_grid.container(border=True)
            c.subheader(t, divider="green")
            colA, colB, colC = c.columns(3)
            
            if t == 'Portfolio':
                colA.image("imagens/pie-chart-dollar-svgrepo-com.svg")
            elif t == "IBOV":
                colA.image("imagens/pie-chart-dollar-svgrepo-com.svg")
            else:
                colA.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{t}.png', width=85)
            
            colB.metric(label="retorno", value=f"{rets.get(t, 0):.2%}")
            colC.metric(label="volatilidade", value=f"{volatilidade.get(t, 0):.2%}")
        
        style_metric_cards(background_color='rgba(255,255,255,0)')
        
        # Gráficos
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.subheader('Desempenho relativo')
            st.line_chart(norm_precos)
            
        with col2:
            st.subheader('Risco-Retorno')
            fig = px.scatter(
                x=volatilidade,
                y=rets,
                text=volatilidade.index,
                color=rets/volatilidade,
                color_continuous_scale=px.colors.sequential.Bluered_r
            )
            fig.update_traces(
                textfont_color='white',
                marker=dict(size=45),
                textfont_size=10,
            )
            fig.update_layout(
                yaxis_title='Retorno Total',
                xaxis_title='Volatilidade (anualizada)',
                height=600,
                xaxis_tickformat=".0%",
                yaxis_tickformat=".0%",
                coloraxis_colorbar_title='Sharpe'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Exibição dos dados brutos
        st.dataframe(precos)
        
    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")

# Interface principal
with st.sidebar:
    tickers, precos = build_sidebar()

if tickers and not precos.empty:
    build_main(tickers, precos)
