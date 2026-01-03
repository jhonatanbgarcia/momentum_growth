import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Growth Hunter Pro", layout="wide", initial_sidebar_state="expanded")
br_tz = pytz.timezone('America/Sao_Paulo')

# --- BANCO DE DADOS TOP 50 (Exemplos de Growth e Blue Chips) ---
TOP_50_B3 = sorted([
    'EMBR3.SA', 'RENT3.SA', 'DIRR3.SA', 'TOTS3.SA', 'WEGE3.SA', 'PETR4.SA', 'VALE3.SA', 
    'ITUB4.SA', 'BBDC4.SA', 'PRIO3.SA', 'LREN3.SA', 'BBAS3.SA', 'ABEV3.SA', 'MGLU3.SA', 
    'CIEL3.SA', 'VBBR3.SA', 'CSNA3.SA', 'GGBR4.SA', 'SUZB3.SA', 'KLBN11.SA', 'RAIZ4.SA',
    'AZUL4.SA', 'GOLL4.SA', 'COGN3.SA', 'CVCB3.SA', 'HAPV3.SA', 'RADL3.SA', 'HYPE3.SA',
    'BPAC11.SA', 'STBP3.SA', 'ALOS3.SA', 'CYRE3.SA', 'MRVE3.SA', 'ELET3.SA', 'CPLE6.SA'
])

# --- FUNÇÕES DE ANÁLISE AVANÇADA ---
def fetch_comprehensive_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if df.empty: return None
        
        # Dados Técnicos
        close = df['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # Volatilidade e Médias
        ma20 = close.rolling(window=20).mean()
        ma50 = close.rolling(window=50).mean()
        dist_ma20 = ((close.iloc[-1] / ma20.iloc[-1]) - 1) * 100
        volatilidade = (df['High'] - df['Low']).tail(10).mean()
        
        # Dados Fundamentais Sintetizados (Yahoo Finance)
        info = stock.info
        
        return {
            "ticker": ticker,
            "price": close.iloc[-1],
            "change": ((close.iloc[-1] / close.iloc[-2]) - 1) * 100,
            "rsi": rsi.iloc[-1],
            "ma20": ma20.iloc[-1],
            "ma50": ma50.iloc[-1],
            "dist_ma20": dist_ma20,
            "vol": volatilidade,
            "history": close.tail(60),
            "target": info.get('targetMeanPrice', close.iloc[-1] * 1.15),
            "empresa": info.get('longName', ticker)
        }
    except:
        return None

# --- SIDEBAR COM MULTI-SELECT ---
with st.sidebar:
    st.header("🎯 Gestão de Portfólio")
    favoritas = st.multiselect(
        "Selecione suas Favoritas (Top 50):",
        options=TOP_50_B3,
        default=['EMBR3.SA', 'RENT3.SA', 'DIRR3.SA', 'TOTS3.SA']
    )
    
    st.divider()
    auto_refresh = st.checkbox("🔄 Atualização Automática (30 min)", value=False)
    btn_update = st.button("🚀 Atualizar Agora")
    
    st.markdown("""
    ### 📖 Legenda Pro
    - **RSI < 35:** Sobre-venda (Oportunidade Técnica).
    - **RSI > 65:** Sobre-compra (Exaustão).
    - **Dist. Média 20:** O quanto o preço está 'longe' do seu valor justo médio recente.
    """)

# --- LAYOUT PRINCIPAL ---
st.title("📈 Terminal Pro: Momentum & Growth")

# Cronômetro de atualização
if auto_refresh:
    st.caption(f"Próxima atualização em 30 minutos. Última: {datetime.now(br_tz).strftime('%H:%M:%S')}")
    # Nota: Em um app real Streamlit, o auto-refresh é feito com st_autorefresh. 
    # Aqui simulamos a intenção.

# --- SEÇÃO 1: CARDS DETALHADOS ---
st.header("⭐ Favoritas em Detalhe")
for t in favoritas:
    data = fetch_comprehensive_data(t)
    if data:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 1.5, 2])
            
            with col1:
                st.subheader(data['ticker'])
                st.write(f"**{data['empresa']}**")
                st.metric("Preço Atual", f"R$ {data['price']:.2f}", f"{data['change']:.2f}%")
                st.metric("RSI (14d)", f"{data['rsi']:.2f}")

            with col2:
                st.markdown("**Análise de Momento:**")
                # Lógica de síntese
                if data['rsi'] < 35:
                    st.success("🔥 OPORTUNIDADE TÉCNICA")
                    msg = "O ativo está sendo negociado com forte pessimismo. O preço atual está abaixo do suporte psicológico, sugerindo uma reversão de alta iminente."
                elif data['rsi'] > 65:
                    st.error("⚠️ ALERTA DE EXAUSTÃO")
                    msg = "Ativo muito esticado. A força compradora atingiu o pico e o risco de uma correção para a média de 20 períodos é elevado agora."
                else:
                    st.info("⚖️ CONSOLIDAÇÃO")
                    msg = "O ativo está em zona de equilíbrio. Ideal para acumulação gradual sem pressa de entrada explosiva."
                
                st.write(msg)
                st.write(f"**Alvo Analistas:** R$ {data['target']:.2f}")
                st.write(f"**Distância Média (20d):** {data['dist_ma20']:.2f}%")

            with col3:
                st.line_chart(data['history'], height=200)
                c_buy, c_sell = st.columns(2)
                c_buy.button(f"🛒 Compra: R$ {data['price'] - (data['vol']*0.8):.2f}", key=f"b_{t}")
                c_sell.button(f"🎯 Alvo: R$ {data['price'] + (data['vol']*1.2):.2f}", key=f"s_{t}")

# --- SEÇÃO 2: SCREENER DE OPORTUNIDADES ---
st.divider()
st.header("🔎 Radar de Oportunidades (Mercado Aberto)")
with st.spinner("Sintetizando dados de mercado..."):
    all_data = []
    for t in TOP_50_B3:
        d = fetch_comprehensive_data(t)
        if d: all_data.append(d)
    
    df_opp = pd.DataFrame(all_data).sort_values(by='rsi')

st.table(df_opp[['ticker', 'price', 'rsi', 'dist_ma20']].head(10).assign(Status=lambda x: "🔥 COMPRA" if any(x['rsi'] < 35) else "⚖️ NEUTRO"))

# --- LÓGICA DE REFRESH ---
if auto_refresh:
    time.sleep(1800) # 30 minutos
    st.rerun()