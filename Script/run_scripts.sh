"Username $1"
"Key $2"

python3 gen_plots.py
Rscript gen_reports.R
python3 html_to_pdf.py Username Key
