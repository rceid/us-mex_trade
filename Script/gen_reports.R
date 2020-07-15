# from command line, run:$ Rscript gen_reports.R
# 

#install.packages("dplyr")
#install.packages("stringr")
#install.packages("flexdashboard")
#install.packages("remotes")
#remotes::install_github("rstudio/fontawesome")
#install.packages("DT")
#


list.of.packages <- c("fontawesome", "dplyr", "stringr", "flexdashboard", "DT")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) {install.packages(new.packages)}

library(fontawesome)
library(dplyr)
library(stringr)
library(flexdashboard)
library(DT)


COUNTRY_DF <- read.csv(file = '../Data/factsheet_data.csv')
COLS <- c("Name", 'District', "Representative", "Party.Affiliation",  "Mexican.Population", "Total.Population", "Exports.to.Mexico..2018..USD.Million.", "Total.Jobs..2018", "Namelsad")
COL_NAMES <-c("State", 'District', "Representative", "Party Affiliation", "Mexican Population", "Total Population", "Exports to Mexico 2018 (USD Million)", "Total Jobs 2018", "File Names")


clean_df <- function(df) {
  df = df[, COLS]
  #for-loop takes subset of columns and cleans their names
  for (col in colnames(df)) {
    idx <- match(col, COLS)
    #df[[col]] <- prettyNum(df[[col]],big.mark=",")
    names(df)[names(df) == col] <- COL_NAMES[[idx]]
  }
  return(df)
}

subset_state <- function(country_df, state) {
  country_df$'Percent Mexican' <- round(country_df[['Mexican Population']] / country_df[['Total Population']] * 100, digits=1)
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
    demog_table <- state_df[, c('District', 'Representative', 'Party Affiliation', 'Mexican Population', 'Total Population')] 
    trade_table <- state_df[, c('District', "Representative", 'Party Affiliation',  "Exports to Mexico 2018 (USD Million)", "Total Jobs 2018" )]
    districts <- state_df$District
    for (n in 1:length(districts)) {
      district <- toString(districts[[n]])
      out_file <-  paste(state, state_df[which(state_df$District == district),][['File Names']], "Demography")
      district_stats <- district_info(state_df, district)
      rmarkdown::render('demog_dash.Rmd', output_file = out_file, output_dir = demog_folder, 
                        params = list(demography_table = demog_table, district_df=district_stats))
        #rmarkdown::render('trade')
      }
    }
  }


if (!interactive()) {
  go()
}



