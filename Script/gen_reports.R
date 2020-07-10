# from command line, run:$ Rscript gen_reports.R
# 

install.packages("dplyr")
install.packages("stringr")
library(dplyr)
library(stringr)
library(png)
library(grid)

COUNTRY_DF <- read.csv(file = '../Data/factsheet_data.csv')
COLS <- c("Name", "Namelsad", "Representative", "Party.Affiliation",  "Mexican.Pop", "Total.Pop", "Exports.to.Mexico..2018..USD.Million.", "Total.Jobs..2018")
COL_NAMES <-c("State", "District", "Representative", "Party Affiliation", "Mexican Population", "Total Population", "Exports to Mexico 2018 (USD Million)", "Total Jobs 2018")


clean_df <- function(df) {
  df = df[, COLS]
  #for-loop takes subset of columns and cleans their names
  for (col in colnames(df)) {
    idx <- match(col, COLS)
    df[[col]] <- prettyNum(df[[col]],big.mark=",")
    names(df)[names(df) == col] <- COL_NAMES[[idx]]
  }
  return(df)
}

subset_state <- function(country_df, state) {
  #country_df$Pctmex <- round(country_df[['Mexican.Pop']] / country_df[['Total.Pop']] * 100, digits=0)
  state_df <- country_df %>% dplyr::filter(State == state)
  #code below orders districts in ascending order
  state_df$District <- factor(state_df$District, levels = str_sort(state_df$District, numeric=TRUE))
  state_df = state_df[order(state_df$District),]
  rownames(state_df) <- 1:nrow(state_df)
  
  return(state_df)
}

district_info <- function(state_df, district) {
  return (state_df %>% dplyr::filter(District == district))
}


go <- function(){
  df <- clean_df(COUNTRY_DF)
  states <- dplyr::distinct(df, State)
  demog_folder = '../Data/demographic_factsheets'
  trade_folder = '../Data/demographic_factsheets'
  if(!dir.exists(data_folder)) {
    dir.create(data_folder)
  }
  for (i in 1:nrow(states)) {
    state <- states[i,]
    state_df <- subset_state(df, state)
    demog_table <- state_df[, c('District', 'Representative', 'Party Affiliation', 'Mexican Population', 'Total Population')] 
    trade_table <- state_df[, c('District', "Representative", 'Party Affiliation',  "Exports to Mexico 2018 (USD Million)", "Total Jobs 2018" )]
    districts <- state_df$District
    print(table_size)
    for (n in 1:length(districts)) {
      district <- toString(districts[[n]])
      district_stats <- district_info(state_df, district)
      if (nrow(demog_table) <= 6) {
        rmarkdown::render('demog_dash6.Rmd', output_file = district, output_dir = data_folder, 
                          params = list(demography_table = demog_table, district_df=district_stats))
        #rmarkdown::render('trade')
      }
      else {
        rmarkdown::render('demog_dash.Rmd', output_file = district, output_dir = data_folder, 
                          params = list(demography_table = demog_table, district_df=district_stats))
        #rmarkdown::render('trade')
      }
    }
  }
}


if (!interactive()) {
  go()
}



