library(tidyverse)

cocktails_processed <- read_csv("data/cocktails_processed.csv")

# Finding distinct ingredients
distinct_ingredients <- cocktails_processed %>%
  distinct(ingredient) %>%
  arrange(ingredient)

# Creating a vector of ingredients we have
ingredients_we_have <- c("allspice", "angostura bitters", "bourbon",
                         "campari", "egg white", "grand marnier", "gin",
                         "green chartreuse", "kahlua", "lemon juice",
                         "lime juice", "maraschino cherry",
                         "maraschino liqueur", "orange bitters",
                         "rye whiskey", "st. germain")

# Identifying ingredients we have in bar
distinct_ingredients <- distinct_ingredients %>%
  mutate(in_bar = ifelse(ingredient %in% ingredients_we_have,
                         1, 0))

write_csv(distinct_ingredients, file = "data/our_bar.csv")
