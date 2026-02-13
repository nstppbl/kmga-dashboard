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

# Минималистичная CSS стилизация
st.markdown("""
<style>
    /* Минималистичная цветовая схема */
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #e9ecef;
    }
    .stMetric label {
        color: #6c757d;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #212529;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #495057;
        font-size: 0.75rem;
    }
    h1, h2, h3 {
        color: #212529;
        font-weight: 600;
    }
    .stSidebar {
        background-color: #ffffff;
    }
    .stSelectbox label, .stRadio label {
        color: #495057;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .stDataFrame {
        font-size: 0.85rem;
    }
    /* Скрываем некоторые элементы Streamlit по умолчанию */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Загрузка данных с правильной агрегацией
@st.cache_data
def load_data():
    """Загрузка и предобработка данных с исправленной агрегацией"""
    with open('data.json', 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    df = pd.DataFrame(raw['data'])
    
    # Фильтруем только положительные часы
    df = df[df['Hours'] > 0].copy()
    
    # Очистка данных
    df['Employee'] = df['Employee'].str.strip()
    df['Project_No'] = df['Project_No'].str.strip()
    df['Client'] = df['Client'].str.strip()
    df['Activity'] = df['Activity'].str.strip()
    df['Project_Description'] = df['Project_Description'].str.strip()
    
    # Исправленная агрегация: убираем дубликаты перед группировкой
    # Группируем по уникальной комбинации всех полей и суммируем часы
    df_aggregated = df.groupby([
        'Employee', 
        'Project_No', 
        'Client', 
        'Activity', 
        'Project_Description'
    ])['Hours'].sum().reset_index()
    
    # Проверка на дубликаты (для отладки)
    duplicates = df_aggregated.duplicated(subset=['Employee', 'Project_No']).sum()
    if duplicates > 0:
        st.warning(f"⚠️ Найдено {duplicates} потенциальных дубликатов")
    
    # Создаем метки проектов
    df_aggregated['Project_Label'] = df_aggregated['Client'] + ' - ' + df_aggregated['Project_No']
    df_aggregated['Project_Full_Label'] = (
        df_aggregated['Client'] + ' - ' + 
        df_aggregated['Project_No'] + '<br>' + 
        df_aggregated['Project_Description'].str[:50]
    )
    
    return df_aggregated

# Загрузка данных
df = load_data()

# Минималистичный заголовок
st.markdown("### KMGA Analytics Dashboard")
st.caption("Оперативная аналитика ресурсов")

# Sidebar с минималистичными фильтрами
st.sidebar.markdown("### Фильтры")

# Получаем уникальные значения
unique_projects = sorted(df['Project_No'].unique().tolist())
unique_employees = sorted(df['Employee'].unique().tolist())

# Фильтры в sidebar
selected_project = st.sidebar.selectbox(
    "Проект",
    options=['Все проекты'] + unique_projects,
    index=0,
    label_visibility="visible"
)

selected_employee = st.sidebar.selectbox(
    "Сотрудник",
    options=['Все сотрудники'] + unique_employees,
    index=0,
    label_visibility="visible"
)

chart_type = st.sidebar.radio(
    "Тип графика",
    options=['Bar Chart', 'Pie Chart', 'Line Chart', 'Heatmap', 'Treemap'],
    index=0,
    label_visibility="visible"
)

# Дополнительные опции
show_tables = st.sidebar.checkbox("Показать таблицы", value=False)
export_data = st.sidebar.checkbox("Экспорт данных", value=False)

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

# Топ проект
project_hours = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
if len(project_hours) > 0:
    top_project_row = project_hours.loc[project_hours['Hours'].idxmax()]
    top_project = top_project_row['Project_No']
    top_project_label = top_project_row['Project_Label']
    top_project_hours = top_project_row['Hours']
else:
    top_project = "N/A"
    top_project_label = "N/A"
    top_project_hours = 0

# Средняя загрузка
avg_hours_per_employee = filtered_df.groupby('Employee')['Hours'].sum().mean() if active_employees > 0 else 0

# Компактные KPI Cards в одну строку
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Общие часы",
        value=f"{total_hours:,.0f}"
    )

with col2:
    st.metric(
        label="Проектов",
        value=active_projects
    )

with col3:
    st.metric(
        label="Сотрудников",
        value=active_employees
    )

with col4:
    st.metric(
        label="Топ проект",
        value=top_project,
        delta=f"{top_project_hours:,.0f} ч"
    )

with col5:
    st.metric(
        label="Средняя загрузка",
        value=f"{avg_hours_per_employee:.1f}",
        delta="ч/сотрудник"
    )

st.divider()

# Основной график с минималистичным дизайном
st.markdown("### Основная визуализация")

# Приглушенная цветовая палитра (серые и синие тона)
minimal_colors = ['#6c757d', '#495057', '#868e96', '#adb5bd', '#ced4da', '#343a40', 
                  '#007bff', '#0056b3', '#004085', '#003d82']

if chart_type == 'Bar Chart':
    # Stacked Bar Chart
    fig = go.Figure()
    
    # Группируем данные правильно
    for emp in sorted(filtered_df['Employee'].unique()):
        emp_data = filtered_df[filtered_df['Employee'] == emp]
        temp = emp_data.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
        fig.add_trace(go.Bar(
            x=temp['Project_Label'],
            y=temp['Hours'],
            name=emp,
            marker_color=minimal_colors[len(fig.data) % len(minimal_colors)],
            text=[f'{h:,.0f}' for h in temp['Hours']],
            textposition='outside',
            textfont=dict(size=9, color='#495057'),
            hovertemplate='<b>%{fullData.name}</b><br>Проект: %{x}<br>Часы: %{y:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="Часы",
        barmode='stack',
        template='plotly_white',
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10, color='#495057'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#e9ecef',
            borderwidth=1
        ),
        xaxis=dict(
            categoryorder='total descending',
            tickfont=dict(size=9, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6'
        ),
        yaxis=dict(
            tickfont=dict(size=9, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=200, t=20, b=100)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif chart_type == 'Pie Chart':
    # Pie Chart (Donut)
    proj_sum = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
    proj_sum = proj_sum.sort_values('Hours', ascending=False)
    
    fig = go.Figure(data=[go.Pie(
        labels=proj_sum['Project_Label'],
        values=proj_sum['Hours'],
        hole=0.4,
        textinfo='percent',
        textposition='outside',
        textfont=dict(size=9, color='#495057'),
        marker=dict(colors=minimal_colors[:len(proj_sum)]),
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="",
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            font=dict(size=9, color='#495057'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#e9ecef',
            borderwidth=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=250, t=20, b=50)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

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
        line=dict(width=2, color='#6c757d', shape='spline'),
        marker=dict(size=8, color='#495057', line=dict(width=1, color='white')),
        fill='tonexty',
        fillcolor='rgba(108, 117, 125, 0.1)',
        text=[f'{h:,.0f}' for h in project_hours_sorted['Hours']],
        textposition='top center',
        textfont=dict(size=8, color='#495057'),
        hovertemplate='<b>Проект:</b> %{x}<br><b>Часы:</b> %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="Часы",
        template='plotly_white',
        height=500,
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=9, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6'
        ),
        yaxis=dict(
            tickfont=dict(size=9, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=50, r=50, t=20, b=150)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif chart_type == 'Heatmap':
    # Heatmap
    pivot_data = filtered_df.groupby(['Employee', 'Project_No', 'Project_Label'])['Hours'].sum().reset_index()
    pivot_table = pivot_data.pivot_table(
        index='Employee', 
        columns='Project_Label', 
        values='Hours', 
        aggfunc='sum'
    ).fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values.tolist(),
        x=pivot_table.columns.tolist(),
        y=pivot_table.index.tolist(),
        colorscale=[[0, '#f8f9fa'], [0.5, '#ced4da'], [1, '#495057']],
        text=[[f'{val:.0f}' if val > 0 else '' for val in row] for row in pivot_table.values],
        texttemplate='%{text}',
        textfont=dict(size=8, color='white'),
        hovertemplate='<b>Сотрудник:</b> %{y}<br><b>Проект:</b> %{x}<br><b>Часы:</b> %{z:,.0f}<extra></extra>',
        showscale=True,
        colorbar=dict(
            title="Часы",
            titlefont=dict(size=9, color='#495057'),
            tickfont=dict(size=9, color='#495057')
        )
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="",
        template='plotly_white',
        height=900,
        xaxis=dict(
            side="bottom",
            tickangle=-45,
            tickfont=dict(size=8, color='#6c757d'),
            gridcolor='#f1f3f5'
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=9, color='#6c757d'),
            gridcolor='#f1f3f5'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=150, r=50, t=20, b=200)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif chart_type == 'Treemap':
    # Treemap
    treemap_data = filtered_df.groupby(['Client', 'Project_No', 'Project_Label', 'Employee'])['Hours'].sum().reset_index()
    
    fig = px.treemap(
        treemap_data,
        path=[px.Constant("Все"), 'Client', 'Project_Label', 'Employee'],
        values='Hours',
        title="",
        color='Hours',
        color_continuous_scale='Greys',
        template='plotly_white'
    )
    
    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<extra></extra>',
        textfont=dict(size=10, color='white'),
        textposition='middle center',
        texttemplate='%{label}<br>%{value:,.0f} ч'
    )
    
    fig.update_coloraxes(
        colorbar=dict(
            title="Часы",
            titlefont=dict(size=9, color='#495057'),
            tickfont=dict(size=9, color='#495057')
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Опциональные таблицы
if show_tables:
    st.divider()
    st.markdown("### Дополнительная информация")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Топ-10 проектов**")
        top_projects = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
        top_projects = top_projects.sort_values('Hours', ascending=False).head(10)
        st.dataframe(
            top_projects[['Project_Label', 'Hours']].rename(columns={'Project_Label': 'Проект', 'Hours': 'Часы'}),
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    with col2:
        st.markdown("**Топ-10 сотрудников**")
        top_employees = filtered_df.groupby('Employee')['Hours'].sum().reset_index()
        top_employees = top_employees.sort_values('Hours', ascending=False).head(10)
        st.dataframe(
            top_employees.rename(columns={'Employee': 'Сотрудник', 'Hours': 'Часы'}),
            use_container_width=True,
            hide_index=True,
            height=400
        )

# Экспорт данных
if export_data:
    st.divider()
    st.markdown("### Экспорт данных")
    
    # CSV экспорт
    csv = filtered_df[['Employee', 'Project_No', 'Project_Label', 'Client', 'Activity', 'Hours']].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Скачать CSV",
        data=csv,
        file_name=f"kmga_data_{selected_project}_{selected_employee}.csv",
        mime="text/csv"
    )
