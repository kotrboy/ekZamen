import requests
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Загрузка данных
def load_cricket_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json().get("records", []))
    else:
        print(f"Ошибка загрузки: {response.status_code}")
        return pd.DataFrame()

# Конфигурация
DATA_URL = "http://backend:8000/nocodb-data/"
df = load_cricket_data(DATA_URL)

# Проверка и очистка данных
if not df.empty:
    df['Batting_Strike_Rate'] = pd.to_numeric(df['Batting_Strike_Rate'], errors='coerce')
    df['Year'] = df['Year'].astype(int)

# Инициализация Dash
app = dash.Dash(__name__)

# Лейаут приложения
app.layout = html.Div([
    html.H1("Анализ статистики игроков в крикет", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in sorted(df['Year'].unique())],
            value=df['Year'].max(),
            clearable=False,
            style={'width': '50%', 'margin': 'auto'}
        ),
        
        dcc.Graph(id='runs-graph'),
        
        dcc.Graph(id='strike-rate-heatmap',
                 figure=px.imshow(
                     pd.pivot_table(df, values='Batting_Strike_Rate', 
                                   index='Player_Name', columns='Year'),
                     title='Тепловая карта эффективности'
                 ))
    ])
])

# Коллбэки
@app.callback(
    Output('runs-graph', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_graph(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    return px.bar(
        filtered_df.sort_values('Runs_Scored', ascending=False).head(10),
        x='Player_Name', 
        y='Runs_Scored',
        color='Matches_Batted',
        title=f'Топ-10 игроков по очкам ({selected_year} год)',
        labels={'Runs_Scored': 'Набранные очки', 'Player_Name': 'Игрок'}
    )

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')