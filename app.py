
# coding: utf-8

# In[1]:

#Import data from Eurostat for dashboard
import pandas as pd
df = pd.read_csv('nama_10_gdp_1_Data.csv')


# In[2]:

#Show data
df.head()


# In[ ]:

#Define variables
available_indicators=df['NA_ITEM'].unique()
countries=df['GEO'].unique()


# In[ ]:

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__)
server = app.server

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div([

    #First graph
    ### a) scatterplot with two DropDown boxes for the different indicators
    ### b) slide for the different years in the data
    
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            ),
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            ),
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.Slider(
        id='year--slider',
        min=df['TIME'].min(),
        max=df['TIME'].max(),
        value=df['TIME'].max(),
        step=None,
        marks={str(year): str(year) for year in df['TIME'].unique()} 
    ),
 
    #Second graph
    ### Line chart
    ### Drop down box for country and indicator
 
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='series',
                options=[{'label': i, 'value': i} for i in countries],
                value='Spain'
            ),
        ],
        style={'width': '48%', 'marginTop': 40, 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column2',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            ),
        ],style={'width': '48%', 'marginTop': 40, 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-year-graphic'),

])
 
@app.callback( #first graph
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 year_value):
    dff = df[df['TIME'] == year_value]
    
    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == xaxis_column_name]['Value'],
            y=dff[dff['NA_ITEM'] == yaxis_column_name]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_column_name]['GEO'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
            },
            yaxis={
                'title': yaxis_column_name,
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }
 

@app.callback( #second graph
    dash.dependencies.Output('indicator-year-graphic', 'figure'),
    [dash.dependencies.Input('series', 'value'),
     dash.dependencies.Input('yaxis-column2', 'value')])
def update_graph(series_name, yaxis_column_name2):
    
    dff = df[df['GEO'] == series_name]
    dff = dff[dff['UNIT']=='Chain linked volumes, index 2010=100']  
    
    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == yaxis_column_name2]['TIME'],
            y=dff[dff['NA_ITEM'] == yaxis_column_name2]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_column_name2]['GEO'],
            mode='lines',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': 'Year',
            },
            yaxis={
                'title': yaxis_column_name2,
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server()


