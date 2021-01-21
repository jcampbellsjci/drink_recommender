library(tidyverse)

cocktails_raw <- read_csv("data/cocktails_raw.csv")


#### Lowering Case ####

# Making everything lower case
cocktails_processed <- cocktails_raw %>%
  mutate_at(.vars = vars(drink, alcoholic, category,
                         glass, ingredient, measure),
            .funs = list(tolower))


#### Similar Ingredients ####

# Finding count of ingredients
ingredient_count <- cocktails_processed %>%
  group_by(ingredient) %>%
  count(sort = T)

# Going to merge sugar ingredients
sweetners <- c("sugar", "powdered sugar", "sugar syrup", "brown sugar")

cocktails_processed <- cocktails_processed %>%
  mutate(ingredient_processed = ifelse(
    ingredient %in% sweetners, "sugar / simple syrup",
    ifelse(ingredient == "maraschino cherry", "cherry",
           ifelse(ingredient %in% c("wild turkey", "jim beam"), "bourbon",
                  ifelse(ingredient == "lime" & grepl("juice", measure), "lime juice",
                         ifelse(grepl("bitters", ingredient), "bitters",
                                ifelse(ingredient == "lemon" & grepl("juice", measure), "lemon juice",
                                       ifelse(ingredient == "orange" & grepl("juice", measure), "orange juice", 
                                              ingredient))))))))

write_csv(cocktails_processed, file = "data/cocktails_processed.csv")
