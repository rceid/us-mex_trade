"""
Created on Thu Jun 25 13:13:11 2020

@author: Ray
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import census_scripts
import requests
import zipfile
import io
import os 
import jellyfish
from us import states as st

pd.options.mode.chained_assignment = None

SHAPE_URL = 'https://www2.census.gov/geo/tiger/TIGER2018/CD/tl_2018_us_cd116.zip'

#cols = ['Name', 'Namelsad', 'geometry', 'Mexican Pop', 'Latino Pop', 'Total Pop', 'Exports to Mexico, 2018 (USD Million)','Total Jobs, 2018', 'Representative']

def prepare_df(cols):
    all_data = merge_clean()
    all_data = trim_alaska(all_data[cols])
    all_data.drop(['geometry'], axis=1)\
        .to_csv('../Data/factsheet_data.csv')
    return all_data

def merge_clean():
    '''
    '''
    state, shape, census, export = clean_dfs()
    main_df = merge_dfs(state, shape, census, export)
    main_df['Namelsad'] = main_df['Name'] + \
        main_df['Namelsad'].apply(lambda row: format_district(row, True))
    return main_df 

def clean_dfs():
    '''
    '''
    exports = pd.read_excel("../Data/Mexico_exports.xls")
    census = census_scripts.get_census_data()
    states = pd.read_excel('../Data/state-geocodes-v2016.xls', header=5)
    shape = get_districts()
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
    exports_df['Representative'] = np.where((exports_df['Name'] == 'North Carolina') \
                  & (exports_df['Namelsad'] == '3'), 'Greg Murphy', \
                      np.where((exports_df['Name'] == 'North Carolina') \
                              & (exports_df['Namelsad'] == '9'), "Dan Bishop", \
                                  exports_df['Representative']))
    exports_df['Namelsad'] = exports_df['Namelsad']\
        .apply(lambda x: str(x) if len(str(x)) > 1 else '0' + str(x))
    exports_df['Namelsad'] = exports_df['Namelsad'].apply(format_district)
    
    return exports_df



def format_district(row, to_state=False):
    '''
    This function formats congressional district into the format of the 
    district shape files, given the current format provided by the census 
    library
    '''
    if not to_state:
        if row == '00':
            return 'Congressional District (at Large)'
        if row == '98':
            return 'Delegate District (at Large)'
        if row[0] == '0':
            return 'Congressional District ' + row.replace('0', '')
        if row == 'Delegate District (at Large)':
            return row
        else:
            return 'Congressional District ' + row
    else:
        num = ' ' + row[-2:].strip(' ')
        if num.endswith('1') and num != ' 11':
            return num + 'st'
        if num.endswith('2') and num != ' 12':
            return num + 'nd'
        if num.endswith('3') and num != ' 13':
            return num + 'rd'
        if 'Congressional District (at Large)' in row:
            return ' ' + row
        return row if row == 'Congressional District (at Large)' else\
            num + 'th'
        
def merge_dfs(state_df, shape_df, census_df, export_df):
    shape_df = pd.merge(state_df, shape_df,
        on='State (FIPS)', how='inner')
    all_data = pd.merge(shape_df, census_df, on=['Name', 'Namelsad'], how='inner')
    all_data = pd.merge(all_data, export_df, on=['Name', 'Namelsad'], how='inner')
    
    return gpd.GeoDataFrame(all_data)
    
def get_districts():
    '''
    '''
    r = requests.get(SHAPE_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    shape_folder = '../Data/shapefile'
    if not os.path.exists(shape_folder):
        os.mkdir(shape_folder)
    z.extractall(path=shape_folder)
    [shapefile] =  [f for f in z.namelist() if f.endswith('.shp')]

    return gpd.read_file(shape_folder + '/' + shapefile)
    
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
    
##string cleaning function, partially used then went in by hand:
    
def get_party(exports_df):
    '''
    ''' 
    similarity = lambda s1, s2: jellyfish.jaro_winkler(s1, s2)
    party_df = \
        pd.read_csv\
            ("https://theunitedstates.io/congress-legislators/legislators-current.csv")
    party_df['full_name'] = \
        np.where(party_df['full_name'].isna(),\
                 party_df['ballotpedia_id'], party_df['full_name'])  
    party_df = party_df[party_df['type'] == 'rep']
    name_change = {'Brian Higgins': 'Chris Jacobs', }
    for prev, current in name_change.items():
        party_df.loc[party_df.first_name == prev, \
                 ['full_name', 'last_name']] = current[0], current[1]
    party_df['state'] = party_df['state'].apply(lambda row: str(st.lookup(row)))
    
    exports_df['Party Affiliation'] = 'No match'
    for _, party in party_df.iterrows():
        for _, rep in exports_df.iterrows():
            name = rep['Representative']
            if name == 'Rodney Davis' and party['full_name'] == 'Rodney Davis':
                print(similarity(party['last_name'].split()[-1], \
                          rep['Apellido'].split()[-1]) )
            if similarity(party['last_name'].split()[-1], \
                          rep['Apellido'].split()[-1]) > 0.94\
                and party['state'] == rep['Name']:

                exports_df.loc[exports_df.Representative == name, \
                               'Party Affiliation'] = party['party']
                break    
    return party_df
