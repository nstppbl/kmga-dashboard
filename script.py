import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# 1. Загрузка данных
print("📊 Загрузка данных...")
with open('data.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

df = pd.DataFrame(raw['data'])

# Очистка: только записи с часами > 0
df = df[df['Hours'] > 0].copy()

# Улучшение данных
df['Employee'] = df['Employee'].str.strip()
df['Project_No'] = df['Project_No'].str.strip()
df['Client'] = df['Client'].str.strip()
df['Activity'] = df['Activity'].str.strip()

# Улучшенная маркировка проектов
df['Project_Name'] = df['Project_No'] + "<br>" + df['Project_Description'].str[:30] + "..."

print(f"✅ Данные загружены: {len(df)} записей")

# 2. Создаем дашборд с несколькими графиками
print("📈 Создание графиков...")

# Создаем subplots: 3 строки, 2 колонки
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "<b>Затраты времени по сотрудникам (Stacked Bar)</b>",
        "<b>Доли проектов в общих часах (%)</b>",
        "<b>Сравнение проектов (Line Chart)</b>",
        "<b>Распределение по клиентам (%)</b>",
        "<b>Heatmap: Сотрудники × Проекты</b>",
        "<b>Распределение по активностям (%)</b>"
    ),
    vertical_spacing=0.12,
    horizontal_spacing=0.1,
    specs=[
        [{"type": "bar"}, {"type": "pie"}],
        [{"type": "scatter"}, {"type": "pie"}],
        [{"type": "heatmap"}, {"type": "pie"}]
    ]
)

# График 1: Stacked Bar Chart - затраты по сотрудникам
for emp in sorted(df['Employee'].unique()):
    temp = df[df['Employee'] == emp].groupby('Project_No')['Hours'].sum().reset_index()
    fig.add_trace(
        go.Bar(
            x=temp['Project_No'],
            y=temp['Hours'],
            name=emp,
            text=temp['Hours'],
            textposition='auto',
            hovertemplate='<b>%{fullData.name}</b><br>Проект: %{x}<br>Часы: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )

# График 2: Pie Chart - доли проектов
proj_sum = df.groupby('Project_No')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(
        labels=proj_sum['Project_No'],
        values=proj_sum['Hours'],
        hole=0.4,
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>'
    ),
    row=1, col=2
)

# График 3: Line Chart - сравнение проектов
project_hours_sorted = df.groupby('Project_No')['Hours'].sum().sort_values(ascending=False)
fig.add_trace(
    go.Scatter(
        x=project_hours_sorted.index,
        y=project_hours_sorted.values,
        mode='lines+markers',
        name='Часы',
        line=dict(width=3, color='#667eea', shape='spline'),
        marker=dict(size=10, color='#764ba2', line=dict(width=2, color='white')),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)',
        hovertemplate='<b>Проект:</b> %{x}<br><b>Часы:</b> %{y:,.0f}<extra></extra>'
    ),
    row=2, col=1
)

# График 4: Pie Chart - распределение по клиентам
client_sum = df.groupby('Client')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(
        labels=client_sum['Client'],
        values=client_sum['Hours'],
        hole=0.4,
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>'
    ),
    row=2, col=2
)

# График 5: Heatmap - Сотрудники × Проекты
pivot_data = df.groupby(['Employee', 'Project_No'])['Hours'].sum().reset_index()
pivot_table = pivot_data.pivot(index='Employee', columns='Project_No', values='Hours').fillna(0)
fig.add_trace(
    go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='YlOrRd',
        text=pivot_table.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 10},
        hovertemplate='<b>Сотрудник:</b> %{y}<br><b>Проект:</b> %{x}<br><b>Часы:</b> %{z:,.0f}<extra></extra>'
    ),
    row=3, col=1
)

# График 6: Pie Chart - распределение по активностям
activity_sum = df.groupby('Activity')['Hours'].sum().reset_index()
fig.add_trace(
    go.Pie(
        labels=activity_sum['Activity'],
        values=activity_sum['Hours'],
        hole=0.4,
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>'
    ),
    row=3, col=2
)

# 3. Оформление для руководства
fig.update_layout(
    height=1500,
    barmode='stack',  # Сотрудники один над другим
    title_text="<b>KMGA: Оперативная аналитика ресурсов</b>",
    template="plotly_white",
    showlegend=True,
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
)

# Обновляем оси для каждого subplot
fig.update_xaxes(title_text="Проект", row=1, col=1, categoryorder='total descending')
fig.update_yaxes(title_text="Часы", row=1, col=1)
fig.update_xaxes(title_text="Проект", row=2, col=1)
fig.update_yaxes(title_text="Часы", row=2, col=1)
fig.update_xaxes(title_text="Проект", row=3, col=1)
fig.update_yaxes(title_text="Сотрудник", row=3, col=1)

print("✅ Графики созданы")

# 4. Генерируем HTML
print("🌐 Генерация HTML файла...")
fig.write_html('index.html')
print("✅ HTML файл создан: index.html")
print("🌐 Файл готов для размещения на GitHub Pages!")
print("\n💡 Откройте index.html в браузере для просмотра дашборда")
