import pandas as pd
import plotly.express as px
import json
import os

# 1. Читаем данные, которые прислал n8n
with open('data.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 2. Превращаем в таблицу (учитываем структуру n8n)
# Если ты использовал Aggregate, данные могут быть вложены
df = pd.DataFrame([item for item in raw_data])

# 3. Строим интерактивный график загрузки по проектам
fig = px.bar(df, 
             x='Project_No', 
             y='Hours', 
             color='Employee',
             title='Трудозатраты отдела по проектам (KMGA)',
             hover_data=['Project_Description', 'Staff_Comment'],
             barmode='group')

# 4. Сохраняем результат в HTML-файл для GitHub Pages
fig.write_html('index.html')
