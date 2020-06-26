# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 13:13:11 2020

@author: Ray
"""
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


map_df = pd.read_csv('.\\Data\\all_tableau_data.csv')
shape = gpd.read_file(".\\Data\\tl_2019_us_cd116\\tl_2019_us_cd116.shp")

shape.rename(columns={"STATEFP": 'State (FIPS)', "NAMELSAD":'Namelsad'}, 
             inplace=True)
shape['State (FIPS)'] = shape['State (FIPS)'].astype(int)

tab_df = gpd.GeoDataFrame(pd.merge(map_df, shape,
         on=['Namelsad', 'State (FIPS)'], how='inner'))

cols = ['Name', 'Namelsad', 'geometry', 'Mexican Pop', 
        'Latino Pop', 'Total Pop', 'Region']
tab_df = tab_df[cols]

tab_df.to_file("..\\wsl\\viz_data.geojson", driver='GeoJSON')


def plot_state(df, state, col):
    assert col in df.columns
    
    fig, ax = plt.subplots(1,1, figsize=(15,7))
    state_df = df[df['Name'] == state]


    g= state_df.plot(column=col, linewidth=0.1, edgecolor='black', cmap='YlGn', 
                  legend=True, legend_kwds={'orientation': 'vertical'})
    plt.title(col + " by Congressional District")
    plt.axis('off')

    plt.savefig(state+'.png')
    plt.show()

    
plot_state(tab_df, 'Ohio', 'Mexican Pop')
