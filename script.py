import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# 1. Загрузка данных
with open('data.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)
df = pd.DataFrame(raw['data'])

# 2. Улучшенная маркировка проектов
# Делаем короткое и понятное имя для оси X
df['Project_Name'] = df['Project_No'] + "<br>" + df['Project_Description'].str[:20] + "..."

# 3. Создаем дашборд
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("<b>Затраты времени по сотрудникам (Hours)</b>", "<b>Общее распределение по проектам (%)</b>"),
    vertical_spacing=0.15,
    specs=[[{"type": "bar"}], [{"type": "pie"}]]
)

# График 1: Накопительные столбцы (один проект - один столбик)
for emp in df['Employee'].unique():
    temp = df[df['Employee'] == emp].groupby('Project_Name')['Hours'].sum().reset_index()
    fig.add_trace(
        go.Bar(x=temp['Project_Name'], y=temp['Hours'], name=emp, 
               text=temp['Hours'], textposition='auto'),
        row=1, col=1
    )

# График 2: Круговая диаграмма (Donut)
proj_sum = df.groupby('Project_Description')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(labels=proj_sum['Project_Description'], values=proj_sum['Hours'], hole=.4),
    row=2, col=1
)

# Оформление для руководства
fig.update_layout(
    height=1000,
    barmode='stack', # Сотрудники один над другим
    title_text="<b>KMGA: Оперативная аналитика ресурсов</b>",
    template="plotly_white",
    showlegend=True
)

# Генерируем HTML
fig.write_html('index.html')