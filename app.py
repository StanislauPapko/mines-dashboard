import numpy as np
from numpy.polynomial import Polynomial
import pandas as pd
import streamlit as st
from mine import Mine
import plotly.graph_objects as go
from pdf_generator import generate_pdf

SHEET_ID = '1ofZ8WJh3Cpu-QC-Q1m2W6nRfGSunQLxlIvZrifL01zg'
GID_ID = '808628764'
URI_STRING = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_ID}'
df_raw = pd.read_csv(URI_STRING)
df_raw['date'] = pd.to_datetime(df_raw['date'], format='%d/%m/%Y')
df = df_raw.pivot(index='date', columns='mine_name', values='extraction').reset_index()
DATE_COLUMN_ID = 0
FIRST_MINE_COLUMN_ID = 1
date = df.iloc[:, DATE_COLUMN_ID]
mines = df.iloc[:,FIRST_MINE_COLUMN_ID:]

st.set_page_config(page_title='Mines Dashboard', layout='wide')
st.title('Weyland-Yutani Corporation: Extraction Results')
mines_selector = st.sidebar.selectbox('Mine', mines.columns)
selected_mine = Mine(mines[mines_selector])

NUMBER_OF_STATISTICS = 4
col1, col2, col3, col4 = st.columns(NUMBER_OF_STATISTICS)
col1.metric(label='Mean', value=selected_mine.get_mean())
col2.metric(label='Standard Deviation', value=selected_mine.get_std())
col3.metric(label='Median', value=selected_mine.get_median())
col4.metric(label='IQR', value=selected_mine.get_iqr())

PLOTS_TO_CHOOSE = ['Line', 'Bar', 'Stacked']
plot_type = st.sidebar.selectbox("Plot type", PLOTS_TO_CHOOSE)
DEGREE_TO_CHOOSE = [1, 2, 3, 4]
trend_degree = st.sidebar.selectbox("Trendline degree", DEGREE_TO_CHOOSE)
TESTS_TO_CHOOSE = ['IQR Rule', 'Z-score', 'Distance from Moving Average', "Iterative Grubbs's Test"]
outlier_test = st.sidebar.selectbox("Outliers test", TESTS_TO_CHOOSE)
if outlier_test == 'IQR Rule':
    k = st.sidebar.slider('IQR multiplier', min_value=0.5, max_value=3., value=1.5, step=0.1)
    outliers_layer = selected_mine.apply_iqr_rule(k=k)
elif outlier_test == 'Z-score':
    threshold = st.sidebar.slider('Z-score threshold', min_value=1., max_value=5., value=3., step=0.1)
    outliers_layer = selected_mine.apply_zscore(threshold=threshold)
elif outlier_test == 'Distance from Moving Average':
    window = st.sidebar.slider('Moving window length (days)', min_value=3, max_value=20, value=7, step=1)
    distance_bound = st.sidebar.slider('Max distance (%)', min_value=0.05, max_value=1., value=0.3, step=0.05)
    outliers_layer = selected_mine.apply_ma_distance(window=window, distance_bound=distance_bound)
elif outlier_test == "Iterative Grubbs's Test":
    alpha = st.sidebar.slider('Alpha (significance level)', min_value=0.01, max_value=0.2, value=0.05, step=0.01)
    outliers_layer = selected_mine.apply_grubbs(alpha=alpha)

fig = go.Figure()
x = date
y = selected_mine.data
if plot_type == 'Line':
    fig.add_scatter(x=x, y=y, mode='lines', name='Resource extraction')
elif plot_type == 'Bar':
    fig.add_bar(x=x, y=y, name='Resource extraction')
elif plot_type == 'Stacked':
    for mine in mines.columns:
        fig.add_bar(x=x, y=mines[mine], name = mine)
    fig.update_layout(barmode='stack')
fig.add_scatter(x=x[outliers_layer], y=y[outliers_layer], mode='markers', marker={'color':'red', 'size':10}, name='Outliers')
x_ids = np.arange(len(y))
model = Polynomial.fit(x_ids, y, deg=trend_degree)
y_trend = model(x_ids)
fig.add_scatter(x=x, y=y_trend, mode='lines', name='Trendline')
fig.update_layout(margin={'t':0, 'b':0, 'l':0, 'r':0})
st.plotly_chart(fig)
report = generate_pdf(mine=mines_selector, mean=selected_mine.get_mean(), std=selected_mine.get_std(), median=selected_mine.get_median(),
            iqr=selected_mine.get_iqr(), fig=fig, x=x[outliers_layer], y=y[outliers_layer])
st.sidebar.download_button(label="Download PDF Report", data=report, file_name=f"Weyland_Yutani_Report_{mines_selector}.pdf", mime="application/pdf", type="primary")