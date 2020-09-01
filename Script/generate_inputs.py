"""
Created on Thu Jun 25 13:13:11 2020

@author: Ray
"""
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
pd.options.mode.chained_assignment = None
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import census_scripts
import requests
import zipfile
import io
import us
import os
#import jellyfish


#data_path = '.\\..\\Data\\'

SHAPE_URL = 'https://www2.census.gov/geo/tiger/TIGER2018/CD/tl_2018_us_cd116.zip'

STATE_STATS = 'State_trade_politics.xlsx'
STATE_FIPS = 'state-geocodes-v2016.xls'
DISTRICT_EXPORTS = 'Mexico_exports.csv'
DISTRICT_EXPORTS_19 = 'Mexico_exports_district_2019.xlsx'
OUTPUT_DATA = 'factsheet_data.csv'
COLS_TO_KEEP = ['Name', 'Namelsad', 'AWATER',
                'Mexican-American Population', 'Total Population', 
                'State Exports to Mexico, 2019', 'State Imports from Mexico, 2019',
                'Sen1', 'Sen2', 'Exports to Mexico, 2019 (USD Million)',
                'Representative', 'Party Affiliation', 'Rep and Party', 
                'Total Jobs, 2019', 'District', 'State Jobs, 2019', 'Nombre',\
                    'Apellido']

def prepare_df(data_path, delim):
    '''
    Cleans and merges all dataframes before writing them to a csv file
    '''
    print('Fetching data...')
    all_data = merge_clean(data_path, delim)
    all_data = trim_alaska(all_data)
    data_file = all_data[COLS_TO_KEEP]
    print('Writing dataframe to file...')
    data_file.to_csv(data_path + OUTPUT_DATA, encoding='iso-8859-1')
    
    return all_data

def merge_clean(data_path, delim):
    '''
    Handles the data cleaning and merging process of imported dataframes
    '''
    state, shape, census, state_info, export = clean_dfs(data_path, delim)
    main_df = merge_dfs(state, shape, census, state_info, export)
    main_df['District'] = main_df['Name'] + \
        main_df['Namelsad'].apply(lambda row: format_district(row, True))
    #State (FIPS) column is needed for tableau merge:
    main_df['State (FIPS)'] = main_df['State (FIPS)'].astype(str)
    return main_df

def clean_dfs(data_path, delim):
    '''
    Cleans data so the different data sets can be merged
    '''
    exports = pd.read_excel(data_path + DISTRICT_EXPORTS)
    census = census_scripts.get_census_data()
    states = pd.read_excel(data_path + STATE_FIPS, header=5)
    shape = get_districts(data_path, delim)
    shape.rename(columns={"STATEFP": 'State (FIPS)', "NAMELSAD":'Namelsad'}, 
                 inplace=True)
    shape = shape[shape['Namelsad'] != 'Congressional Districts not defined']
    shape['State (FIPS)'] = shape['State (FIPS)'].astype(int)
    state_info = state_stats(data_path)
    exports = clean_exports(exports)
    exports = update_exports(exports, data_path)

    return states, shape, census, state_info, exports

def clean_exports(exports_df):
    '''
    Cleans congressional district names to the desired format and assigns 
    parties to representatives.
    '''
    exports_df.rename(columns={
        'Exportaciones (millones de dolares)': 
            'Exports to Mexico, 2018 (USD Million)', 'Estado':"Name", 
            'Distrito':"Namelsad", 'Empleos 2018':'Total Jobs, 2018'}, 
            inplace=True)
    exports_df['Representative'] = exports_df['Nombre'] + ' ' + \
        exports_df['Apellido']
    exports_df['Representative'] = np.where((exports_df['Name'] == 'North Carolina')
                  & (exports_df['Namelsad'] == '3'), 'Greg Murphy', \
                      np.where((exports_df['Name'] == 'North Carolina') \
                              & (exports_df['Namelsad'] == '9'), "Dan Bishop", \
                                  exports_df['Representative']))
    exports_df['Namelsad'] = exports_df['Namelsad']\
        .apply(lambda x: str(x) if len(str(x)) > 1 else '0' + str(x))
    exports_df['Namelsad'] = exports_df['Namelsad'].apply(format_district)
    #obtained political parties of candidates via string matching with a database online
    #function was imperfect so I added non matches by hand. Results are
    #stored directly in the Mexico_exports.csv file and were loaded directly
    #exports_df = get_party(exports_df)
    
    exports_df['Rep and Party'] = exports_df['Representative'] +\
         ' (' + exports_df['Party Affiliation'].apply(lambda P: str(P)[0]) + ')'
    
    return exports_df

