import db, operator

class Recipe:
	def __init__(self, name, ingredients):
		self._name = name
		self._ingredients = []

		for (typ, amount) in ingredients:
			amount = db.convert_to_ml(amount)
			self._ingredients.append((typ, amount))

	def need_ingredients(self):
		missing_ingredients = []

		for (typ, amount) in self._ingredients:
			if not db._check_liquor_type_exists(typ):
				missing_ingredients.append((typ, amount))
				continue

			liquor_inventory = db.get_inventory_by_liquor_type(typ, amount)
			liquor_inventory.sort(key = operator.itemgetter(3))

			for (_,_,t,a) in liquor_inventory:
				if t == typ:
					# a = amount_needed - amount_in_stock
					if a <= 0:
						break

					elif a > 0:
						missing_ingredients.append((typ, a))
						break;

		return missing_ingredients
