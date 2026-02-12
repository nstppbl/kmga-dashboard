import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# 1. Загрузка данных
with open('data.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)
df = pd.DataFrame(raw['data'])

# 2. Подготовка аналитики
# Склеиваем номер и описание для информативности
df['Project_Label'] = df['Project_No'] + "<br><i>" + df['Project_Description'].str.wrap(25).str.replace('\n', '<br>') + "</i>"

# Группируем для графиков
df_res = df.groupby(['Project_Label', 'Employee'])['Hours'].sum().reset_index()

# 3. Создаем дашборд
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("<b>Загрузка по проектам (часы по сотрудникам)</b>", "<b>Общая доля проектов в отделе</b>"),
    vertical_spacing=0.2,
    specs=[[{"type": "bar"}], [{"type": "pie"}]]
)

# График 1: Накопительные столбцы (Stacked Bar)
for emp in df_res['Employee'].unique():
    temp = df_res[df_res['Employee'] == emp]
    fig.add_trace(
        go.Bar(x=temp['Project_Label'], y=temp['Hours'], name=emp, 
               text=temp['Hours'], textposition='inside'),
        row=1, col=1
    )

# График 2: Круговая диаграмма проектов
proj_totals = df.groupby('Project_Description')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(labels=proj_totals['Project_Description'], values=proj_totals['Hours'], hole=.4),
    row=2, col=1
)

# 4. Стилизация
fig.update_layout(
    height=1200, barmode='stack', 
    title_text="<b>KMGA Resource Management Dashboard</b>",
    template="plotly_white"
)

# 5. Генерация финального HTML с таблицей
# Добавляем таблицу комментариев в конец страницы
table_html = df[['Employee', 'Project_No', 'Staff_Comment', 'Hours']].to_html(classes='table', index=False)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write('<html><head><meta charset="UTF-8"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"></head><body>')
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(f'<div class="container"><h3>Детализация задач:</h3>{table_html}</div>')
    f.write('</body></html>')