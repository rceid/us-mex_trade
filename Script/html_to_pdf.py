# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 11:48:55 2020

@author: Ray
"""
import sys
import os
import pdfcrowd
import pandas as pd

pdf_folder = './/..//Data//factsheet_pdfs'
html_path = './/..//Data//factsheets_demography'
username = 'reid7793'
key = 'dfeb31856304d11bbea4795706341d3e'

if not os.path.exists(pdf_folder):
    os.mkdir(pdf_folder)

districts = pd.read_csv('.//..//Data//factsheet_data.csv')['Namelsad']
    
def go():
    try:
        # create the API client instance
        client = pdfcrowd.HtmlToPdfClient(username, key)
        for district in districts:
            client.convertFileToFile(html_path + '\\' + district + '.html', \
                                 pdf_folder + '\\' + district + '.pdf')
    except pdfcrowd.Error as why:
        # report the error
        sys.stderr.write('Pdfcrowd Error: {}\n'.format(why))
    
        # rethrow or handle the exception
        raise
    

#if __name__ == '__main__':
    #go()