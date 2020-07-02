# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 13:13:11 2020

@author: Ray
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import census_scripts


def prepare_df(cols):
    all_data = merge_clean()
    all_data = trim_alaska(all_data[cols])
    all_data.to_csv('.\\..\\Data\\factsheet_data.csv')
    return all_data

def merge_clean():
    '''
    '''
    state, shape, census, export = clean_dfs()
    main_df = merge_dfs(state, shape, census, export)
    return main_df 

def clean_dfs():
    '''
    '''
    exports = pd.read_csv(".\\..\\Data\\Mexico_exports_district.csv")
    census = census_scripts.get_census_data()
    states = pd.read_excel('.\\..\Data\\state-geocodes-v2016.xls', header=5)
    shape = gpd.read_file(".\\..\\Data\\tl_2019_us_cd116\\tl_2019_us_cd116.shp")
    shape.rename(columns={"STATEFP": 'State (FIPS)', "NAMELSAD":'Namelsad'}, 
                 inplace=True)
    shape = shape[shape['Namelsad'] != 'Congressional Districts not defined']
    shape['State (FIPS)'] = shape['State (FIPS)'].astype(int)
    exports = clean_exports(exports)
    
    return states, shape, census, exports

def clean_exports(exports_df):
    exports_df.rename(columns={
        'Exportaciones (millones de dolares)': 
            'Exports to Mexico, 2018 (USD Million)', 'Estado':"Name", 
            'Distrito':"Namelsad", 'Empleos 2018':'Total Jobs, 2018'}, 
            inplace=True)
    exports_df['Representative'] = exports_df['Nombre'] + ' ' + \
        exports_df['Apellido']
    exports_df['Representative'] = \
        np.where((exports_df['Name'] == 'North Carolina') \
                 & (exports_df['Namelsad'] == 3), 'Greg Murphy', \
                     np.where((exports_df['Name'] == 'North Carolina') \
                              & (exports_df['Namelsad'] == 9), "Dan Bishop", \
                                  exports_df['Representative']))
    exports_df['Namelsad'] = exports_df['Namelsad']\
        .apply(lambda x: str(x) if len(str(x)) > 1 else '0' + str(x))
    exports_df['Namelsad'] = exports_df['Namelsad'].apply(format_district)
    
    return exports_df

def format_district(row):
    '''
    This function formats congressional district into the format of the 
    district shape files, given the current format provided by the census 
    library
    '''
    if row == '00':
        return 'Congressional District (at Large)'
    elif row == '98':
        return 'Delegate District (at Large)'
    elif row[0] == '0':
        return 'Congressional District ' + row.replace('0', '')
    else:
        return 'Congressional District ' + row
        
def merge_dfs(state_df, shape_df, census_df, export_df):
    shape_df = pd.merge(state_df, shape_df,
        on='State (FIPS)', how='inner')
    all_data = pd.merge(shape_df, census_df, on=['Name', 'Namelsad'], how='inner')
    all_data = pd.merge(all_data, export_df, on=['Name', 'Namelsad'], how='inner')
    
    return gpd.GeoDataFrame(all_data)
    
def trim_alaska(all_data):
    '''
    removes the Aleutian Islands as it distorts Alaska state plot
    '''
        
    alaska_gdf = all_data.loc[all_data['Name'] == 'Alaska']
    alaska_mp = alaska_gdf['geometry'].values[0]
    ak_exp_gdf = gpd.GeoDataFrame(alaska_mp)
    ak_exp_gdf.columns = ['geometry']
    #Polygon covers Alaska up to 180th Meridian
    target_poly = Polygon([(-180, 50), (-180, 75), 
                           (-100, 75), (-100, 50)])
    eastern_ak = ak_exp_gdf[ak_exp_gdf.intersects(target_poly)].copy()
    eastern_ak['Name'] = 'Alaska'
    alaska_trimmed = eastern_ak.dissolve(by='Name')
    states_trimmed = all_data.copy()
    states_trimmed.loc[states_trimmed['Name'] == 'Alaska', 'geometry'] \
        = alaska_trimmed['geometry'].values
        
    return states_trimmed

        
        
        
        
        
        
        
