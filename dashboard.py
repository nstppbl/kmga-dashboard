import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import json

# Настройка страницы
st.set_page_config(
    page_title="KMGA Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Загрузка данных
@st.cache_data
def load_data():
    """Загрузка и предобработка данных"""
    with open('data.json', 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    df = pd.DataFrame(raw['data'])
    df = df[df['Hours'] > 0].copy()
    
    # Очистка данных
    df['Employee'] = df['Employee'].str.strip()
    df['Project_No'] = df['Project_No'].str.strip()
    df['Client'] = df['Client'].str.strip()
    df['Activity'] = df['Activity'].str.strip()
    
    # Правильная агрегация - группируем по всем ключевым полям и суммируем часы
    df_aggregated = df.groupby(['Employee', 'Project_No', 'Client', 'Activity', 'Project_Description'])['Hours'].sum().reset_index()
    
    # Создаем метки проектов
    df_aggregated['Project_Label'] = df_aggregated['Client'] + ' - ' + df_aggregated['Project_No']
    df_aggregated['Project_Full_Label'] = df_aggregated['Client'] + ' - ' + df_aggregated['Project_No'] + '<br>' + df_aggregated['Project_Description'].str[:50]
    
    return df_aggregated

# Загрузка данных
df = load_data()

# Заголовок
st.title("📊 KMGA Analytics Dashboard")
st.markdown("**Оперативная аналитика ресурсов**")

# Sidebar с фильтрами
st.sidebar.header("🔍 Фильтры")

# Получаем уникальные значения
unique_projects = sorted(df['Project_No'].unique().tolist())
unique_employees = sorted(df['Employee'].unique().tolist())

# Фильтры
selected_project = st.sidebar.selectbox(
    "📁 Проект",
    options=['Все проекты'] + unique_projects,
    index=0
)

selected_employee = st.sidebar.selectbox(
    "👤 Сотрудник",
    options=['Все сотрудники'] + unique_employees,
    index=0
)

chart_type = st.sidebar.radio(
    "📊 Тип графика",
    options=['Bar Chart', 'Pie Chart', 'Line Chart', 'Heatmap', 'Treemap'],
    index=0
)

# Фильтрация данных
filtered_df = df.copy()
if selected_project != 'Все проекты':
    filtered_df = filtered_df[filtered_df['Project_No'] == selected_project]
if selected_employee != 'Все сотрудники':
    filtered_df = filtered_df[filtered_df['Employee'] == selected_employee]

# Расчет метрик
total_hours = filtered_df['Hours'].sum()
active_projects = filtered_df['Project_No'].nunique()
active_employees = filtered_df['Employee'].nunique()
project_hours = filtered_df.groupby('Project_No')['Hours'].sum()
top_project = project_hours.idxmax() if len(project_hours) > 0 else "N/A"
top_project_hours = project_hours.max() if len(project_hours) > 0 else 0
avg_hours_per_employee = filtered_df.groupby('Employee')['Hours'].sum().mean() if active_employees > 0 else 0

# KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="⏱️ Общие часы",
        value=f"{total_hours:,.0f}"
    )

with col2:
    st.metric(
        label="📁 Проектов",
        value=active_projects
    )

with col3:
    st.metric(
        label="👥 Сотрудников",
        value=active_employees
    )

with col4:
    st.metric(
        label="🏆 Топ проект",
        value=top_project,
        delta=f"{top_project_hours:,.0f} часов"
    )

with col5:
    st.metric(
        label="📊 Средняя загрузка",
        value=f"{avg_hours_per_employee:.1f}",
        delta="часов на сотрудника"
    )

st.divider()

# Основной график
st.subheader("📈 Основная визуализация")

if chart_type == 'Bar Chart':
    # Stacked Bar Chart
    fig = go.Figure()
    for emp in sorted(filtered_df['Employee'].unique()):
        temp = filtered_df[filtered_df['Employee'] == emp].groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
        fig.add_trace(go.Bar(
            x=temp['Project_Label'],
            y=temp['Hours'],
            name=emp,
            text=[f'{h:,.0f}' for h in temp['Hours']],
            textposition='auto',
            hovertemplate='<b>%{fullData.name}</b><br>Проект: %{x}<br>Часы: %{y:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="<b>Затраты времени по сотрудникам (Stacked Bar)</b>",
        xaxis_title="Проект",
        yaxis_title="Часы",
        barmode='stack',
        template='plotly_white',
        height=600,
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        xaxis={'categoryorder': 'total descending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == 'Pie Chart':
    # Pie Chart
    proj_sum = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
    fig = go.Figure(data=[go.Pie(
        labels=proj_sum['Project_Label'],
        values=proj_sum['Hours'],
        hole=0.4,
        textinfo='percent+label',
        texttemplate='%{label}<br>%{value:,.0f} ч (%{percent})',
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>'
    )])
    fig.update_layout(
        title="<b>Доли проектов в общих часах (%)</b>",
        template='plotly_white',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == 'Line Chart':
    # Line Chart
    project_hours_df = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
    project_hours_sorted = project_hours_df.sort_values('Hours', ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=project_hours_sorted['Project_Label'],
        y=project_hours_sorted['Hours'],
        mode='lines+markers',
        name='Часы',
        line=dict(width=3, color='#667eea', shape='spline'),
        marker=dict(size=10, color='#764ba2', line=dict(width=2, color='white')),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)',
        text=[f'{h:,.0f}' for h in project_hours_sorted['Hours']],
        textposition='top center',
        hovertemplate='<b>Проект:</b> %{x}<br><b>Часы:</b> %{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title="<b>Сравнение проектов (Line Chart)</b>",
        xaxis_title="Проект",
        yaxis_title="Часы",
        template='plotly_white',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == 'Heatmap':
    # Heatmap
    pivot_data = filtered_df.groupby(['Employee', 'Project_No', 'Project_Label'])['Hours'].sum().reset_index()
    pivot_table = pivot_data.pivot_table(index='Employee', columns='Project_Label', values='Hours', aggfunc='sum').fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values.tolist(),
        x=pivot_table.columns.tolist(),
        y=pivot_table.index.tolist(),
        colorscale='YlOrRd',
        text=[[f'{val:.0f}' if val > 0 else '' for val in row] for row in pivot_table.values],
        texttemplate='%{text}',
        textfont={"size": 8, "color": "white"},
        hovertemplate='<b>Сотрудник:</b> %{y}<br><b>Проект:</b> %{x}<br><b>Часы:</b> %{z:,.0f}<extra></extra>',
        showscale=True,
        colorbar=dict(title="Часы")
    ))
    fig.update_layout(
        title="<b>Heatmap: Сотрудники × Проекты</b>",
        xaxis_title="Проект",
        yaxis_title="Сотрудник",
        template='plotly_white',
        height=900,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(side="bottom", tickangle=-45),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=150, r=50, t=50, b=200)
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == 'Treemap':
    # Treemap
    treemap_data = filtered_df.groupby(['Client', 'Project_No', 'Project_Label', 'Employee'])['Hours'].sum().reset_index()
    fig = px.treemap(
        treemap_data,
        path=[px.Constant("Все"), 'Client', 'Project_Label', 'Employee'],
        values='Hours',
        title="<b>Иерархия: Клиент → Проект → Сотрудник</b>",
        color='Hours',
        color_continuous_scale='Viridis',
        template='plotly_white',
        hover_data={'Hours': True}
    )
    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<extra></extra>',
        textfont=dict(size=11, color='white'),
        textposition='middle center',
        texttemplate='%{label}<br>%{value:,.0f} ч'
    )
    st.plotly_chart(fig, use_container_width=True)

# Таблицы и дополнительные графики
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Топ-10 проектов")
    top_projects = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index().sort_values('Hours', ascending=False).head(10)
    st.dataframe(
        top_projects[['Project_Label', 'Hours']].rename(columns={'Project_Label': 'Проект', 'Hours': 'Часы'}),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("👥 Топ-10 сотрудников")
    top_employees = filtered_df.groupby('Employee')['Hours'].sum().sort_values(ascending=False).head(10).reset_index()
    st.dataframe(
        top_employees.rename(columns={'Employee': 'Сотрудник', 'Hours': 'Часы'}),
        use_container_width=True,
        hide_index=True
    )

# Дополнительные графики
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Распределение по клиентам")
    client_sum = filtered_df.groupby('Client')['Hours'].sum().reset_index()
    fig_client = go.Figure(data=[go.Pie(
        labels=client_sum['Client'],
        values=client_sum['Hours'],
        hole=0.4,
        textinfo='percent+label',
        texttemplate='%{label}<br>%{value:,.0f} ч (%{percent})',
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>'
    )])
    fig_client.update_layout(
        template='plotly_white',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_client, use_container_width=True)

with col2:
    st.subheader("⚙️ Распределение по активностям")
    activity_sum = filtered_df.groupby('Activity')['Hours'].sum().reset_index()
    fig_activity = go.Figure(data=[go.Pie(
        labels=activity_sum['Activity'],
        values=activity_sum['Hours'],
        hole=0.4,
        textinfo='percent+label',
        texttemplate='%{label}<br>%{value:,.0f} ч (%{percent})',
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>'
    )])
    fig_activity.update_layout(
        template='plotly_white',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_activity, use_container_width=True)

