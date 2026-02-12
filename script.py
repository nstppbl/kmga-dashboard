import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# 1. Загрузка и подготовка данных
with open('data.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)
df = pd.DataFrame(raw['data'])

# Группируем данные, чтобы не было "каши"
df_res = df.groupby(['Project_No', 'Project_Description', 'Employee'])['Hours'].sum().reset_index()

# 2. Создаем макет: Сверху общая загрузка, снизу детализация по задачам
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("<b>Распределение ресурсов по проектам</b>", "<b>Структура трудозатрат отдела (%)</b>"),
    vertical_spacing=0.15,
    specs=[[{"type": "bar"}], [{"type": "pie"}]]
)

# --- ГРАФИК 1: Stacked Bar (Информативный) ---
# Мы объединяем номер и описание проекта для оси X
df_res['Label'] = df_res['Project_No'] + "<br>" + df_res['Project_Description'].str[:20] + "..."

for emp in df_res['Employee'].unique():
    temp = df_res[df_res['Employee'] == emp]
    fig.add_trace(
        go.Bar(
            x=temp['Label'], 
            y=temp['Hours'], 
            name=emp,
            text=temp['Hours'],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Сотрудник: " + emp + "<br>Часов: %{y}<extra></extra>"
        ),
        row=1, col=1
    )

# --- ГРАФИК 2: Donut Chart (Общая картина) ---
proj_totals = df.groupby('Project_Description')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(
        labels=proj_totals['Project_Description'], 
        values=proj_totals['Hours'], 
        hole=.4,
        legendgroup="projects",
        legendgrouptitle_text="Проекты:"
    ),
    row=2, col=1
)

# 3. Настройка оформления (Best Practices)
fig.update_layout(
    height=1000,
    barmode='stack',
    title_text="<b>KMGA Resource Management Dashboard</b>",
    template="plotly_white",
    legend_tracegroupgap=20,
    showlegend=True
)

# Для теста в Colab: fig.show()
fig.write_html('index.html')