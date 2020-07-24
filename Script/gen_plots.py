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

QUANTILE = 10

def go(command_line=True):
    '''
    Creates choropleth maps for each statistic defined above for each US state,
    as well as creating a dataframe that merges census data with export data as
    well as Congress data for 436 US Congressional Districts
    '''
    delim = select_delim(command_line)
    data_path = '..'+ delim + 'Data' + delim
    all_states(COLS, data_path, delim)
    print('All plots generated, script closing')

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
        quant = stat + ' Quantiles'
        tab_df[quant] = \
            pd.qcut(tab_df[stat], q=QUANTILE, labels=False) + 1
        plot_country(tab_df, quant, usa_maps + delim)
        path = data_path + 'Maps ' + stat
        if not os.path.exists(path):
            os.mkdir(path)
        min_max = get_min_max(tab_df, stat)
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
    if len(state_df) > 4:# and (state != 'Massachusetts' \
                              #and stat == 'Mexican-American Population'):
        state_df.plot(column=stat, linewidth=0.05#, labels=['0', '1', '2', '3','4', '5','6','7', '8', '9', '10']
                      ,edgecolor='black', cmap='Greens', legend=True,
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

def plot_country(df, stat, path):
    '''
    Plots a choropleth map of the entire country for a given metric
    '''
    assert stat in df.columns
    df = df[~df[stat].isna()]
    fig, ax = plt.subplots(1,1, figsize=(60,60))
    df = df.loc[(df['Name'] != 'Alaska') & (df['Name'] != 'Hawaii')]
    df.plot(column=stat, linewidth=0.08, edgecolor='black', \
             cmap='Greens', legend=True)#, scheme = 'quantiles')
        
    patches = legend_label(df, stat)
    pos = -.07*QUANTILE
    plt.legend(handles=patches, loc='lower right', bbox_to_anchor=(.35, pos),\
                             fontsize='x-small', title='Quantile Breakdown')

    plt.figtext(.5, .95, 'United States of America', fontsize=16, ha='center')
    plt.figtext(.5, .90, stat, fontsize=10, ha='center')
    plt.axis('off')
    file_name = 'USA_' + stat + '.png'
    plt.savefig(path + file_name)
    plt.close(fig)
    
def legend_label(df, stat):
    '''
    '''
    stat = stat.replace(' Quantiles', '')
    cmap = plt.cm.get_cmap('Greens')
    patches = []
    labels = pd.qcut(df[stat], QUANTILE, retbins=True, precision=0)[0].unique()
    labels = list(map(lambda grp: str(grp).split(', '), labels))
    labels = sorted(labels, key = lambda x: int(x[0][1:-2]))

    for q in range(QUANTILE):
        color = q/(QUANTILE-1)
        label = ', '.join(labels[q])
        label = label.replace('.0', '').replace('(', '').replace(']', '')\
            #.replace(',', ' -')
        low, up = label.split(', ')
        if low != 0:
            low = str(int(low) +1)            
        low , up = "{:,}".format(int(low)), "{:,}".format(int(up))
        label = low + ' - ' + up
        patch = mpatches.Patch(color=cmap(color), label=label)
        patches.append(patch)

    return patches

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
