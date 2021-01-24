import pandas as pd
import numpy as np
from df2gspread import df2gspread as d2g
from df2gspread import gspread2df as g2d

import gspread
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials

# Configure the connection 
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# Give the path to the Service Account Credential json file 
creds = ServiceAccountCredentials.from_json_keyfile_name('cocktail-service-302300-693fd125ddfa.json',
															   scope)
client = gspread.authorize(creds)

# The sprad sheet ID, which can be taken from the link to the sheet
spreadsheet_key = '1V1S3jNznYBq_v2PS3qBTcMgbG5w0pmXmyL42NqDKl84'

def get_cocktail_ingredients(wks_name='cocktails_processed'):
	cocktail_ingredients = g2d.download(spreadsheet_key, wks_name, 
								 credentials=creds,
	col_names = True, row_names = True)
	cocktail_ingredients = cocktail_ingredients.reset_index()
	cocktail_ingredients = cocktail_ingredients.rename(columns={'index':'drink'})
	return cocktail_ingredients

def get_our_bar(wks_name = 'our_bar'):
	our_bar = g2d.download(spreadsheet_key, wks_name, 
								 credentials=creds,
	col_names = True, row_names = True)
	our_bar = our_bar.loc[our_bar.in_bar == '1']
	our_bar_list = our_bar.index.tolist()
	return our_bar, our_bar_list

def get_recommendations(our_bar, our_bar_list, cocktail_ingredients):

	recommendations = list()
	cocktail_ingredients.index.name = 'drink'
	for cocktail in cocktail_ingredients.drink.unique().tolist():
		cocktail_df = cocktail_ingredients.loc[cocktail_ingredients.drink == cocktail]
		ingredients = cocktail_df.ingredient_processed.unique().tolist()
		if all(elem in our_bar_list for elem in ingredients):
			recommendations.append(cocktail)

	recommendations = cocktail_ingredients.loc[cocktail_ingredients.drink.isin(recommendations)]
	recommendations = recommendations.fillna('')
	recommendations = recommendations[['drink','ingredient','ingredient_processed','measure']]


	return recommendations

def write_recommendations_to_sheet(cocktail_ingredients, recommendations, worksheet = 'recommendations'):
	 # upload the dataframe of the clients we want to delete
	d2g.upload(recommendations,
			   spreadsheet_key,
			   worksheet,
			   credentials=creds,
			   col_names=True,
			   row_names=False,
			   start_cell = 'A1',
			   clean=False)

def calculate_ingredients_needed(cocktail_ingredients, our_bar_list):
	cocktail_ingredients['ingredients_needed'] = ''

	for cocktail in cocktail_ingredients.drink.unique().tolist():
		cocktail_df = cocktail_ingredients.loc[cocktail_ingredients.drink == cocktail]
		ingredients = cocktail_df.ingredient.unique().tolist()
		ingredients_we_have = sum(el in ingredients for el in our_bar_list)
		ingredients_needed = len(ingredients) - ingredients_we_have
		cocktail_ingredients.loc[cocktail_ingredients.drink == cocktail,'ingredients_needed'] = ingredients_needed
	
	return cocktail_ingredients

def update_ingredients_needed_field(cocktail_ingredients, worksheet='cocktails_processed'):
	cell_to_start_df = 'A1'
# upload the dataframe of the clients we want to delete
	d2g.upload(cocktail_ingredients,
			   spreadsheet_key,
			   worksheet,
			   credentials=creds,
			   col_names=True,
			   row_names=False,
			   start_cell = cell_to_start_df,
			   clean=False)

def get_top_ingredients_to_buy(our_bar, cocktail_ingredients):
	# def top ingredients we should buy next based on how many cocktails we could make with just its addition
	our_bar = our_bar.reset_index()
	our_bar.columns = ['ingredient_processed','in_bar']
	cocktail_ingredients_bar = cocktail_ingredients.merge(our_bar, how = 'left', on = 'ingredient_processed').fillna(0)
	
	# get missing ingredient for 1-missing list
	missing_ingredient_per_cocktail = cocktail_ingredients_bar.loc[(cocktail_ingredients_bar.ingredients_needed == 1) 
												   & (cocktail_ingredients_bar.in_bar == 0)]
	
	top_ingredients_to_buy = missing_ingredient_per_cocktail.groupby(['ingredient_processed'])['drink'].nunique().reset_index().sort_values(by='drink',
																											  ascending=False)
	return top_ingredients_to_buy, cocktail_ingredients_bar

def get_top_ingredient_pairs_to_buy(cocktail_ingredients_bar):
	two_ingredient_needed_cocktails = cocktail_ingredients_bar.loc[(cocktail_ingredients_bar.ingredients_needed == 2) 
                                                   & (cocktail_ingredients_bar.in_bar == 0)].groupby(['drink'])['ingredient_processed'].apply(lambda x: ', '.join(x)).reset_index()

	return two_ingredient_needed_cocktails.groupby(['ingredient_processed'])['drink'].count().reset_index().sort_values(by='drink',ascending=False)

def write_top_ingredients_to_buy(top_ingredients_to_buy, worksheet = 'top_ingredients_to_buy'):
	 cell_to_start_df = 'A1'
# upload the dataframe of the clients we want to delete
	 d2g.upload(top_ingredients_to_buy,
			   spreadsheet_key,
			   worksheet,
			   credentials=creds,
			   col_names=True,
			   row_names=False,
			   start_cell = cell_to_start_df,
			   clean=False)
	

def get_cocktails_main(alcoholic=True):
	cocktail_ingredients = get_cocktail_ingredients(wks_name='cocktails_processed')
	if alcoholic:
		cocktail_ingredients = cocktail_ingredients.loc[cocktail_ingredients['alcoholic'] == 'alcoholic']
	our_bar, our_bar_list = get_our_bar(wks_name = 'our_bar')
	recommendations = get_recommendations(our_bar, our_bar_list, cocktail_ingredients)
	print('Writing {} recommendations'.format(recommendations.drink.nunique()))

	write_recommendations_to_sheet(cocktail_ingredients, recommendations, worksheet = 'recommendations')


	cocktail_ingredients = calculate_ingredients_needed(cocktail_ingredients, our_bar_list)
	update_ingredients_needed_field(cocktail_ingredients, worksheet='cocktails_processed')


	top_ingredients_to_buy, cocktail_ingredients_bar = get_top_ingredients_to_buy(our_bar, cocktail_ingredients)
	# top_ingredient_pairs_to_buy = get_top_ingredient_pairs_to_buy(cocktail_ingredients_bar)

	# top_ingredients_to_buy = top_ingredients_to_buy.append(top_ingredient_pairs_to_buy)
	top_ingredients_to_buy = top_ingredients_to_buy.reset_index().sort_values(by='drink', ascending=False) 
	write_top_ingredients_to_buy(top_ingredients_to_buy, worksheet = 'top_ingredients_to_buy')
	
get_cocktails_main(alcoholic=True)



