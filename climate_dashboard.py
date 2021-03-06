import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_table

df = pd.read_csv('./data/USCRN_data.csv')
df1 = pd.read_csv('./data/Stapleton.csv')

PAGE_SIZE = 10


app = dash.Dash()

station_options = []
for station in df['station'].unique():
    station_options.append({'label':str(station), 'value':station})

year_options = []
for YEAR in df1['YEAR'].unique():
    year_options.append({'label':(YEAR), 'value':YEAR})

# year_options = []
# for year in df1['YEAR'].unique():
#     year_options.append({'label':str(year),'value':year})

month_options = []
for month in df1['MONTH'].unique():
    month_options.append({'label':(month), 'value':month})

app.layout = html.Div([

    html.Div([
        html.H3('Denver Max Daily Temp', style={'align': 'center', 'color': 'blue'}),
        dcc.Graph(id='graph'),
            html.Div([
                dcc.Dropdown(id='year-picker1',options=year_options,value=df1['YEAR'].min()),
            ],
            style={'width': '48%', 'display': 'inline-block'}), 
            html.Div([
                dcc.Dropdown(id='year-picker2',options=year_options,value=df1['YEAR'].min()),
            ],
            style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
            html.Div([
                dcc.RadioItems(id='month-picker1',options=month_options,value=df1['MONTH']),
            ],
            style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.RadioItems(id='month-picker2',options=month_options,value=df1['MONTH']),
            ],
            style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

            html.H4('Datatable'),
            html.Div([
                dash_table.DataTable(
                        id='table-multicol-sorting',
                        columns=[
                            {"name": i, "id": i} for i in sorted(df1.columns)
                        ],
                        pagination_settings={
                            'current_page': 0,
                            'page_size': PAGE_SIZE
                        },
                        pagination_mode='be',

                        sorting='be',
                        sorting_type='multi',
                        sorting_settings=[]
                    )
            ])
    ]),

    html.Div([
        html.H3('USCRN Monthly Max Temp', style={'align': 'center', 'color': 'blue'}),
        dcc.Graph(id='max_graph'),
        html.Label('Dropdown'),
        dcc.Dropdown(
            id='station-picker-max',
            options=station_options,value=df['station'],
            placeholder = "Select Station",
        ),
    ]),

    html.Div([
        html.H3('USCRN Monthly Min Temp'),
        dcc.Graph(id='min_graph'),
        html.Label('Dropdown'),
        dcc.Dropdown(
            id='station-picker-min',
            options=station_options,value=df['station'],
            placeholder = "Select Station",
        ),
    ]),

    html.Div([
        dcc.Graph(id='stapleton'),
        html.Label('denver'),
        dcc.Dropdown(
            id='denver-year-picker',
            options=year_options,value=df1['YEAR'],
        )
    ])

])

@app.callback(Output('graph', 'figure'),
              [Input('year-picker1', 'value'),
               Input('year-picker2', 'value'),
               Input('month-picker1', 'value'),
               Input('month-picker2', 'value')])
def update_figure(selected_year1, selected_year2, selected_month1, selected_month2):
    filtered_df1 = df1[df1['YEAR'] == selected_year1]
    filtered_df2 = df1[df1['YEAR'] == selected_year2]
    traces = []
    for selected_month1 in filtered_df1['MONTH'].unique():
        df_by_month = filtered_df1[filtered_df1['MONTH'] == selected_month1]
        traces.append(go.Scatter(
            x=df_by_month['DAY'],
            y=df_by_month['TMAX'],
            text=df_by_month['NAME'],
            mode='markers + lines',
            opacity=0.7,
            marker={'size': 5},
            name=selected_year1
        ))
    for selected_month2 in filtered_df2['MONTH'].unique():
        df_by_month = filtered_df2[filtered_df2['MONTH'] == selected_month2]
        traces.append(go.Scatter(
            x=df_by_month['DAY'],
            y=df_by_month['TMAX'],
            text=df_by_month['NAME'],
            mode='markers + lines',
            opacity=0.7,
            marker={'size': 5},
            name=selected_year2
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'TIME'},
            yaxis={'title': 'TMAX'},
            hovermode='closest'
        )
    }

@app.callback(
    Output('table-multicol-sorting', "data"),
    [Input('table-multicol-sorting', "pagination_settings"),
     Input('table-multicol-sorting', "sorting_settings")])
def update_graph(pagination_settings, sorting_settings):
    print(sorting_settings)
    if len(sorting_settings):
        dff = df1.sort_values(
            [col['column_id'] for col in sorting_settings],
            ascending=[
                col['direction'] == 'asc'
                for col in sorting_settings
            ],
            inplace=False
        )
    else:
        # No sort is applied
        dff = df1

    return dff.iloc[
        pagination_settings['current_page']*pagination_settings['page_size']:
        (pagination_settings['current_page'] + 1)*pagination_settings['page_size']
    ].to_dict('rows')

@app.callback(Output('max_graph', 'figure'),
        [Input('station-picker-max', 'value')])
def update_figure(selected_station):
    filtered_df = df[df['station'] == selected_station]
    traces = []
    for station_name in filtered_df['station'].unique():
        df_by_station = filtered_df[filtered_df['station'] == station_name]
        traces.append(go.Scatter(
            x=df_by_station['RUN_MON'],
            y=df_by_station['T_MAX'],
            text=df_by_station['station'],
            mode='markers+lines',
            opacity=0.7,
            marker={'size': 5},
            name=station_name
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Running Total Months'},
            yaxis={'title': 'Temp in Deg C'},
            hovermode='closest'
        )
    }


@app.callback(Output('min_graph', 'figure'),
        [Input('station-picker-min', 'value')])
def update_figure(selected_station):
    filtered_df = df[df['station'] == selected_station]
    traces = []
    for station_name in filtered_df['station'].unique():
        df_by_station = filtered_df[filtered_df['station'] == station_name]
        traces.append(go.Scatter(
            x=df_by_station['RUN_MON'],
            y=df_by_station['T_MIN'],
            text=df_by_station['station'],
            mode='markers+lines',
            opacity=0.7,
            marker={'size': 5},
            name=station_name
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Running Total Months'},
            yaxis={'title': 'Temp in Deg C'},
            hovermode='closest'
        )
    }

@app.callback(Output('stapleton', 'figure'),
        [Input('denver-year-picker', 'value')])
def update_figure(selected_year):
    filtered_df1 = df1[df1['YEAR'] == selected_year]
    traces = []
    for year in filtered_df1['YEAR'].unique():
        df1_by_year = filtered_df1[filtered_df1['YEAR'] == year]
        traces.append(go.Scatter(
            x=df1_by_year['MONTH'],
            y=df1_by_year['TMAX'],
            text=df1_by_year['YEAR'],
            mode='markers+lines',
            opacity=0.7,
            marker={'size': 5},
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Running Total Months'},
            yaxis={'title': 'Temp in Deg F'},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server()