import drinkz.db
import drinkz.recipes
import os, errno

try:
    os.makedirs('./html')
except OSError:
    if not os.path.isdir('./html'):
        raise

drinkz.db._reset_db()
drinkz.db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
drinkz.db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

drinkz.db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
drinkz.db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')

drinkz.db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
drinkz.db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

drinkz.db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
drinkz.db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')

r1 = drinkz.recipes.Recipe('scotch on the rocks', [('blended scotch', '4 oz')])
drinkz.db.add_recipe(r1)

r2 = drinkz.recipes.Recipe('vodka martini', [('unflavored vodka', '6 oz'),
                                            ('vermouth', '1.5 oz')])
drinkz.db.add_recipe(r2)

r3 = drinkz.recipes.Recipe('vomit inducing martini', [('orange juice',
                                                      '6 oz'),
                                                     ('vermouth',
                                                      '1.5 oz')])
drinkz.db.add_recipe(r3);

r4 = drinkz.recipes.Recipe('whiskey bath', [('blended scotch', '5.5 liter')])
drinkz.db.add_recipe(r4)

### index.html
fp = open('./html/index.html', 'w');
text = 	"""<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="Content-type" content="text/html; charset=utf-8">
	<title>CSE491-Drinkz</title>
</head>
<body>
<h1>Matthew Savela's HW3 Output</h1>
<ul>
	<li><a href='recipes.html'>Recipes By Name</a></li>
	<li><a href='inventory.html'>Liquor Inventory (Amounts)</a></li>
	<li><a href='liquor_types.html'>Liquor Inventory (Types)</a></li>
</ul>
</body>
</html>
"""
fp.write(text)
fp.close()

### liquor_types.html
fp = open('./html/liquor_types.html', 'w')
text = """<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="Content-type" content="text/html; charset=utf-8">
	<title>CSE491-Drinkz: Liquor Types</title>
</head>
<body>
<h1>Matthew Savela's HW3 Output - Liquor Types</h1>
<ul>
	<li><a href='recipes.html'>Recipes By Name</a></li>
	<li><a href='inventory.html'>Liquor Inventory (Amounts)</a></li>
	<li><a href='liquor_types.html'>Liquor Inventory (Types)</a></li>
</ul>
<hr />
<ul>
"""
bottle_types = list(drinkz.db.get_bottle_types())
for (m, l, t) in bottle_types:
	text += "\t<li>" + t + "</li>\n"
text +=	"""</ul>
</body>
</html>
"""
fp.write(text)
fp.close()

### inventory.html
fp = open('./html/inventory.html', 'w')
text = """<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="Content-type" content="text/html; charset=utf-8">
	<title>CSE491-Drinkz: Liquor Inventory</title>
</head>
<body>
<h1>Matthew Savela's HW3 Output - Liquor Inventory</h1>
<ul>
	<li><a href='recipes.html'>Recipes By Name</a></li>
	<li><a href='inventory.html'>Liquor Inventory (Amounts)</a></li>
	<li><a href='liquor_types.html'>Liquor Inventory (Types)</a></li>
</ul>
<hr />
<ul>
"""
liquor_inventory = list(drinkz.db.get_liquor_inventory())
for (m,l) in liquor_inventory:
	amount = drinkz.db.get_liquor_amount(m,l)
	text += "\t<li>" + m + " - " + l + " - " + str(amount) + "ml</li>\n"
text +=	"""</ul>
</body>
</html>
"""
fp.write(text)
fp.close()

### recipes.html
fp = open('./html/recipes.html', 'w')
text = """<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="Content-type" content="text/html; charset=utf-8">
	<title>CSE491-Drinkz: Recipes</title>
</head>
<body>
<h1>Matthew Savela's HW3 Output - Recipes</h1>
<ul>
	<li><a href='recipes.html'>Recipes By Name</a></li>
	<li><a href='inventory.html'>Liquor Inventory (Amounts)</a></li>
	<li><a href='liquor_types.html'>Liquor Inventory (Types)</a></li>
</ul>
<hr />
<ul>
"""
recipes = list(drinkz.db.get_all_recipes())
for r in recipes:
	missing_ingredients = r.need_ingredients()
	if len(missing_ingredients) == 0:
		haveIngredients = "Yes"
	else:
		haveIngredients = "No"

	text += "\t<li>" + r._name + " - " + haveIngredients + "</li>\n"
text +=	"""</ul>
</body>
</html>
"""
fp.write(text)
fp.close()