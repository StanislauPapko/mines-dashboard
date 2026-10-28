import pandas as pd
from fpdf import FPDF
import plotly.graph_objects as go
import io

def print_line(pdf:FPDF ,text:str):
    pdf.cell(0, 10, text, new_x='LMARGIN', new_y='NEXT')

def next_line(pdf:FPDF):
    pdf.ln(5)

def print_anomaly_summary(pdf:FPDF, data:pd.DataFrame, type:str):
    print_line(pdf, text=f"Total number of {type}: {len(data)}")
    if not data.empty:
        for _, row in data.iterrows():
            date_str = str(row['Date']).split()[0]
            print_line(pdf, text=f"- {date_str}: {row['Extraction']:.2f} units extracted")

def generate_pdf(mine:str, mean:float, std:float, median:float, iqr:float, fig:go.Figure, x:pd.Series, y:pd.Series) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", "B", 18)
    print_line(pdf=pdf, text=f"Weyland-Yutani Corporation Extraction Report: {mine}")
    pdf.set_font("Times", "B", 14)
    print_line(pdf=pdf, text="1.Descriptive Statistics")
    pdf.set_font("Times", "", 12)
    print_line(pdf=pdf, text=f"- Mean: {mean}")
    print_line(pdf=pdf, text=f"- Standard Deviation: {std}")
    print_line(pdf=pdf, text=f"- Median: {median}")
    print_line(pdf=pdf, text=f"- IQR: {iqr}")
    pdf.set_font("Times", "B", 14)
    print_line(pdf=pdf, text="2.Chart")
    fig.update_layout(template="plotly_white")
    image = fig.to_image(format='png', width=1000, height=500, scale=2)
    pdf.image(io.BytesIO(image), w=190)
    pdf.set_font("Times", "B", 14)
    print_line(pdf=pdf, text="3.Anomalies")
    df = pd.DataFrame({'Date': x, 'Extraction': y})
    spikes = df[df['Extraction'] > median]
    drops = df[df['Extraction'] < median]
    pdf.set_font("Times", "", 12)
    print_anomaly_summary(pdf=pdf, data=spikes, type='spikes')
    print_anomaly_summary(pdf=pdf, data=drops, type='drops')
    return bytes(pdf.output())