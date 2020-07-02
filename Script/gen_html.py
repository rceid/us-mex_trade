# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 12:24:59 2020

@author: Ray
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import jinja2
import matplotlib.pyplot as plt


# Sample DataFrame
df = gpd.read_file('./../Data/viz_data.geojson')


state_df = df[df['Name'] == "Ohio"]
cols = state_df.columns[:-1]
styler = state_df[cols].style
# Template handling
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=''))
template = env.get_template('template.html')
my_title = 'Demographic Data for Ohio'
html = template.render(my_table=styler.render(), my_title=my_title)

# Plot

ax = state_df.plot(column='Mexican Pop', linewidth=0.1, edgecolor='black', 
                   cmap='YlGn', 
                  legend=True, legend_kwds={'orientation': 'vertical'})
plt.axis('off')
plt.title('Mexican Population by District')
fig = ax.get_figure()
fig.savefig('plot.svg')

# Write the HTML file
with open('report.html', 'w') as f:
    f.write(html)