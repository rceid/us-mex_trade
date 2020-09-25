# us-mex_trade
This repository contains code to create a dataframe containing demographic, trade, and political iformation for 436 US Congressional Districts. The data frame serves two purposes:
1) It is used by a Tableau to create the interactive map on the Mexican Embassy's website. 
2) The Scripts contained in this repository also use the data to generate factsheets for 436 congressional districts.

#### To generate the PDF factsheets, from the Script directory run the following: 
*$ sh run_scripts.sh username key* 

where _username_ and _key_ are your username and API key from pdfcrowd, the application which converts html documents to pdf. In run_scripts.sh, the following scripts are run in sequence:
  
* gen_plots.py: Creates choropleth maps for all demographic and trade statistics, specified at the top of the file, for all 436 districts, and saves the files as png image files. Also saves the dataframe containing the relevant statistics by district to the Data folder
* gen_reports.R: Retreieves the dataframe from the Datafodler and uses the information, along with the png files created in the previous python script to knit factsheets for every relevant statistic for every district, saved as html files in the Data folder.
* html_to_pdf.py: Takes all previously mentioned html files and converts them to pdfs, saving them in the Data folder. <username> and <key> are both arugments in this function described above.

All png, html, and pdf files are ignored by git and will not be pushed to the repository; they are saved locally. The shape file queried from the internet in gen_plots.py is also ignored by git, given the size of the file.
