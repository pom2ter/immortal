import libtcodpy as libtcod
import game


class Item(object):
	def __init__(self, typ, name, unid_name, icon, color, dark_color, weight, cost, dice, article, flags):
		self.type = typ
		self.name = name
		self.unidentified_name = unid_name
		self.icon = icon
		self.color = libtcod.Color(color[0], color[1], color[2])
		self.dark_color = libtcod.Color(dark_color[0], dark_color[1], dark_color[2])
		self.weight = weight
		self.cost = cost
		self.dice = dice
		self.article = article
		self.flags = flags

	def pick_up(self):
		if self.type == "money":
			gold = libtcod.random_get_int(0, 1, 100)
			game.message.new('You pick up ' + str(gold) + ' gold pieces', game.player.turns, libtcod.gold)
			game.player.gold += gold
		else:
			game.message.new('You pick up a ' + self.unidentified_name, game.player.turns, libtcod.green)
			game.player.inventory.append(self)
		game.player.add_turn()

	def use(self, pos):
		if "usable" in self.flags:
			if "healing" in self.flags:
				if game.player.health == game.player.max_health:
					game.message.new("You are already at max health.", game.player.turns, libtcod.white)
				else:
					heal = self.dice.roll_dice()
					game.player.health += heal
					if game.player.health > game.player.max_health:
						game.player.health = game.player.max_health
					game.player.inventory.pop(pos)
					game.message.new("You gain " + str(heal) + " hit points.", game.player.turns, libtcod.green)
					game.player.add_turn()
		else:
			game.message.new("You can't use that item.", game.player.turns, libtcod.white)

	def is_equippable(self):
		if "equippable" in self.flags:
			return True
		return False


class ItemList(object):
	def __init__(self):
		self.list = []

	# setup the items structure and run parser
	def init_parser(self):
		parser = libtcod.parser_new()
		item_type_struct = libtcod.parser_new_struct(parser, 'item_type')
		libtcod.struct_add_property(item_type_struct, 'type', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'unidentified_name', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon', libtcod.TYPE_STRING, True)
		libtcod.struct_add_property(item_type_struct, 'icon_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'dark_color', libtcod.TYPE_COLOR, True)
		libtcod.struct_add_property(item_type_struct, 'weight', libtcod.TYPE_FLOAT, False)
		libtcod.struct_add_property(item_type_struct, 'cost', libtcod.TYPE_INT, False)
		libtcod.struct_add_property(item_type_struct, 'dices', libtcod.TYPE_DICE, False)
		libtcod.struct_add_property(item_type_struct, 'article', libtcod.TYPE_STRING, True)
		libtcod.struct_add_flag(item_type_struct, 'healing')
		libtcod.struct_add_flag(item_type_struct, 'usable')
		libtcod.struct_add_flag(item_type_struct, 'equippable')
		libtcod.parser_run(parser, "data/items.txt", ItemListener())

	def add_to_list(self, item=None):
		if not item == None:
			self.list.append(item)

	def getitem(self, name):
		for item in self.list:
			if name in item.name:
				return item
		return None


class Dice(object):
	def __init__(self, dices, faces, multi, bonus):
		self.nb_dices = dices
		self.nb_faces = faces
		self.multiplier = multi
		self.bonus = bonus

	def roll_dice(self):
		return libtcod.random_get_int(0, self.nb_dices, self.nb_dices * self.nb_faces * int(self.multiplier)) + int(self.bonus)


class ItemListener(object):
	def new_struct(self, struct, name):
		self.temp_item = Item('', '', '', '', [0, 0, 0], [0, 0, 0], 0, 0, Dice(0, 0, 0, 0), '', [])
		self.temp_item.name = name
		return True

	def new_flag(self, name):
		self.temp_item.flags.append(name)
		return True

	def new_property(self, name, typ, value):
		if name == 'icon_color':
			self.temp_item.color.r = value.r
			self.temp_item.color.g = value.g
			self.temp_item.color.b = value.b
		elif name == 'dark_color':
			self.temp_item.dark_color.r = value.r
			self.temp_item.dark_color.g = value.g
			self.temp_item.dark_color.b = value.b
		elif name == 'dices':
			self.temp_item.dice.nb_dices = value.nb_dices
			self.temp_item.dice.nb_faces = value.nb_faces
			self.temp_item.dice.multiplier = value.multiplier
			self.temp_item.dice.bonus = value.addsub
		else:
			if name == "type":
				self.temp_item.type = value
			if name == "cost":
				self.temp_item.cost = value
			if name == "icon":
				self.temp_item.icon = value
			if name == "weight":
				self.temp_item.weight = value
			if name == "article":
				self.temp_item.article = value
			if name == "unidentified_name":
				self.temp_item.unidentified_name = value
		return True

	def end_struct(self, struct, name):
		game.items.add_to_list(self.temp_item)
		return True

	def error(self, msg):
		print 'error : ', msg
		return True
