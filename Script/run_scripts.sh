#!/bin/sh

Username=$1
Key=$2

echo Arguments accepted, beginning plot generation, gen_plots.py...
#python3 gen_plots.py

echo Plots generated, now generating factsheets, gen_reports.R...
#Rscript gen_reports.R

echo All factsheets generated, now converring to pdf, html_to_pdf.py...
python3 html_to_pdf.py $Username $Key

echo Script has successfully run, closing.
