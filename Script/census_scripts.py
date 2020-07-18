# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 12:48:43 2020

@author: Ray
"""

import pandas as pd
import us
import census 
from us import states 
from census import Census
import generate_inputs

#saving API key, opening session, and specifying variables
KEY = '0bde28441892c9a213ccb5782415c27f88130a35'
C = Census(KEY, year=2018)
CODES = {'B03001_004E': "Mexican-American Population", 'B03001_003E': 'Latino Population',
         'B02001_001E' : 'Total Population'}

def get_census_data():
    cong = C.acs5.state_congressional_district(list(CODES.keys()), "*", "*")
    cong = pd.DataFrame(cong)
    cong['Name'] = cong['state'].apply(lambda x: str(states.lookup(x)))
    #converting FIPS to state names
    cong['Name'] = cong['state'].apply(lambda x: str(states.lookup(x)))
    #Renaming code columns
    cong.rename(columns=CODES, inplace=True)
    #dropping obsolete congressional districts and Puerto Rico
    cong = cong[cong['congressional district'] != 'ZZ']
    cong= cong[cong['Name'] != 'Puerto Rico']
    #string cleaning with function above
    cong['Namelsad'] = \
        cong['congressional district'].apply(generate_inputs.format_district)    
    cong.sort_values(by=['Name', 'congressional district'], inplace=True)
    df = cong[['Mexican-American Population', 'Latino Population', 'Total Population',
               'Name', 'Namelsad']]
    
    return df
    




