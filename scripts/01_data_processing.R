library(tidyverse)

cocktails_raw <- read_csv("data/cocktails_raw.csv")

# Making everything lower case
cocktails_processed <- cocktails_raw %>%
  mutate_at(.vars = vars(drink, alcoholic, category,
                         glass, ingredient, measure),
            .funs = list(tolower))

write_csv(cocktails_processed, file = "data/cocktails_processed.csv")
