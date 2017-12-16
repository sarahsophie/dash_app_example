
# coding: utf-8

# In[1]:

#Import data from Eurostat for dashboard
import pandas as pd
df = pd.read_csv('nama_10_gdp_1_Data_from1975.csv')


# In[2]:

#Show data
df.head()


# In[3]:

import numpy as np

#Define variables

#Available indicators
available_indicators=df['NA_ITEM'].unique()
available_indicators==available_indicators.sort() #sort alphabetically

#Countries
countries=df['GEO'].unique()
countries==countries.sort() #sort alphabetically

#Categorize countries into regions
countries_eu = ['European Union (28 countries)', 'European Union (15 countries)',
       'Euro area (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)',
       'Euro area (19 countries)', 'Euro area (18 countries)',
       'Euro area (12 countries)']
Western_Europe=['Belgium','France','Luxembourg','Netherlands','Portugal','United Kingdom','Ireland','Iceland']
Southern_Europe=['Italy','Malta','Portugal','Spain']
Southeastern_Europe=['Albania','Cyprus','Greece','Kosovo (under United Nations Security Council Resolution 1244/99)','Turkey','Albania','Bosnia and Herzegovina','Bulgaria', 'Croatia','Montenegro','Romania', 'Serbia', 'Slovenia','Former Yugoslav Republic of Macedonia, the','Hungary','Slovakia']
Northern_Europe=['Estonia','Latvia','Lithuania','Sweden','Denmark','Norway','Finland']
Central_Europe=['Austria','Germany (until 1990 former territory of the FRG)','Hungary','Liechtenstein','Poland','Switzerland','Czech Republic']

#Create new column that classifies countries into regions
df['GEO_Category'] = np.where(df['GEO'].isin(countries_eu), 'EU',
                        np.where(df['GEO'].isin(Western_Europe),'Western Europe',
                        np.where(df['GEO'].isin(Southern_Europe),'Southern Europe',
                        np.where(df['GEO'].isin(Southeastern_Europe),'Southeastern Europe',
                        np.where(df['GEO'].isin(Northern_Europe),'Northern Europe',
                        np.where(df['GEO'].isin(Central_Europe),'Central Europe',""))))))


# In[ ]:

#Import libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output

#Create the app
#in jupyter notebook: app = dash.Dash()
app = dash.Dash(__name__)
server = app.server

#Style
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

#Design layout of app
app.layout = html.Div([

    #First graph:
    ### a) Scatterplot with two DropDown boxes for the different indicators
    ### b) Slider for the different years in the data
    
    html.Div([
        html.H2(children = 'Correlation between indicators'), #Title for graph 1  
        html.H5(children = 'Click on a data point to see the development for the selected country in detail in the graph below.'),
        html.Div([

            #Create dropdown for x-axis (select indicator)
            html.Label('Select x-axis indicator'), 
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            ),
            
            #Option to choose linear / log representation of values
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            
            #Create dropdown for y-axis (select a second indicator)
            html.Label('Select y-axis indicator'),
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            ),
            
            #Option to choose linear / log representation of values
             dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )           
        ],
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic', #Unique name for graph 1
    clickData={'points': [{'customdata': 'Spain'}]}), #Track clicks on a data point
    
    #Create slider to select year
    html.Div( 
        [html.Label('Select year', style={"text-align":"center"}),
        dcc.Slider( 
        id='year--slider',
        min=df['TIME'].min(),
        max=df['TIME'].max(),
        value=df['TIME'].max(),
        step=1,
        marks={str(year): str(year) for year in df['TIME'].unique()[[0,5,10,15,20,25,30,35,41]]}
    
        )], style={'marginRight': 100, 'marginLeft': 100, 'marginTop':50, 'marginBottom':100},),

        
    #Second graph:
    ### Line chart
    ### Drop down box for country and indicator
 
    html.Div([
        
        html.H2(children = 'Development of indicators over time'), #Title for graph 2
 
        #Create dropdown for country / region
        html.Div([
            html.Label('Select region'),            
            dcc.Dropdown(
                id='country',
                options=[{'label': i, 'value': i} for i in countries],
                multi=True,
                value=[]
            ),
        ],
        style={'width': '48%', 'marginTop': 0, 'display': 'inline-block'}),           
        
        #Create dropdown for y-axis (indicator)
        html.Div([
            html.Label('Select y-axis indicator'), 
            dcc.Dropdown(
                id='yaxis-column2',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            ),
        ],style={'width': '48%', 'marginTop': 0, 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-year-graphic'), #Unique name for graph 2

])

# Callback to link first graph's click data to country dropdown
@app.callback(dash.dependencies.Output('country', 'value'),
            [dash.dependencies.Input('indicator-graphic', 'clickData')])

def update_graph(clickData):
    selected_values.append(clickData['points'][0]['customdata'])
    return selected_values

#Callback for first graph
@app.callback( 
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('xaxis-type', 'value'),
     dash.dependencies.Input('yaxis-type', 'value'),
     dash.dependencies.Input('year--slider', 'value')])

def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    
    #Filter data according to year
    dff = df[df['TIME'] == year_value]
    dff = dff[dff['UNIT']=='Chain linked volumes, index 2010=100'] 
    
    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == xaxis_column_name][dff["GEO_Category"]==i]['Value'],
            y=dff[dff['NA_ITEM'] == yaxis_column_name][dff["GEO_Category"]==i]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_column_name][dff["GEO_Category"]==i]['GEO'],
            mode='markers',
            customdata=dff[dff['NA_ITEM'] == yaxis_column_name][dff["GEO_Category"]==i]['GEO'],
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ) for i in df.GEO_Category.unique()
        ],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 100, 'b': 50, 't': 20, 'r': 100},
            hovermode='closest',
            showlegend=True,
            legend={"orientation":"h", "y":100,"yanchor":"top"}            
        )
    }
 
#Callback for second graph
####It is important that variable names do not overlap with callback 1
@app.callback( 
    dash.dependencies.Output('indicator-year-graphic', 'figure'),
    [dash.dependencies.Input('country', 'value'),
     dash.dependencies.Input('yaxis-column2', 'value')])

def update_graph(country, yaxis_column_name2):
 
    # Reset values to country selection
    global selected_values
    selected_values = country
  
    #Filter data based on chosen indicator
    dff2 = df[df['NA_ITEM'] == yaxis_column_name2]
    dff2 = dff2[dff2['UNIT']=='Chain linked volumes, index 2010=100']  
    
    # Setting up one trace for each country selected
    lines = []
    for country_element in selected_values:
        lines.append(go.Scatter(
            x=dff2[dff2["GEO"]==country_element]['TIME'],
            y=dff2[dff2["GEO"]==country_element]['Value'],
            text=dff2[dff2["GEO"]==country_element]['TIME'],
            mode='line',
            name=country_element
            ))
   
    return {
        'data': [line for line in lines],
        'layout': go.Layout(
            xaxis={
                'title': "Years",
                'type': 'linear'
            },
            yaxis={
                'title': yaxis_column_name2,
                'type': 'linear'
            },
            margin={'l': 60, 'b': 60, 't': 10, 'r': 0},
            hovermode='closest',
            showlegend = True,
            legend={"orientation":"h", "y":100, "yanchor":"top"}
        )
    }


if __name__ == '__main__':
    app.run_server()

