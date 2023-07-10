from dash import Dash, html, dcc, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('combined_data.csv')

births = pd.read_csv('all_births_22nd.csv')

hist = pd.read_csv('all_pops_for_hist.csv')

with open('geo_east.json') as f:
    world = json.load(f)
    
fig = px.choropleth(df, geojson=world,
                    featureidkey='properties.sov_a3',
                    locations='Country',
                    center={"lat": 33.67, "lon": 128.09},
                    #facet_col='Country',
                    color_continuous_scale='plotly3',
                    color_continuous_midpoint=40,
                    range_color=[33,48],
                    scope='asia',
                    color='Age',
                    animation_frame='Year',
                    animation_group='Country',                   
                    ).update_layout(title='Median population age (2003-2021)')

for i, frame in enumerate(fig.frames):
    frame.layout.title = "Median age of population:<br><br>{}".format(df['combined'][i])
    fig.update_layout(title_x=0.70, title_y=0.25)
    fig.update_xaxes(mirror=True)

fig.update_geos(visible=False)

app.layout = html.Div([       
    
    html.H2('Aging Populations and Declining Births in Japan, South Korea, and Taiwan 2003 - 2021'),
    
    html.Div([
        dcc.Graph(
            id='median-age',
            figure=fig,
            hoverData={'points': [{'location': 'JPN'}]}
        )
    ], style={'width': '39%', 'display': 'inline-block', 'padding': '0 20'}),
    
    html.Div([
        dcc.Graph(id='life'),
    ], style={'display': 'inline-block', 'width': '39%'}),    
    
    html.Div([
        dcc.Graph(id='circle'),
    ], style={'display': 'inline-block', 'width': '20%'}),
    
    html.Div([
        dcc.Graph(id='pll_coord'),
    ], style={'display': 'center', 'width': '100%'}),    
])

'''
@app.callback(
    Output('hoverData', 'children'),
    Input('median-age', 'hoverData'))
def display_hover_data(hoverData):
    print(hoverData)
    return json.dumps(hoverData, indent=2)
'''
def update_graph(xaxis_column_name, yaxis_column_name, year_value):

    dff = df[df['Year'] == year_value]
    
    fig = fig
    
    fig.update_layout(height=400, width=400)

    return fig

def create_sunburst(dff, title):

    sun_fig = px.sunburst(dff, path=['Country', 'Year', 'Births'], values='Births', color='Country')
    
    sun_fig.update_layout(height=400)
    
    sun_fig.add_annotation(x=0.25, y=0.90, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)    

    return sun_fig

def create_pll_coord(dff, title, country_name):

    pll_fig = px.parallel_coordinates(dff,
                                      dimensions=['Year', 'Age', 'lx', 'qx', 'ex', 'ex_date'],
                                      color_continuous_scale=px.colors.diverging.Tealrose,
                                      color_continuous_midpoint=2,
                                      labels={'Year': 'Year', 'Age': 'Median Age n', 'lx': 'Num. Surviving at n (lx)', 'qx': 'Probability of Death Before n+1 (qx)', 'ex': 'Estimated Years Remaining (ex)', 'ex_date': 'Estimated Year of Death'})                                      
    
    pll_fig.update_layout(
    plot_bgcolor = 'white',
    paper_bgcolor = 'white')
    
    pll_fig.update_layout(height=500)

    return pll_fig   

def create_time_series(dff, title):

    fig = px.scatter(dff, x='Year', y='Births', color='Country', trendline='ols', trendline_color_override="orange", title=title)

    #fig.update_traces(mode='lines+markers')

    fig.update_xaxes(showgrid=False)
    
    fig.update_layout(height=500, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

    return fig

def create_life_hist(dff, cat_color, title):
    
    fig = px.histogram(dff, x='Age', y='Total', color='Country', animation_frame='Year', marginal='rug', hover_name='Total', color_discrete_sequence=cat_color)
    
    fig.update_xaxes(showgrid=False, mirror=True)

    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)

    fig.update_layout(height=400)
    fig.update_layout(showlegend=False)    

    return fig

@app.callback(
    Output('circle', 'figure'),
    Input('median-age', 'hoverData'),
)

def update_circle(hoverData):
    print(hoverData)
    country_name = hoverData['points'][0]['location']
    dff = births[births['Country'] == country_name]
    title = 'Births by Year'
    return create_sunburst(dff, title)

@app.callback(
    Output('pll_coord', 'figure'),
    Input('median-age', 'hoverData'),
)

def update_pll_coord(hoverData):
    print(hoverData)
    country_name = hoverData['points'][0]['location']
    dff = df[df['Country'] == country_name]
    title = '<b>{} Life tables (lx, qx, ex)'.format(country_name)    
    return create_pll_coord(dff, title, country_name)

@app.callback(
    Output('life', 'figure'),
    Input('median-age', 'hoverData'),
)
def update_life(hoverData):
    print(hoverData)
    country_name = hoverData['points'][0]['location']
    dff = hist[hist['Country'] == country_name]
    cat_color = hist.loc[hist['Country'] == country_name, 'cat_color'].values
    title = '<b>{} Population distribution'.format(country_name)    
    return create_life_hist(dff, cat_color, title)

if __name__ == '__main__':
    app.run_server(debug=True)
