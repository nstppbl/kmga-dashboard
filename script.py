import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# 1. Загрузка данных
with open('data.json', 'r', encoding='utf-8') as f:
    raw_json = json.load(f)
df = pd.DataFrame(raw_json['data'])

# 2. Создаем дашборд из двух графиков
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Загрузка сотрудников по проектам (часы)", "Доля проектов в общем объеме работ"),
    vertical_spacing=0.15,
    specs=[[{"type": "bar"}], [{"type": "pie"}]]
)

# График 1: Столбчатая диаграмма (группировка по сотрудникам)
for employee in df['Employee'].unique():
    temp_df = df[df['Employee'] == employee]
    fig.add_trace(
        go.Bar(x=temp_df['Project_No'], y=temp_df['Hours'], name=employee,
               hovertemplate="Проект: %{x}<br>Часы: %{y}<extra></extra>"),
        row=1, col=1
    )

# График 2: Круговая диаграмма по проектам
project_hours = df.groupby('Project_Description')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(labels=project_hours['Project_Description'], values=project_hours['Hours'], hole=.3),
    row=2, col=1
)

# Настройка оформления
fig.update_layout(
    height=900, 
    title_text="Аналитика трудозатрат отдела KMGA",
    showlegend=True,
    barmode='stack' # Столбики теперь будут суммироваться один над другим
)

fig.write_html('index.html')
