# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 10:27:46 2020

@author: Ray
"""
import dash

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import geopandas as gpd
from dash.dependencies import Input, Output
import plotly.express as px
import matplotlib.pyplot as plt
import base64

df = gpd.read_file('./../Data/viz_data.geojson')\

state_df = df[df['Name'] == "Ohio"]
cols = state_df.columns[:-1]
ax = state_df.plot(column='Mexican Pop', linewidth=0.1, edgecolor='black', 
                   cmap='YlGn', 
                  legend=True, legend_kwds={'orientation': 'vertical'})
plt.axis('off')
plt.title('Mexican Population by District')
fig = ax.get_figure()
filename = 'plot.png'
fig.savefig(filename)

app = dash.Dash()
encoded_image = base64.b64encode(open(filename, 'rb').read())


app.layout = html.Div([
    html.Img(src=app.get_asset_url(filename))
    #src='data:image/png;base64,{}'.format(encoded_image))
])

if __name__ == '__main__':
    app.run_server(debug=True)