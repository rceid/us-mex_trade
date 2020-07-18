# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 14:32:07 2020

@author: Ray
"""


import os
import matplotlib.pyplot as plt
import generate_inputs
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
plt.rcParams.update({'figure.max_open_warning': 0})

STATS = ["Mexican-American Population", 'Exports to Mexico, 2018 (USD Million)']

COLS = ['Name', 'Namelsad', 'geometry', 'Mexican-American Population', 
            'Latino Population', 'Total Population', 'Exports to Mexico, 2018 (USD Million)',
            'Total Jobs, 2018', 'Representative', 'Party Affiliation']

QUANTILE = 5

def go(command_line=True):
    '''
    Creates choropleth maps for each statistic defined above for each US state,
    as well as creating a dataframe that merges census data with export data as
    well as Congress data for 436 US Congressional Districts
    '''
    delim = select_delim(command_line)
    data_path = '..'+ delim + 'Data' + delim
    all_states(COLS, data_path, delim)
        

def select_delim(command_line):
    '''
    This function allows the user to define from where they are calling the
    go function.
    '''
    if command_line:
        return '/'
    else:
        return '\\' 

def all_states(cols, data_path, delim):
    '''
    iteratively creates plots for all states for all stats
    '''
    print("Initializing dataframe...")
    tab_df = generate_inputs.prepare_df(cols, data_path, delim)
    usa_maps = data_path + 'USA_maps'
    print("Dataframe loaded, now plotting maps")
    if not os.path.exists(usa_maps):
        os.mkdir(usa_maps)
    for stat in STATS:
        print("Generating maps for the following stat: {}".format(stat))
        plot_country(tab_df, stat, usa_maps + delim)
        path = data_path + 'Maps ' + stat
        if not os.path.exists(path):
            os.mkdir(path)
        min_max = get_min_max(tab_df, stat)
        tab_df[stat + ' Quantiles'] = \
            pd.qcut(tab_df[stat], q=QUANTILE, labels=False) + 1   
        for State in tab_df['Name'].unique():
            plot_state(tab_df, State, stat + ' Quantiles', path + delim, min_max)
                    
def plot_state(df, state, stat, path, min_max):
    '''
    creates a plot by state of a given statistic and saves the image into
    its respective folder
    '''
    fig, ax = plt.subplots(1,1, figsize=(15,7))
    state_df = df[df['Name'] == state]
    if len(state_df[state_df[stat].isna()]) >= 1:
        print("{} has an NA value in the '{}' column;".format(state, stat),\
              "no plot will be generated")
        return
    state_df = state_df.append(min_max)
    if len(state_df) > 3:
        state_df.plot(column=stat, linewidth=0.05, 
                      edgecolor='black', cmap='Greens', legend=True,
                      legend_kwds={'orientation': 'horizontal', 'fraction':.1,
                                   'pad':0, 'shrink':.4})
    else:
        #darker map contours for states with only one district
        state_df.plot(column=stat, linewidth=0.2,
                      edgecolor='black', cmap='Greens', legend=True, 
                      legend_kwds={'orientation': 'horizontal','fraction':.1,
                                   'pad':0,'shrink':.4})
    plt.figtext(.5, .95, state, fontsize=16, ha='center')
    plt.figtext(.5, .90, stat, fontsize=10, ha='center')
    plt.axis('off')
    file_name = state + '.png'
    plt.savefig(path + file_name)
    plt.close(fig)
    return state_df
   
def plot_country(df, stat, path):
    '''
    Plots a choropleth map of the entire country for a given metric
    '''
    assert stat in df.columns
    df = df[~df[stat].isna()]
    fig, ax = plt.subplots(1,1, figsize=(20,10))
    df = df.loc[(df['Name'] != 'Alaska') & (df['Name'] != 'Hawaii')]
    df.plot(column=stat, linewidth=0.05, edgecolor='black', \
            scheme = 'quantiles', cmap='Greens', legend=True)
        
    patches = legend_label(stat)
    plt.legend(handles=patches, loc='lower right', bbox_to_anchor=(.35,-.35),\
                             fontsize='small', title='Quantile Breakdown')

    plt.figtext(.5, .95, 'United States of America', fontsize=16, ha='center')
    plt.figtext(.5, .90, stat, fontsize=10, ha='center')
    plt.axis('off')
    file_name = 'USA_' + stat + '.png'
    plt.savefig(path + file_name)
    plt.close(fig)
    
def legend_label(stat):
    '''
    '''
    cmap = plt.cm.get_cmap('Greens')
    if 'Exports' in stat:
        patch1 = mpatches.Patch(color=cmap(0.0), label='1 - 114')
        patch2 = mpatches.Patch(color=cmap(0.25), label='115 - 247')
        patch3 = mpatches.Patch(color=cmap(0.5), label='248 - 387')
        patch4 = mpatches.Patch(color=cmap(0.75), label='388 - 691')
        patch5 = mpatches.Patch(color=cmap(1.0), label='692 - 11,176')
    else:
        patch1 = mpatches.Patch(color=cmap(0.0), label='2,645 - 11,655')
        patch2 = mpatches.Patch(color=cmap(0.25), label='11,656 - 22,192')
        patch3 = mpatches.Patch(color=cmap(0.5), label='22,193 - 49,171')
        patch4 = mpatches.Patch(color=cmap(0.75), label='49,172 - 132,773')
        patch5 = mpatches.Patch(color=cmap(1.0), label='132,774 - 607,546')

    return [patch1, patch2, patch3, patch4, patch5]

def get_min_max(df, stat):
    '''
    Gets the min and max values for the given stat for later standardization of
    the choropleth map colorbar
    '''
    mini = df[df[stat] == df[stat].min()]
    maxi = df[df[stat] == df[stat].max()]
    mini['geometry'], mini[stat + ' Quantiles'] = None, 1
    maxi['geometry'], maxi[stat + ' Quantiles'] = None, QUANTILE
    
    return mini.append(maxi)
     
                    
if __name__ == '__main__':
    go()
                
                