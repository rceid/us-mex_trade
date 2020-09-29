# This script takes the factsheet dataframe created in generate_inputs.py and extracts trade, 
# demographic, and political data from each row (i.e., US Congressional District) and inputs
# the data into trade_dash.Rmd and demog_dash.Rmd to create two factsheets for each district.


list.of.packages <- c("fontawesome", "dplyr", "stringr", "flexdashboard", "DT")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) {install.packages(new.packages)}

library(fontawesome)
library(dplyr)
library(stringr)
library(flexdashboard)
library(DT)


COUNTRY_DF <- read.csv(file = '../Data/factsheet_data.csv')
COLS <- c("Name", 'District', "Rep.and.Party",  "Mexican.American.Population", "Total.Population", "Exports.to.Mexico..2018..USD.Million.", "Total.Jobs..2018", "Namelsad")
COL_NAMES <-c("State", 'District', "Representative", "Mexican Identifying Population", "Total Population", "Exports to Mexico 2018 (USD Million)", "Total Jobs from Exports to Mexico 2018", "File Names")


clean_df <- function(df) {
  '
  Renames the columns from the dataframe
  '
  df = df[, COLS]
  #for-loop takes subset of columns and cleans their names
  for (col in colnames(df)) {
    idx <- match(col, COLS)
    names(df)[names(df) == col] <- COL_NAMES[[idx]]
  }
  return(df)
}

subset_state <- function(country_df, state) {
  '
  Creates a dataframe subset for a given US state given the dataframe containing all 50 states and Washington, D.C.
  '
  country_df$'Percent Mexican' <- round(country_df[['Mexican Identifying Population']] / country_df[['Total Population']] * 100, digits=1)
  state_df <- country_df %>% dplyr::filter(State == state)
  #code below orders districts in ascending order
  state_df$District <- factor(state_df$District, levels = str_sort(state_df$District, numeric=TRUE))
  state_df = state_df[order(state_df$District),]
  rownames(state_df) <- 1:nrow(state_df)
  int_cols <- colnames(state_df)[grepl('Population', colnames(state_df))]
  for (col in int_cols) {
    state_df[[col]] <- prettyNum(state_df[[col]],big.mark=",")
  }
  return(state_df)
}

district_info <- function(state_df, district) {
  return (state_df %>% dplyr::filter(District == district))
}


go <- function(){
  '
  In sequence, this function does the following:
  1. Loads the dataset containing all data on all states and their districts
  2. creates folders for the html files that will be knitted
  3. Iteratively subsets each state from the larger dataframe, creates a table on that state s trade and demographic information
  4. Iterates through each district contained in the state dataframe and knits a flexdashboard file for both trade and 
  demographic stats using inputs generated in the loops
  5. Saves the Files as html in their respective folders
  *This function is called in the line of code below it, allowing it to be called from the command line
  '
  df <- clean_df(COUNTRY_DF)
  states <- dplyr::distinct(df, State)
  demog_folder = '../Data/factsheets_demography'
  trade_folder = '../Data/factsheets_trade'
  if(!dir.exists(demog_folder) && !dir.exists(trade_folder) ) {
    dir.create(demog_folder)
    dir.create(trade_folder)
  }
  for (i in 1:nrow(states)) {
    state <- states[i,]
    state_df <- subset_state(df, state)
    demog_table <- state_df[, c('District', 'Representative', 'Mexican Identifying Population', 'Total Population')] 
    t_table <- state_df[, c('District', "Representative", "Exports to Mexico 2018 (USD Million)", "Total Jobs from Exports to Mexico 2018" )]
    districts <- state_df$District
    for (n in 1:length(districts)) {
      district <- toString(districts[[n]])
      out_file <-  paste(state, state_df[which(state_df$District == district),][['File Names']])
      district_stats <- district_info(state_df, district)
      rmarkdown::render('demog_dash.Rmd', output_file = paste(out_file, 'Demography'), output_dir = demog_folder, 
                        params = list(demography_table = demog_table, district_df=district_stats))
      rmarkdown::render('trade_dash.Rmd', output_file = paste(out_file, 'Trade'), output_dir = trade_folder, 
                        params = list(trade_table = t_table, district_df=district_stats))
      }
    }
  }


if (!interactive()) {
  go()
}



