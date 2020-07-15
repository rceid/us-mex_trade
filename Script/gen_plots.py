# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 14:32:07 2020

@author: Ray
"""


import os
import matplotlib.pyplot as plt
import generate_inputs
plt.rcParams.update({'figure.max_open_warning': 0})

STATS = ["Mexican Population", "Latino Population", "Total Population"]
COLS = ['Name', 'Namelsad', 'geometry', 'Mexican Population', 
            'Latino Population', 'Total Population', 'Exports to Mexico, 2018 (USD Million)',
            'Total Jobs, 2018', 'Representative', 'Party Affiliation']



def go():
    delim = select_delim(command_line=True)
    all_states(COLS, delim)
        

def select_delim(command_line=True):
    '''
    '''
    if command_line:
        return '/'
    else:
        return '\\' 

def all_states(cols, delim):
    '''
    iteratively creates plots for all states for all stats
    '''
    tab_df = generate_inputs.prepare_df(COLS, delim)
    for idx, stat in enumerate(STATS):
        path = '..'+ delim + 'Data' + delim + stat + '_maps'
        if not os.path.exists(path):
            os.mkdir(path)
        for State in tab_df['Name'].unique():
            state_df = plot_state(tab_df, State, stat, path, delim)
            # if idx == 0:
            #     for dist in state_df['District'].unique():
            #         p = '..' + delim + 'Data'+ delim + 'District_shapes'
            #         if not os.path.exists(p):
            #             os.mkdir(p)
            #         plot_district(state_df, dist, p, delim)
                    
def plot_state(df, state, stat, path, delim):
    '''
    creates a plot by state of a given statistic and saves the image into
    its respective folder
    '''
    assert stat in df.columns
    
    fig, ax = plt.subplots(1,1, figsize=(15,7))
    state_df = df[df['Name'] == state]
    state_df[stat] = state_df[stat]
    if len(state_df) > 1:
        state_df.plot(column=stat, linewidth=0.05, edgecolor='black', cmap='Greens', 
                  legend=True, legend_kwds={'orientation': 'horizontal',
                                            'fraction':.1, 'pad':0, 
                                            'shrink':.4})
    else:
        state_df.plot(column=stat, linewidth=0.2, edgecolor='black', cmap='Greens', 
                  legend=True, legend_kwds={'orientation': 'horizontal',
                                            'fraction':.1, 'pad':0, 
                                            'shrink':.4})
    
    plt.figtext(.5, .95, state, fontsize=16, ha='center')
    plt.figtext(.5, .90, stat, fontsize=10, ha='center')
    plt.axis('off')
    file_name = state + '.png'
    plt.savefig(path + delim + file_name)
    plt.close(fig)
    
    return state_df
    
def plot_district(state_df, district, path, delim):
    '''
    Creates a plot of the shape of a congressional district
    '''
    fig, ax = plt.subplots(1,1, figsize=(15,7))
    district_plot = state_df.loc[state_df["District"] == district]
    district_plot.plot(edgecolor='black', cmap='Blues_r')
    plt.axis('off')
    file_name = district_plot['District'].item()
    plt.savefig(path + delim + file_name)
    plt.close(fig)
    

                    
if __name__ == '__main__':
    go()
                
                
                
                
                
                