def update_exports(export_df_18, data_path):
    '''
    '''
    exports_df = pd.read_excel(data_path + DISTRICT_EXPORTS_19)
    exports_df = (exports_df.groupby(['ST', 'CD'])[2018].sum() / 1000000)\
        .reset_index(name='Exports to Mexico, 2019 (USD Million)')
    jobs = pd.read_excel(data_path + DISTRICT_EXPORTS_19, sheet_name=1)
    jobs = jobs.groupby(['ST', 'CD'])['Total Jobs 2018'].sum().\
        reset_index(name='Total Jobs, 2019')
    jobs['Total Jobs, 2019'] = jobs['Total Jobs, 2019']\
        .apply(lambda job: int(round(job)))
    exports_df = pd.merge(exports_df, jobs, how='inner', on=['ST', 'CD'])
    del jobs
    exports_df.rename(columns={'ST':"Name", 'CD':"Namelsad"}, inplace=True)
    exports_df['Name'] = exports_df['Name'].replace(us.states.mapping('abbr','name'))
    #standardizing district labels to match previous export df
    exports_df.loc[exports_df['Namelsad'] == 'AL', 'Namelsad'] = '00'
    exports_df.loc[exports_df['Name'] == 'District of Columbia', 'Namelsad'] = '98'
    states = set(map(lambda state: str(state), us.states.STATES\
                     + ['District of Columbia']))
    exports_df = exports_df[exports_df['Name'].isin(states)]
    exports_df['Namelsad'] = exports_df['Namelsad'].astype(str)
    exports_df['Namelsad'] = exports_df['Namelsad'].apply(format_district)
    state_jobs = exports_df.groupby('Name')['Total Jobs, 2019'].sum().\
        reset_index(name='State Jobs, 2019')
    exports_df = pd.merge(exports_df, state_jobs, how='inner', on='Name')   
    #merge with 2018 trade info df to get desired stats
    exports_df = pd.merge(exports_df, export_df_18, how='inner', \
                          on=['Name', 'Namelsad'])
    return exports_df
    
    

def state_stats(data_path):
    '''
    Renders the senators in the correct format for later use in the interactive map
    '''
    excel_file = data_path + STATE_STATS
    
    senators = pd.read_excel(excel_file, sheet_name='Senators')
    senators['Sen and Party'] = senators['Senator Name'] + ' '\
        + senators['Senator Last Name'] + ' (' + senators['Party'] + ')'
    senators['Name'] = senators['State']    
    senators = senators[['Sen and Party', 'Name']]
    senators = senators.pivot(columns='Name', values='Sen and Party')
    senators = senators.apply(lambda x: pd.Series(x.dropna().values))\
        .transpose().reset_index()
    senators.rename(columns={0:'Sen1', 1:'Sen2'}, inplace=True)
    
    state_trade = pd.read_excel(excel_file, sheet_name='Trade', header=[0,1])
    state_trade.columns = [lvl1 + ': ' + lvl2 for lvl1, lvl2 in state_trade.columns]
    cols = state_trade.columns
    rename = {cols[1]:'Name', cols[2]:'State Exports to Mexico, 2019',\
                 cols[8]:'State Imports from Mexico, 2019', cols[23]:\
                     'State Jobs, 2017'}
    state_trade.rename(columns=rename, inplace=True)
    state_trade = state_trade[list(rename.values())]
    state_trade['Name'] = state_trade['Name'].str.strip('\xa0')
    
    return pd.merge(state_trade, senators, on='Name', how='outer')
    
    

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
        if 'Congressional District (at Large)' in row or \
            row == 'Delegate District (at Large)':
            return ' ' + row
        else:
            return num + 'th'
        
def merge_dfs(state_df, shape_df, census_df, state_info, export_df):
    '''
    Merges all dataframes, which are now clean
    '''
    shape_df = pd.merge(state_df, shape_df,
        on='State (FIPS)', how='inner')
    all_data = pd.merge(shape_df, census_df, on=['Name', 'Namelsad'], how='inner')
    all_data = pd.merge(all_data, state_info, on='Name', how='inner')
    all_data = pd.merge(all_data, export_df, on=['Name', 'Namelsad'], how='inner')

    
    return gpd.GeoDataFrame(all_data)
    
def get_districts(data_path, delim):
    '''
    Imports the shape file containing the geometry of every US congressional 
    district and creates a GeoPandas dataframe. The shape file is called from 
    ts URL and is not saved locally due to the file size
    '''
    r = requests.get(SHAPE_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    shape_folder = data_path + 'shapefile'
    if not os.path.exists(shape_folder):
        os.mkdir(shape_folder)
    z.extractall(path=shape_folder)
    [shapefile] =  [f for f in z.namelist() if f.endswith('.shp')]

    return gpd.read_file(shape_folder + delim + shapefile)
    
def trim_alaska(all_data):
    '''
    removes the Aleutian Islands as it distorts Alaska state plot.
    Code obtained from the following article:
    https://towardsdatascience.com/how-to-split-shapefiles-e8a8ac494189?gi=a2a29fdbde28
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
    

# def get_party(exports_df):
#    '''
#    string cleaning and record linkage function, partially used then went in
#    by hand and fixed unmatches
#    '''
#     similarity = lambda s1, s2: jellyfish.jaro_winkler(s1, s2)
#     party_df = \
#         pd.read_csv\
#             ("https://theunitedstates.io/congress-legislators/legislators-current.csv")
#     party_df['full_name'] = \
#         np.where(party_df['full_name'].isna(),\
#                  party_df['ballotpedia_id'], party_df['full_name'])  
#     party_df = party_df[party_df['type'] == 'rep']
#     name_change = {'Brian Higgins': 'Chris Jacobs', }
#     for prev, current in name_change.items():
#         party_df.loc[party_df.first_name == prev, \
#                  ['full_name', 'last_name']] = current[0], current[1]
#     party_df['state'] = party_df['state'].apply(lambda row: str(st.lookup(row)))
    
#     exports_df['Party Affiliation'] = 'No match'
#     for _, party in party_df.iterrows():
#         for _, rep in exports_df.iterrows():
#             name = rep['Representative']
#             if name == 'Rodney Davis' and party['full_name'] == 'Rodney Davis':
#             if similarity(party['last_name'].split()[-1], \
#                           rep['Apellido'].split()[-1]) > 0.94\
#                 and party['state'] == rep['Name']:

#                 exports_df.loc[exports_df.Representative == name, \
#                                'Party Affiliation'] = party['party']
#                 break    
#     return party_df
