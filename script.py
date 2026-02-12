import pandas as pd
import plotly.express as px
import json
import os

# 1. Читаем данные из JSON
with open('data.json', 'r', encoding='utf-8') as f:
    raw_json = json.load(f)

# 2. Вытаскиваем список из ключа 'data'
df = pd.DataFrame(raw_json['data']) 

# 3. Строим график (остальное без изменений)
fig = px.bar(df, x='Project_No', y='Hours', color='Employee', barmode='group')
fig.write_html('index.html')
