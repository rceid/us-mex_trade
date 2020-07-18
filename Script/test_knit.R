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


#setwd(paste(getwd(), '/wsl/git/us-mex_trade',sep=''))

subset_state <- function(country_df, state) {
  #country_df$Pctmex <- round(country_df[['Mexican.Pop']] / country_df[['Total.Pop']] * 100, digits=0)
  state_df <- country_df %>% dplyr::filter(State == state)
  state_df <- country_df[country_df$]
  #code below orders districts in ascending order
  state_df$District <- factor(state_df$District, levels = str_sort(state_df$District, numeric=TRUE))
  state_df = state_df[order(state_df$District),]
  rownames(state_df) <- 1:nrow(state_df)
  
  return(state_df)
}

district_info <- function(state_df, district) {
  return (state_df %>% dplyr::filter(District == district))
}
library(dplyr)

data_folder  = '../Data/factsheets_demography'
state = 'District of Columbia'
district = 'District of Columbia Delegate District (at Large)'
state_df <- subset_state(df, state)
t_table <- state_df[, c('District', "Representative", 'Party Affiliation',  "Exports to Mexico 2018 (USD Million)", "Total Jobs 2018" )]
district_stats <- district_info(state_df, district)
rmarkdown::render('trade_dash.Rmd', output_file = district, output_dir = data_folder, 
                    params = list(trade_table = t_table, district_df=district_stats))
