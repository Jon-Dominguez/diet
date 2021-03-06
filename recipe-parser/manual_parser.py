import json, csv
usda = None

def load_usda():
	global usda
	with open('cleanFoodData.json') as f:
	  usda = json.load(f)

def get_usda_ingredient(id):
	global usda
	for food in usda:
		if food["id"] == int(id):
			return food
	return None
"""
recipe =
{
	title:(String),
	ingredients:
		[
			{
				id:usda_food.id,
				portion:(Integer),
				quantity:(Float),
			},
			...
		]
}
usda_food =
{
	id:(String),
	description:(String),
	nutrients:
		[
			{
				description:(String),
				value:(Float)
			},
			...
		],
	portions:
		[
			{
				grams:(Float),
				unit:(String)
			},
			...
		]
}
"""
def save_recipe(recipe):
	nutrients = []
	ids = []
	descriptions = []
	portions = []
	quantities = []
	computed_nutrients = {}
	for ingredient in recipe["ingredients"]:
		usda_ingredient = get_usda_ingredient(ingredient["id"])
		ingredient["nutrients"] = usda_ingredient["nutrients"]
		ingredient["description"] = usda_ingredient["description"]
		if int(ingredient["portion"]) == 0:
			ingredient["portion"] = {"grams":100, "unit":"100g"}
		else:
			ingredient["portion"] = usda_ingredient["portions"][int(ingredient["portion"])-1]
		for nutrient in ingredient["nutrients"]:
			if nutrient["description"] not in nutrients:
				nutrients.append(nutrient["description"])
				computed_nutrients[nutrient["description"]] = []
		ids.append(ingredient["id"])
		descriptions.append(ingredient["description"])
		portions.append(ingredient["portion"]["unit"])
		quantities.append(ingredient["quantity"])
	for i,ingredient in enumerate(recipe["ingredients"]):
		for nutrient in ingredient["nutrients"]:
			if len(computed_nutrients[nutrient["description"]]) == i:
				computed_nutrients[nutrient["description"]].append(float(nutrient["value"])*float(ingredient["quantity"])*float(ingredient["portion"]["grams"])/float(100))
			else:
				continue
		for nutrient_desc in computed_nutrients:
			if len(computed_nutrients[nutrient_desc]) == i:
				computed_nutrients[nutrient_desc].append(0)

	with open('manual/'+recipe["title"]+'.csv','wb+') as f:
	  writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
	  writer.writerow(['Ingredient ID']+ids)
	  writer.writerow(['Ingredient Description']+descriptions)
	  writer.writerow(['Portion size']+portions)
	  writer.writerow(['Quantity']+quantities)
	  for nutrient_desc, nutrient_values in computed_nutrients.iteritems():
	  	writer.writerow([nutrient_desc]+nutrient_values+[reduce(lambda x, y: x+y, nutrient_values)])

def main():
	load_usda()
	while True:
		recipe = {"title":raw_input("Please enter recipe title\n"), "ingredients":[]}
		while True:
			usda_ingredient = get_usda_ingredient(int(raw_input("Please enter ingredient ID\n")))
			if usda_ingredient == None:
				print "Ingredient not found!"
				continue
			else:
				ingredient = {"id":usda_ingredient["id"]}
				print json.dumps(usda_ingredient["portions"], sort_keys=True, indent=4, separators=(',', ': '))
				ingredient["portion"] = input("Please enter portion type (seen in 'amount' property, 0 for default 100g)\n")
				ingredient["quantity"] = input("Please enter quantity (i.e. quantity*portion_type = total grams)\n")
				recipe["ingredients"].append(ingredient)
				if raw_input("Type enter to add another ingredient or 'n' to start a new recipe\n") == "n":
					save_recipe(recipe)
					break
				else:
					continue
main()

