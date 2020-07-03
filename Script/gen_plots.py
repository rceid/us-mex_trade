# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 14:32:07 2020

@author: Ray
"""


import os
import matplotlib.pyplot as plt
import generate_inputs
plt.rcParams.update({'figure.max_open_warning': 0})

STATS = ["Mexican Pop", "Latino Pop", "Total Pop"]
COLS = ['Name', 'Namelsad', 'geometry', 'Mexican Pop', 
            'Latino Pop', 'Total Pop', 'Exports to Mexico, 2018 (USD Million)',
            'Total Jobs, 2018', 'Representative']


def go():
    all_states()
    
def plot_state(df, state, stat, path):
    '''
    creates a plot by state of a given statistic and saves the image into
    its respective folder
    '''
    assert stat in df.columns
    
    fig, ax = plt.subplots(1,1, figsize=(15,7))
    state_df = df[df['Name'] == state]
    state_df[stat] = state_df[stat] / 1000
    state_df.plot(column=stat, linewidth=0.05, edgecolor='black', cmap='Blues', 
                  legend=True, legend_kwds={'orientation': 'horizontal',
                                            'fraction':.1, 'pad':0, 
                                            'shrink':.4})
    
    plt.title(stat + " by Congressional District", fontsize=10)
    plt.axis('off')
    file_name = state + '.png'
    plt.savefig(path + '\\' + file_name)
    plt.close(fig)
    
def all_states():
    '''
    iteratively creates plots for all states for all stats
    '''
    tab_df = generate_inputs.prepare_df(COLS)
    for stat in STATS:
        path = '.\\..\\Data\\' + stat + '_maps'
        if not os.path.exists(path):
            os.mkdir(path)
        for State in tab_df['Name'].unique():
            plot_state(tab_df, State, stat, path)