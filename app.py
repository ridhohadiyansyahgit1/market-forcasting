import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="📈 Market Forecaster",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #060b14 0%, #0a1628 100%); }
    .block-container { padding: 1.5rem 2rem 4rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080f1e 0%, #0d1b2a 100%);
        border-right: 1px solid rgba(56,189,248,0.1);
    }
    .hero {
        background: linear-gradient(135deg, rgba(56,189,248,0.1), rgba(99,102,241,0.08), rgba(168,85,247,0.06));
        border: 1px solid rgba(56,189,248,0.2); border-radius: 20px;
        padding: 2rem; margin-bottom: 1.5rem;
        position: relative; overflow: hidden;
    }
    .hero::before {
        content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%;
        background: radial-gradient(circle at 20% 50%, rgba(56,189,248,0.04) 0%, transparent 50%),
                    radial-gradient(circle at 80% 50%, rgba(168,85,247,0.04) 0%, transparent 50%);
        pointer-events:none;
    }
    .hero-title {
        font-size:2.4rem; font-weight:800;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .hero-sub { color:rgba(226,232,240,0.5); font-size:0.9rem; margin-top:0.5rem; }
    .hero-badges { margin-top:0.8rem; display:flex; gap:0.4rem; flex-wrap:wrap; }
    .badge {
        border-radius:20px; padding:3px 12px; font-size:0.72rem; font-weight:600;
        border: 1px solid; 
    }
    .badge-blue { background:rgba(56,189,248,0.1); border-color:rgba(56,189,248,0.3); color:#38bdf8; }
    .badge-purple { background:rgba(168,85,247,0.1); border-color:rgba(168,85,247,0.3); color:#c084fc; }
    .badge-green { background:rgba(52,211,153,0.1); border-color:rgba(52,211,153,0.3); color:#34d399; }
    .badge-gold { background:rgba(251,191,36,0.1); border-color:rgba(251,191,36,0.3); color:#fbbf24; }
    .metric-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(56,189,248,0.15); border-radius:14px;
        padding:1.2rem 1rem; text-align:center; position:relative; overflow:hidden;
    }
    .metric-card::after {
        content:''; position:absolute; top:0; left:0; right:0; height:2px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    }
    .metric-value {
        font-size:1.6rem; font-weight:800;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .metric-label { font-size:0.68rem; color:rgba(226,232,240,0.4); text-transform:uppercase; letter-spacing:0.07em; margin-top:4px; }
    .metric-delta-pos { font-size:0.8rem; color:#34d399; font-weight:600; margin-top:2px; }
    .metric-delta-neg { font-size:0.8rem; color:#f87171; font-weight:600; margin-top:2px; }
    .section-title {
        font-size:1rem; font-weight:700; color:#e2e8f0;
        margin:1.5rem 0 1rem; display:flex; align-items:center; gap:10px;
    }
    .section-title::after { content:''; flex:1; height:1px; background:linear-gradient(90deg, rgba(56,189,248,0.25), transparent); }
    .card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(56,189,248,0.12); border-radius:14px;
        padding:1.2rem; margin-bottom:1rem;
    }
    .price-up { color:#34d399; font-weight:700; }
    .price-down { color:#f87171; font-weight:700; }
    .stButton > button {
        background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
        border:none !important; border-radius:10px !important;
        font-weight:700 !important; color:white !important;
        box-shadow: 0 4px 20px rgba(56,189,248,0.25) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background:rgba(255,255,255,0.02); border-radius:12px; padding:4px; gap:4px;
        border:1px solid rgba(56,189,248,0.08);
    }
    .stTabs [aria-selected="true"] {
        background:linear-gradient(135deg, rgba(56,189,248,0.15), rgba(129,140,248,0.1)) !important;
        color:#38bdf8 !important;
    }
    hr { border-color:rgba(56,189,248,0.08) !important; }
    .ticker-tag {
        display:inline-block; background:rgba(56,189,248,0.1);
        border:1px solid rgba(56,189,248,0.25); border-radius:8px;
        padding:2px 10px; font-size:0.78rem; color:#38bdf8; font-weight:600;
        margin:2px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TICKER LISTS
# ─────────────────────────────────────────────
SAHAM_IDX = {
    "BBCA (Bank BCA)": "BBCA.JK",
    "BBRI (Bank BRI)": "BBRI.JK",
    "TLKM (Telkom)": "TLKM.JK",
    "GOTO (GoTo)": "GOTO.JK",
    "BMRI (Bank Mandiri)": "BMRI.JK",
    "ASII (Astra)": "ASII.JK",
    "UNVR (Unilever)": "UNVR.JK",
    "ICBP (Indofood CBP)": "ICBP.JK",
}
CRYPTO = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
}
COMMODITY = {
    "Gold / XAUUSD": "GC=F",
    "Silver / XAGUSD": "SI=F",
    "Crude Oil (WTI)": "CL=F",
}

ALL_TICKERS = {**SAHAM_IDX, **CRYPTO, **COMMODITY}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
        <div style="font-size:2.5rem;">📈</div>
        <div style="font-size:1.1rem;font-weight:800;background:linear-gradient(135deg,#38bdf8,#818cf8);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Market Forecaster</div>
        <div style="font-size:0.72rem;color:rgba(226,232,240,0.35);margin-top:3px;">LSTM Deep Learning</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div style="color:rgba(226,232,240,0.45);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;">⚙️ Pengaturan</div>', unsafe_allow_html=True)

    asset_type = st.selectbox("Kategori Aset:", ["Saham Indonesia 🇮🇩", "Cryptocurrency ₿", "Komoditas 🥇"])
    if "Saham" in asset_type:
        ticker_name = st.selectbox("Pilih Saham:", list(SAHAM_IDX.keys()))
        ticker = SAHAM_IDX[ticker_name]
    elif "Crypto" in asset_type:
        ticker_name = st.selectbox("Pilih Crypto:", list(CRYPTO.keys()))
        ticker = CRYPTO[ticker_name]
    else:
        ticker_name = st.selectbox("Pilih Komoditas:", list(COMMODITY.keys()))
        ticker = COMMODITY[ticker_name]

    st.markdown("<br>", unsafe_allow_html=True)
    period_map = {"6 Bulan": "6mo", "1 Tahun": "1y", "2 Tahun": "2y", "5 Tahun": "5y"}
    period_label = st.select_slider("Periode Data:", list(period_map.keys()), value="1 Tahun")
    period = period_map[period_label]

    forecast_days = st.slider("Forecast berapa hari ke depan?", 7, 60, 30)

    st.divider()
    run_btn = st.button("🚀 Jalankan Analisis!", use_container_width=True)
    st.divider()
    st.markdown("""
    <div style="color:rgba(226,232,240,0.3);font-size:0.7rem;text-align:center;line-height:1.8;">
        Data: Yahoo Finance API<br>Model: LSTM (Keras)<br>Realtime · No API Key
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-title">📈 Market Forecaster</div>
    <div class="hero-sub">Prediksi harga Saham · Crypto · Gold menggunakan LSTM Deep Learning — data real-time dari Yahoo Finance</div>
    <div class="hero-badges">
        <span class="badge badge-blue">🏦 Saham Indonesia</span>
        <span class="badge badge-purple">₿ Cryptocurrency</span>
        <span class="badge badge-gold">🥇 Gold / XAUUSD</span>
        <span class="badge badge-green">🧠 LSTM Neural Network</span>
        <span class="badge badge-blue">⚡ Real-time Data</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not run_btn:
    # Landing state
    c1, c2, c3 = st.columns(3)
    c1.markdown("""<div class="card" style="text-align:center;">
        <div style="font-size:2.5rem;">🏦</div>
        <div style="font-weight:700;color:#38bdf8;margin-top:0.5rem;">Saham Indonesia</div>
        <div style="font-size:0.8rem;color:rgba(226,232,240,0.4);margin-top:0.3rem;">
            BBCA · BBRI · TLKM · GOTO · BMRI
        </div></div>""", unsafe_allow_html=True)
    c2.markdown("""<div class="card" style="text-align:center;">
        <div style="font-size:2.5rem;">₿</div>
        <div style="font-weight:700;color:#c084fc;margin-top:0.5rem;">Cryptocurrency</div>
        <div style="font-size:0.8rem;color:rgba(226,232,240,0.4);margin-top:0.3rem;">
            BTC · ETH · SOL · BNB · XRP
        </div></div>""", unsafe_allow_html=True)
    c3.markdown("""<div class="card" style="text-align:center;">
        <div style="font-size:2.5rem;">🥇</div>
        <div style="font-weight:700;color:#fbbf24;margin-top:0.5rem;">Komoditas</div>
        <div style="font-size:0.8rem;color:rgba(226,232,240,0.4);margin-top:0.3rem;">
            Gold (XAUUSD) · Silver · Crude Oil
        </div></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:2rem;color:rgba(226,232,240,0.3);">
        👈 Pilih aset di sidebar, lalu klik <b style="color:#38bdf8;">Jalankan Analisis!</b>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# FETCH DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(ticker, period):
    df = yf.download(ticker, period=period, progress=False)
    df = df[['Open','High','Low','Close','Volume']].dropna()
    return df

with st.spinner(f"📡 Mengambil data {ticker_name} dari Yahoo Finance..."):
    try:
        df = fetch_data(ticker, period)
        if df.empty:
            st.error("❌ Data tidak tersedia. Coba ticker lain.")
            st.stop()
    except Exception as e:
        st.error(f"❌ Gagal fetch data: {e}")
        st.stop()

# ─────────────────────────────────────────────
# CURRENT STATS
# ─────────────────────────────────────────────
latest = float(df['Close'].iloc[-1])
prev = float(df['Close'].iloc[-2])
change = latest - prev
change_pct = (change / prev) * 100
high_52w = float(df['Close'].tail(252).max())
low_52w = float(df['Close'].tail(252).min())
avg_vol = float(df['Volume'].tail(30).mean())

is_up = change >= 0
arrow = "▲" if is_up else "▼"
delta_color = "price-up" if is_up else "price-down"

c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(f"""<div class="metric-card">
    <div class="metric-value">{latest:,.2f}</div>
    <div class="{'metric-delta-pos' if is_up else 'metric-delta-neg'}">{arrow} {abs(change_pct):.2f}%</div>
    <div class="metric-label">Harga Terakhir</div></div>""", unsafe_allow_html=True)
c2.markdown(f"""<div class="metric-card">
    <div class="metric-value">{change:+,.2f}</div>
    <div class="{'metric-delta-pos' if is_up else 'metric-delta-neg'}">{arrow} Hari ini</div>
    <div class="metric-label">Perubahan Harga</div></div>""", unsafe_allow_html=True)
c3.markdown(f"""<div class="metric-card">
    <div class="metric-value">{high_52w:,.2f}</div>
    <div class="metric-delta-pos">52W High</div>
    <div class="metric-label">Tertinggi</div></div>""", unsafe_allow_html=True)
c4.markdown(f"""<div class="metric-card">
    <div class="metric-value">{low_52w:,.2f}</div>
    <div class="metric-delta-neg">52W Low</div>
    <div class="metric-label">Terendah</div></div>""", unsafe_allow_html=True)
c5.markdown(f"""<div class="metric-card">
    <div class="metric-value">{avg_vol/1e6:.1f}M</div>
    <div class="metric-delta-pos">30-day avg</div>
    <div class="metric-label">Volume</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Chart & Analisis", "🧠 LSTM Forecast", "📉 Technical Indicators", "📋 Data & Stats"
])

# ══════════════════════════════════════════════
# TAB 1 — CHART
# ══════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-title">📊 Harga {ticker_name}</div>', unsafe_allow_html=True)

    # Candlestick
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Harga', increasing_line_color='#34d399',
        decreasing_line_color='#f87171',
        increasing_fillcolor='rgba(52,211,153,0.3)',
        decreasing_fillcolor='rgba(248,113,113,0.3)'
    ), row=1, col=1)

    # MA Lines
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20',
                             line=dict(color='#fbbf24', width=1.5), opacity=0.9), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50',
                             line=dict(color='#38bdf8', width=1.5), opacity=0.9), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='MA200',
                             line=dict(color='#c084fc', width=1.5), opacity=0.9), row=1, col=1)

    # Volume
    colors_vol = ['rgba(52,211,153,0.5)' if c >= o else 'rgba(248,113,113,0.5)'
                  for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume',
                         marker_color=colors_vol), row=2, col=1)

    fig.update_layout(
        template='plotly_dark', height=600,
        plot_bgcolor='rgba(6,11,20,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        legend=dict(orientation='h', y=1.02, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(family='Inter')
    )
    fig.update_xaxes(gridcolor='rgba(56,189,248,0.05)')
    fig.update_yaxes(gridcolor='rgba(56,189,248,0.05)')
    st.plotly_chart(fig, use_container_width=True)

    # Return Distribution
    st.markdown(f'<div class="section-title">📈 Distribusi Return Harian</div>', unsafe_allow_html=True)
    returns = df['Close'].pct_change().dropna() * 100
    col1, col2 = st.columns([2,1])
    with col1:
        fig_ret = px.histogram(returns, nbins=60, color_discrete_sequence=['#818cf8'],
                               title="Distribusi Return Harian (%)")
        fig_ret.add_vline(x=0, line_dash='dash', line_color='white', opacity=0.5)
        fig_ret.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                               plot_bgcolor='rgba(6,11,20,0.8)', showlegend=False,
                               margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_ret, use_container_width=True)
    with col2:
        avg_ret = returns.mean()
        std_ret = returns.std()
        sharpe = avg_ret / std_ret * np.sqrt(252)
        max_dd = ((df['Close'] / df['Close'].cummax()) - 1).min() * 100
        st.markdown(f"""<div class="card">
            <b>📊 Return Stats</b><br><br>
            Avg Daily Return: <b style="color:{'#34d399' if avg_ret>0 else '#f87171'}">{avg_ret:+.3f}%</b><br>
            Volatilitas: <b style="color:#fbbf24">{std_ret:.3f}%</b><br>
            Sharpe Ratio: <b style="color:#38bdf8">{sharpe:.2f}</b><br>
            Max Drawdown: <b style="color:#f87171">{max_dd:.2f}%</b><br>
            Total Return: <b style="color:{'#34d399' if (df['Close'].iloc[-1]/df['Close'].iloc[0]-1)>0 else '#f87171'}">
                {(df['Close'].iloc[-1]/df['Close'].iloc[0]-1)*100:+.1f}%</b>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — LSTM FORECAST
# ══════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-title">🧠 LSTM Forecast — {forecast_days} Hari ke Depan</div>', unsafe_allow_html=True)

    @st.cache_resource
    def train_lstm(ticker, period, forecast_days):
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
            from sklearn.preprocessing import MinMaxScaler

            data = fetch_data(ticker, period)
            prices = data['Close'].values.reshape(-1, 1)

            scaler = MinMaxScaler()
            scaled = scaler.fit_transform(prices)

            SEQ_LEN = 60
            X, y = [], []
            for i in range(SEQ_LEN, len(scaled)):
                X.append(scaled[i-SEQ_LEN:i, 0])
                y.append(scaled[i, 0])
            X, y = np.array(X), np.array(y)
            X = X.reshape(X.shape[0], X.shape[1], 1)

            split = int(len(X) * 0.85)
            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]

            # Model LSTM Bidirectional
            model = Sequential([
                Bidirectional(LSTM(64, return_sequences=True), input_shape=(SEQ_LEN, 1)),
                Dropout(0.2),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dense(1)
            ])
            model.compile(optimizer='adam', loss='huber')
            model.fit(X_train, y_train, epochs=30, batch_size=32,
                      validation_data=(X_test, y_test), verbose=0,
                      callbacks=[tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)])

            # Prediksi on test set
            test_pred = scaler.inverse_transform(model.predict(X_test, verbose=0))
            test_actual = scaler.inverse_transform(y_test.reshape(-1,1))

            # Forecast masa depan
            last_seq = scaled[-SEQ_LEN:].reshape(1, SEQ_LEN, 1)
            future_preds = []
            for _ in range(forecast_days):
                pred = model.predict(last_seq, verbose=0)[0,0]
                future_preds.append(pred)
                last_seq = np.append(last_seq[:,1:,:], [[[pred]]], axis=1)

            future_prices = scaler.inverse_transform(np.array(future_preds).reshape(-1,1)).flatten()
            future_dates = pd.date_range(start=data.index[-1] + timedelta(days=1),
                                          periods=forecast_days, freq='B')

            return {
                'model': model, 'scaler': scaler,
                'test_pred': test_pred.flatten(),
                'test_actual': test_actual.flatten(),
                'test_dates': data.index[-len(test_actual):],
                'future_prices': future_prices,
                'future_dates': future_dates,
                'data': data, 'success': True
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    with st.spinner("🧠 Training LSTM model... (1-2 menit pertama kali)"):
        result = train_lstm(ticker, period, forecast_days)

    if not result['success']:
        st.error(f"❌ Error: {result['error']}")
    else:
        data = result['data']
        future_prices = result['future_prices']
        future_dates = result['future_dates']
        test_pred = result['test_pred']
        test_actual = result['test_actual']
        test_dates = result['test_dates']

        # Forecast metrics
        last_price = data['Close'].iloc[-1]
        forecast_end = future_prices[-1]
        forecast_change = (forecast_end - last_price) / last_price * 100
        is_bull = forecast_change > 0

        fc1, fc2, fc3 = st.columns(3)
        fc1.markdown(f"""<div class="metric-card">
            <div class="metric-value">{last_price:,.2f}</div>
            <div class="metric-label">Harga Sekarang</div></div>""", unsafe_allow_html=True)
        fc2.markdown(f"""<div class="metric-card">
            <div class="metric-value">{forecast_end:,.2f}</div>
            <div class="{'metric-delta-pos' if is_bull else 'metric-delta-neg'}">
                {'▲' if is_bull else '▼'} {abs(forecast_change):.2f}%
            </div>
            <div class="metric-label">Prediksi {forecast_days} Hari</div></div>""", unsafe_allow_html=True)
        fc3.markdown(f"""<div class="metric-card">
            <div class="metric-value">{'🟢 BULLISH' if is_bull else '🔴 BEARISH'}</div>
            <div class="metric-label">Sinyal Forecast</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart forecast
        fig_fc = go.Figure()

        # Historical (last 120 days)
        hist_tail = data.tail(120)
        fig_fc.add_trace(go.Scatter(
            x=hist_tail.index, y=hist_tail['Close'],
            name='Harga Historis', line=dict(color='#38bdf8', width=2)
        ))

        # Test predictions
        fig_fc.add_trace(go.Scatter(
            x=test_dates, y=test_pred,
            name='Prediksi (Validasi)', line=dict(color='#fbbf24', width=1.5, dash='dot')
        ))

        # Future forecast with confidence band
        std_err = np.std(test_actual - test_pred)
        upper = future_prices + 1.96 * std_err
        lower = future_prices - 1.96 * std_err

        fig_fc.add_trace(go.Scatter(
            x=list(future_dates) + list(future_dates[::-1]),
            y=list(upper) + list(lower[::-1]),
            fill='toself', fillcolor='rgba(129,140,248,0.1)',
            line=dict(color='rgba(0,0,0,0)'),
            name='95% Confidence Interval'
        ))
        fig_fc.add_trace(go.Scatter(
            x=future_dates, y=future_prices,
            name=f'Forecast {forecast_days}D',
            line=dict(color='#c084fc', width=2.5, dash='dash'),
            marker=dict(size=4)
        ))

        # Garis pemisah
        fig_fc.add_vline(x=data.index[-1], line_dash='dash',
                          line_color='rgba(226,232,240,0.3)', line_width=1)
        fig_fc.add_annotation(x=data.index[-1], y=last_price,
                               text="Today", showarrow=True,
                               arrowcolor='#38bdf8', font=dict(color='#38bdf8', size=11))

        fig_fc.update_layout(
            template='plotly_dark', height=500,
            title=f"LSTM Forecast — {ticker_name} (+{forecast_days} hari)",
            plot_bgcolor='rgba(6,11,20,0.8)', paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', y=1.02),
            margin=dict(l=0,r=0,t=50,b=0)
        )
        fig_fc.update_xaxes(gridcolor='rgba(56,189,248,0.05)')
        fig_fc.update_yaxes(gridcolor='rgba(56,189,248,0.05)')
        st.plotly_chart(fig_fc, use_container_width=True)

        # Forecast table
        st.markdown('<div class="section-title">📅 Tabel Forecast Harian</div>', unsafe_allow_html=True)
        forecast_df = pd.DataFrame({
            'Tanggal': future_dates.strftime('%d %b %Y'),
            'Prediksi Harga': [f"{p:,.2f}" for p in future_prices],
            'Perubahan (%)': [f"{(future_prices[i]-future_prices[i-1])/future_prices[i-1]*100:+.2f}%" if i>0
                               else f"{(future_prices[0]-last_price)/last_price*100:+.2f}%"
                               for i in range(len(future_prices))]
        })
        st.dataframe(forecast_df, use_container_width=True, height=300)

        st.markdown("""
        <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                    border-radius:10px;padding:0.75rem 1rem;font-size:0.8rem;color:#fbbf24;">
            ⚠️ <b>Disclaimer:</b> Prediksi ini hanya untuk tujuan edukasi. Bukan saran investasi.
            Harga pasar dipengaruhi banyak faktor yang tidak bisa diprediksi sepenuhnya oleh model AI.
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — TECHNICAL INDICATORS
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📉 Technical Indicators</div>', unsafe_allow_html=True)

    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']

    # Bollinger Bands
    df['BB_Mid'] = df['Close'].rolling(20).mean()
    df['BB_Std'] = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
    df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']

    fig_tech = make_subplots(rows=3, cols=1, shared_xaxes=True,
                              row_heights=[0.5, 0.25, 0.25],
                              subplot_titles=('Bollinger Bands', 'RSI', 'MACD'),
                              vertical_spacing=0.06)

    # Bollinger Bands chart
    fig_tech.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                                   line=dict(color='rgba(56,189,248,0.4)', dash='dash', width=1)), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                                   fill='tonexty', fillcolor='rgba(56,189,248,0.05)',
                                   line=dict(color='rgba(56,189,248,0.4)', dash='dash', width=1)), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close',
                                   line=dict(color='#38bdf8', width=2)), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=df.index, y=df['BB_Mid'], name='BB Mid',
                                   line=dict(color='#fbbf24', width=1, dash='dot')), row=1, col=1)

    # RSI
    fig_tech.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI',
                                   line=dict(color='#c084fc', width=2)), row=2, col=1)
    fig_tech.add_hline(y=70, line_dash='dash', line_color='#f87171', opacity=0.6, row=2, col=1)
    fig_tech.add_hline(y=30, line_dash='dash', line_color='#34d399', opacity=0.6, row=2, col=1)
    fig_tech.add_hrect(y0=70, y1=100, fillcolor='rgba(248,113,113,0.05)', line_width=0, row=2, col=1)
    fig_tech.add_hrect(y0=0, y1=30, fillcolor='rgba(52,211,153,0.05)', line_width=0, row=2, col=1)

    # MACD
    colors_macd = ['rgba(52,211,153,0.6)' if v >= 0 else 'rgba(248,113,113,0.6)'
                   for v in df['MACD_Hist'].fillna(0)]
    fig_tech.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='MACD Hist',
                               marker_color=colors_macd), row=3, col=1)
    fig_tech.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD',
                                   line=dict(color='#38bdf8', width=1.5)), row=3, col=1)
    fig_tech.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Signal',
                                   line=dict(color='#fbbf24', width=1.5)), row=3, col=1)

    fig_tech.update_layout(template='plotly_dark', height=700,
                            plot_bgcolor='rgba(6,11,20,0.8)', paper_bgcolor='rgba(0,0,0,0)',
                            legend=dict(orientation='h', y=1.02),
                            margin=dict(l=0,r=0,t=40,b=0))
    fig_tech.update_xaxes(gridcolor='rgba(56,189,248,0.05)')
    fig_tech.update_yaxes(gridcolor='rgba(56,189,248,0.05)')
    st.plotly_chart(fig_tech, use_container_width=True)

    # Signal Summary
    st.markdown('<div class="section-title">🎯 Sinyal Trading</div>', unsafe_allow_html=True)
    rsi_now = df['RSI'].iloc[-1]
    macd_now = df['MACD'].iloc[-1]
    signal_now = df['Signal'].iloc[-1]
    price_now = df['Close'].iloc[-1]
    bb_upper = df['BB_Upper'].iloc[-1]
    bb_lower = df['BB_Lower'].iloc[-1]

    signals = []
    if rsi_now > 70: signals.append(("RSI", "🔴 OVERBOUGHT", "Potensi koreksi turun", "#f87171"))
    elif rsi_now < 30: signals.append(("RSI", "🟢 OVERSOLD", "Potensi rebound naik", "#34d399"))
    else: signals.append(("RSI", "🟡 NEUTRAL", f"RSI = {rsi_now:.1f}", "#fbbf24"))

    if macd_now > signal_now: signals.append(("MACD", "🟢 BULLISH", "MACD > Signal Line", "#34d399"))
    else: signals.append(("MACD", "🔴 BEARISH", "MACD < Signal Line", "#f87171"))

    if price_now > bb_upper: signals.append(("Bollinger", "🔴 OVERBOUGHT", "Harga di atas BB Upper", "#f87171"))
    elif price_now < bb_lower: signals.append(("Bollinger", "🟢 OVERSOLD", "Harga di bawah BB Lower", "#34d399"))
    else: signals.append(("Bollinger", "🟡 NORMAL", "Harga dalam range BB", "#fbbf24"))

    cols = st.columns(3)
    for i, (ind, sig, desc, color) in enumerate(signals):
        cols[i].markdown(f"""<div class="card" style="border-color:{color}33;text-align:center;">
            <div style="font-size:0.7rem;color:rgba(226,232,240,0.4);text-transform:uppercase;">{ind}</div>
            <div style="font-size:1.1rem;font-weight:700;color:{color};margin:0.5rem 0;">{sig}</div>
            <div style="font-size:0.78rem;color:rgba(226,232,240,0.5);">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — DATA & STATS
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">📋 Data Historis</div>', unsafe_allow_html=True)
    display_df = df[['Open','High','Low','Close','Volume']].tail(100).copy()
    display_df = display_df.round(2)
    display_df.index = display_df.index.strftime('%Y-%m-%d')
    st.dataframe(display_df[::-1], use_container_width=True, height=400)

    st.markdown('<div class="section-title">📊 Statistik Deskriptif</div>', unsafe_allow_html=True)
    st.dataframe(df[['Open','High','Low','Close','Volume']].describe().round(2), use_container_width=True)

    # Correlation
    st.markdown('<div class="section-title">🔗 Korelasi Fitur</div>', unsafe_allow_html=True)
    corr = df[['Open','High','Low','Close','Volume']].corr()
    fig_corr = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r',
                          title="Correlation Matrix")
    fig_corr.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig_corr, use_container_width=True)
