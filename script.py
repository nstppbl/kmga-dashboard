import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# 1. Загрузка данных
with open('data.json', 'r', encoding='utf-8') as f:
    raw_json = json.load(f)
df = pd.DataFrame(raw_json['data'])

# 2. Группировка для итоговой аналитики
df_grouped = df.groupby(['Project_No', 'Employee', 'Project_Description'])['Hours'].sum().reset_index()
# Сортируем проекты по общему количеству часов
df_grouped = df_grouped.sort_values(by='Hours', ascending=False)

# 3. Создаем дашборд
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Загрузка инженеров по проектам (Stacked)", "Общее распределение времени"),
    vertical_spacing=0.2,
    specs=[[{"type": "bar"}], [{"type": "pie"}]]
)

# Добавляем Stacked Bar (один столбик - один проект, внутри - люди)
for employee in df_grouped['Employee'].unique():
    temp = df_grouped[df_grouped['Employee'] == employee]
    fig.add_trace(
        go.Bar(x=temp['Project_No'], y=temp['Hours'], name=employee, 
               text=temp['Hours'], textposition='auto'),
        row=1, col=1
    )

# Добавляем Pie Chart
proj_total = df_grouped.groupby('Project_Description')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(labels=proj_total['Project_Description'], values=proj_total['Hours'], hole=.3),
    row=2, col=1
)

# Оформление
fig.update_layout(
    height=1000, 
    barmode='stack', 
    title_text="KMGA Dashboard: Аналитика ресурсов",
    template="plotly_white"
)

fig.write_html('index.html')