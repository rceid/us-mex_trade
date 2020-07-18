# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 11:48:55 2020

@author: Ray
"""
#!/usr/bin/python3

import sys
import os
import pdfcrowd
import pandas as pd
import gen_plots
'''
username = 'Mexemb'
key = '51b096adbc95e065cef128b556f16d20'
'''

def go(username, key, command_line=True):
    '''
    Establishes a connection to the pdfcrowd server and iteratively converts
    all html factsheet documents into static PDFs
    '''
    delim = gen_plots.select_delim(command_line)
    districts, pdf_folders, html_folders = create_folders_districts(delim)
    try:
        # create the API client instance
        client = pdfcrowd.HtmlToPdfClient(username, key)
        print('Username and password valid, connected to pdfcrowd client')
        for html_path, pdf_folder in zip(html_folders, pdf_folders):
            if pdf_folder[-10:] == 'Demography':
                print('Converting demographic factsheets...')
                suffix = ' Demography'
            else:
                suffix = ' Trade'
                print('Converting trade factsheets...')
            for district in districts:
                client.convertFileToFile(html_path + delim + district + '.html', \
                                         pdf_folder + delim + district + suffix + '.pdf')
    except pdfcrowd.Error as why:
        # report the error
        sys.stderr.write('Pdfcrowd Error: {}\n'.format(why))
    
        # rethrow or handle the exception
        raise
    
def create_folders_districts(delim):
    '''
    Initializes the fodlers to use and the districts to iterate through
    '''
    pdf_folders = ['.' + delim + '..'+ delim + 'Data'+ delim + 'PDFs_Demography', 
                   '.'+ delim + '..'+ delim + 'Data'+ delim + 'PDFs_Trade']
    html_folders = ['.'+ delim + '..'+ delim + 'Data'+ delim + 'factsheets_demography',
                    '.'+ delim + '..'+ delim + 'Data'+ delim + 'factsheets_trade']
    for folder in pdf_folders:
        if not os.path.exists(folder):
            os.mkdir(folder)
    
    df = pd.read_csv('.' + delim + '..' + delim + 'Data' + delim + 'factsheet_data.csv')
    districts = df['Name'] + ' ' + df['Namelsad']
    del df
    return districts, pdf_folders, html_folders


#if __name__ == '__main__':
    #_, username, key = sys.argv
    #go(username, key)