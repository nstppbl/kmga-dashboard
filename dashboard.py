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

# Современный CSS стилизация
st.markdown("""
<style>
    /* Чистый современный дизайн */
    .main {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Стильные KPI карточки */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.2s;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .stMetric label {
        color: #6c757d;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #212529;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        color: #28a745;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }
    
    /* Заголовки */
    h1, h2, h3 {
        color: #212529;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Sidebar */
    .stSidebar {
        background: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    .stSelectbox label, .stRadio label, .stCheckbox label {
        color: #495057;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Улучшенные элементы формы */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    .stRadio > div {
        gap: 0.5rem;
    }
    
    /* Скрываем элементы Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Улучшаем таблицы */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Убираем предупреждения по умолчанию */
    .stAlert {
        display: none;
    }
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
    df_aggregated = df.groupby([
        'Employee', 
        'Project_No', 
        'Client', 
        'Activity', 
        'Project_Description'
    ])['Hours'].sum().reset_index()
    
    # Создаем метки проектов - более четкие с Client и Project_Description
    df_aggregated['Project_Label'] = (
        df_aggregated['Client'] + ' - ' + 
        df_aggregated['Project_No'] + ' | ' + 
        df_aggregated['Project_Description'].str[:60]
    )
    df_aggregated['Project_Full_Label'] = (
        df_aggregated['Client'] + ' - ' + 
        df_aggregated['Project_No'] + '<br>' + 
        df_aggregated['Project_Description']
    )
    
    # Проверка на дубликаты (Employee + Project_No)
    duplicates_check = df_aggregated.duplicated(subset=['Employee', 'Project_No'], keep=False)
    duplicates_df = df_aggregated[duplicates_check].copy() if duplicates_check.any() else pd.DataFrame()
    
    return df_aggregated, duplicates_df

# Загрузка данных
df, duplicates_df = load_data()

# Показываем дубликаты если они есть
if not duplicates_df.empty:
    with st.expander("⚠️ Найдены потенциальные дубликаты", expanded=False):
        st.dataframe(
            duplicates_df[['Employee', 'Project_No', 'Client', 'Project_Description', 'Hours']].sort_values(['Employee', 'Project_No']),
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Всего найдено {len(duplicates_df)} записей с дублирующимися комбинациями Employee + Project_No")

# Красивый заголовок
st.markdown("""
<div style='text-align: center; padding: 2rem 0 1rem 0;'>
    <h1 style='color: #212529; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;'>
        KMGA Analytics Dashboard
    </h1>
    <p style='color: #6c757d; font-size: 1.1rem; font-weight: 400;'>
        Оперативная аналитика ресурсов
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar с фильтрами
st.sidebar.markdown("""
<div style='padding: 1rem 0; border-bottom: 2px solid #e9ecef; margin-bottom: 1.5rem;'>
    <h3 style='color: #212529; font-size: 1.2rem; font-weight: 700; margin: 0;'>Фильтры</h3>
</div>
""", unsafe_allow_html=True)

# Получаем уникальные значения
unique_projects = sorted(df['Project_No'].unique().tolist())
unique_employees = sorted(df['Employee'].unique().tolist())

# Фильтры в sidebar
selected_project = st.sidebar.selectbox(
    "📁 Проект",
    options=['Все проекты'] + unique_projects,
    index=0,
    label_visibility="visible"
)

selected_employee = st.sidebar.selectbox(
    "👤 Сотрудник",
    options=['Все сотрудники'] + unique_employees,
    index=0,
    label_visibility="visible"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

chart_type = st.sidebar.radio(
    "📊 Тип графика",
    options=['Bar Chart', 'Pie Chart', 'Line Chart', 'Heatmap', 'Treemap'],
    index=1,
    label_visibility="visible"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Дополнительные опции
show_tables = st.sidebar.checkbox("📋 Показать таблицы", value=False)
export_data = st.sidebar.checkbox("💾 Экспорт данных", value=False)

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

# Стильные KPI Cards
st.markdown("<br>", unsafe_allow_html=True)
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
        delta=f"{top_project_hours:,.0f} ч"
    )

with col5:
    st.metric(
        label="📊 Средняя загрузка",
        value=f"{avg_hours_per_employee:.1f}",
        delta="ч/сотрудник"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Основной график с современным дизайном
st.markdown("""
<div style='padding: 1rem 0;'>
    <h2 style='color: #212529; font-size: 1.5rem; font-weight: 700; margin: 0;'>Основная визуализация</h2>
</div>
""", unsafe_allow_html=True)

# Современная цветовая палитра (приглушенные, но красивые цвета)
modern_colors = [
    '#4A90E2',  # Синий
    '#50C878',  # Зеленый
    '#FF6B6B',  # Красный
    '#FFA500',  # Оранжевый
    '#9B59B6',  # Фиолетовый
    '#1ABC9C',  # Бирюзовый
    '#E74C3C',  # Коралловый
    '#3498DB',  # Голубой
    '#F39C12',  # Желтый
    '#16A085',  # Изумрудный
    '#E67E22',  # Морковный
    '#95A5A6',  # Серый
    '#34495E',  # Темно-серый
    '#2ECC71',  # Светло-зеленый
    '#8E44AD',  # Темно-фиолетовый
    '#C0392B',  # Темно-красный
    '#D35400'   # Темно-оранжевый
]

# Градиентная палитра для pie chart
pie_colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel

if chart_type == 'Bar Chart':
    # Stacked Bar Chart
    fig = go.Figure()

    employees = sorted(filtered_df['Employee'].unique())
    for i, emp in enumerate(employees):
        emp_data = filtered_df[filtered_df['Employee'] == emp]
        temp = emp_data.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
        fig.add_trace(go.Bar(
            x=temp['Project_Label'],
            y=temp['Hours'],
            name=emp,
            marker_color=modern_colors[i % len(modern_colors)],
            text=[f'{h:,.0f}' for h in temp['Hours']],
            textposition='outside',
            textfont=dict(size=10, color='#495057'),
            hovertemplate='<b>%{fullData.name}</b><br>Проект: %{x}<br>Часы: %{y:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="Часы",
        barmode='stack',
        template='plotly_white',
        height=650,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10, color='#495057'),
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#e9ecef',
            borderwidth=1
        ),
        xaxis=dict(
            categoryorder='total descending',
            tickfont=dict(size=10, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6',
            showgrid=True
        ),
        yaxis=dict(
            tickfont=dict(size=10, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6',
            showgrid=True
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=220, t=30, b=120)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif chart_type == 'Pie Chart':
    # Pie Chart (Donut) с улучшенным дизайном
    proj_sum = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
    proj_sum = proj_sum.sort_values('Hours', ascending=False)
    
    # Группируем маленькие проекты в "Другие"
    if len(proj_sum) > 10:
        top_10 = proj_sum.head(10)
        others = proj_sum.tail(len(proj_sum) - 10)
        others_sum = others['Hours'].sum()
        if others_sum > 0:
            top_10 = pd.concat([top_10, pd.DataFrame([{
                'Project_No': 'OTHER',
                'Project_Label': 'Другие проекты',
                'Hours': others_sum
            }])], ignore_index=True)
        proj_sum = top_10
    
    fig = go.Figure(data=[go.Pie(
        labels=proj_sum['Project_Label'],
        values=proj_sum['Hours'],
        hole=0.5,
        textinfo='percent+label',
        textposition='outside',
        textfont=dict(size=11, color='#495057'),
        marker=dict(
            colors=pie_colors[:len(proj_sum)],
            line=dict(color='#ffffff', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<br>Доля: %{percent}<extra></extra>',
        rotation=90
    )])
    
    fig.update_layout(
        title="",
        template='plotly_white',
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.15,
            font=dict(size=10, color='#495057'),
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#e9ecef',
            borderwidth=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=280, t=30, b=50)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif chart_type == 'Line Chart':
    # Line Chart с градиентом
    project_hours_df = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
    project_hours_sorted = project_hours_df.sort_values('Hours', ascending=False)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=project_hours_sorted['Project_Label'],
        y=project_hours_sorted['Hours'],
        mode='lines+markers',
        name='Часы',
        line=dict(width=3, color='#4A90E2', shape='spline'),
        marker=dict(size=10, color='#4A90E2', line=dict(width=2, color='white')),
        fill='tonexty',
        fillcolor='rgba(74, 144, 226, 0.15)',
        text=[f'{h:,.0f}' for h in project_hours_sorted['Hours']],
        textposition='top center',
        textfont=dict(size=9, color='#495057'),
        hovertemplate='<b>Проект:</b> %{x}<br><b>Часы:</b> %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="Часы",
        template='plotly_white',
        height=550,
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6',
            showgrid=True
        ),
        yaxis=dict(
            tickfont=dict(size=10, color='#6c757d'),
            gridcolor='#f1f3f5',
            linecolor='#dee2e6',
            showgrid=True
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=60, r=50, t=30, b=150)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif chart_type == 'Heatmap':
    # Heatmap с улучшенной цветовой схемой
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
        colorscale=[[0, '#f8f9fa'], [0.3, '#e3f2fd'], [0.6, '#4A90E2'], [1, '#1e5aa8']],
        text=[[f'{val:.0f}' if val > 0 else '' for val in row] for row in pivot_table.values],
        texttemplate='%{text}',
        textfont=dict(size=9, color='white'),
        hovertemplate='<b>Сотрудник:</b> %{y}<br><b>Проект:</b> %{x}<br><b>Часы:</b> %{z:,.0f}<extra></extra>',
        showscale=True,
        colorbar=dict(
            title="Часы",
            titlefont=dict(size=10, color='#495057'),
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
            tickfont=dict(size=9, color='#6c757d'),
            gridcolor='#f1f3f5'
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=10, color='#6c757d'),
            gridcolor='#f1f3f5'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=150, r=80, t=30, b=200)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif chart_type == 'Treemap':
    # Treemap с улучшенной цветовой схемой
    treemap_data = filtered_df.groupby(['Client', 'Project_No', 'Project_Label', 'Employee'])['Hours'].sum().reset_index()
    
    fig = px.treemap(
        treemap_data,
        path=[px.Constant("Все"), 'Client', 'Project_Label', 'Employee'],
        values='Hours',
        title="",
        color='Hours',
        color_continuous_scale='Blues',
        template='plotly_white'
    )
    
    fig.update_layout(
        height=650,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Часы: %{value:,.0f}<extra></extra>',
        textfont=dict(size=11, color='white'),
        textposition='middle center',
        texttemplate='%{label}<br>%{value:,.0f} ч',
        marker=dict(line=dict(color='white', width=2))
    )
    
    # Исправляем обновление colorbar для treemap
    if hasattr(fig.layout, 'coloraxis'):
        fig.update_layout(
            coloraxis_colorbar=dict(
                title="Часы",
                titlefont=dict(size=10, color='#495057'),
                tickfont=dict(size=9, color='#495057')
            )
        )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Опциональные таблицы
if show_tables:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding: 1rem 0;'>
        <h2 style='color: #212529; font-size: 1.5rem; font-weight: 700; margin: 0;'>Дополнительная информация</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Топ-10 проектов**")
        top_projects = filtered_df.groupby(['Project_No', 'Project_Label'])['Hours'].sum().reset_index()
        top_projects = top_projects.sort_values('Hours', ascending=False).head(10)
        st.dataframe(
            top_projects[['Project_Label', 'Hours']].rename(columns={'Project_Label': 'Проект', 'Hours': 'Часы'}),
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    with col2:
        st.markdown("**👥 Топ-10 сотрудников**")
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
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding: 1rem 0;'>
        <h2 style='color: #212529; font-size: 1.5rem; font-weight: 700; margin: 0;'>Экспорт данных</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # CSV экспорт
    csv = filtered_df[['Employee', 'Project_No', 'Project_Label', 'Client', 'Activity', 'Hours']].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Скачать CSV",
        data=csv,
        file_name=f"kmga_data_{selected_project}_{selected_employee}.csv",
        mime="text/csv",
        use_container_width=True
    )
