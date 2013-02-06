import libtcodpy as libtcod
import copy
import game
import util
import map
import messages

RACES = ["Human", "Elf", "Dwarf", "Halfling"]
CLASSES = ["Fighter", "Rogue", "Priest", "Mage", "Explorer"]
GENDER = ["Male", "Female"]
COMBAT_SKILLS = ['Sword', 'Axe', 'Mace', 'Dagger', 'Polearm', 'Staff', 'Bow', 'Missile', 'Hands']
RACE_DESC = ["Humans are the most common race in the Realm. They are average at everything and thus don't have any racial bonuses or penalties.",
			"Elves are more dedicated to magic than combat. They have bonuses to intelligence and wisdow but penalties to strength and endurance.",
			"Dwarves are the strongest (but stupidest) people in the Realm. They are primarily used has 'tanks'. They have a bonus to strength and endurance and a penalty to everything else.",
			"Halfling are a small, friendly and clever folk, known for their thieving prowess. They have a bonus to dexterity and intelligence but a penalty to strength and wisdom."]
CLASS_DESC = ["Fighters are master of arms especially melee weapons but their magic skills are very limited. Their primary attribute is strength. This is the perfect class for dwarves. They start with moderate knowledge in all combat skills except ranged weapons.",
			"Rogues uses stealth to survive rather than weapons or magic. Their primary attribute is dexterity. This is a good class for halflings. They start with moderate knowledge in thieving skills.",
			"Priests are decent fighters that can use defensive and curative magic. Their primary attribute is wisdom. They start with some knowledge in both combat and magic skills.",
			"Mages are the opposite of fighters; great with magic, weak with weapons (except staves). Their primary attribute is intelligence. This is a good class for elves. They start with moderate knowledge in all magic skills.",
			"An explorer is basically a classless character so he doesnt have any specialties but gains more skill points per level to compensate. This 'class' is for those who likes to fine-tune their character from the very beginning."]
BASE_STATS = [[9, 9, 9, 9, 9], [12, 9, 7, 8, 11], [10, 12, 8, 9, 8], [10, 8, 9, 12, 8], [7, 9, 13, 10, 8], [9, 9, 9, 9, 9],
				[7, 9, 11, 10, 8], [10, 9, 9, 9, 10], [8, 12, 10, 10, 7], [8, 8, 11, 13, 7], [5, 9, 15, 11, 7], [7, 9, 11, 10, 8],
				[11, 7, 7, 8, 12], [14, 7, 5, 7, 14], [12, 10, 6, 8, 11], [12, 6, 7, 11, 11], [9, 7, 11, 9, 11], [11, 7, 7, 8, 12],
				[8, 10, 10, 8, 9], [11, 10, 8, 7, 11], [9, 13, 9, 8, 8], [9, 9, 10, 11, 8], [6, 10, 14, 9, 8], [8, 10, 10, 8, 9]
				]
EXPERIENCE_TABLES = [0, 100, 250, 500, 800, 1250, 1750, 2450, 3250, 4150, 5200, 6400, 7800, 9400, 11200, 13200, 16400, 18800, 21400, 24200, 27000]
FIGHTER_HP_GAIN = 10
FIGHTER_MP_GAIN = 2
ROGUE_HP_GAIN = 8
ROGUE_MP_GAIN = 4
PRIEST_HP_GAIN = 7
PRIEST_MP_GAIN = 8
MAGE_HP_GAIN = 5
MAGE_MP_GAIN = 10
EXPLORER_HP_GAIN = 6
EXPLORER_MP_GAIN = 6


class Player(object):
	def __init__(self):
		self.name = ""
		self.race = RACES[0]
		self.gender = GENDER[0]
		self.profession = CLASSES[0]
		self.strength = 9
		self.dexterity = 9
		self.intelligence = 9
		self.wisdom = 9
		self.endurance = 9
		self.karma = 9
		self.icon = '@'
		self.icon_color = libtcod.white
		self.level = 1
		self.xp = 0
		self.health = 0
		self.max_health = 0
		self.base_health = 0
		self.mana = 0
		self.max_mana = 0
		self.base_mana = 0
		self.inventory = []
		self.equipment = []
		self.turns = 0
		self.gold = 0
		self.mks = 0
		self.combat_skills = [Skill('Sword', 0, 0), Skill('Axe', 0, 0), Skill('Mace', 0, 0), Skill('Dagger', 0, 0), Skill('Polearm', 0, 0),
								Skill('Staff', 0, 0), Skill('Bow', 0, 0), Skill('Missile', 0, 0), Skill('Hands', 0, 0)]

	def add_turn(self):
		self.turns += 1
		game.gametime.update(5)
		game.player_move = True
		game.redraw_gui = True
		if self.turns % (50 - self.endurance) == 0:
			self.health += 1
			if self.health > self.max_health:
				self.health = self.max_health
			else:
				game.hp_anim.append([game.char, '1', libtcod.green, 0])
		self.item_expiration()
		self.item_is_active()
		game.fov_torch = any("torchlight" in x.flags and x.active for x in game.player.inventory)

	# attack an enemy
	def attack(self, target):
		if not target.entity.is_hostile():
			target.entity.becomes_hostile()
		#thac0 = 20 - (self.attack_rating() - target.entity.defense_rating)
		#dice = util.roll_dice(1, 20, 1, 0)
		attacker = util.roll_dice(1, 50, 1, 0)
		defender = util.roll_dice(1, 50, 1, 0)
		if attacker != 1 and defender != 50 and ((attacker + self.attack_rating()) >= (defender + target.entity.defense_rating) or attacker == 50 or defender == 1):
		#if dice != 1 and (dice >= thac0 or dice == 20):
			damage = 0
			for i in range(len(self.equipment)):
				if self.equipment[i].type == "weapon":
					damage = self.equipment[i].dice.roll_dice()
			if damage == 0:
				damage = util.roll_dice(1, 4, 1, 0)
			target.entity.take_damage(damage)
			game.hp_anim.append([target, str(-damage), libtcod.light_yellow, 0])
			game.message.new('You hit ' + target.entity.article + target.entity.name + ' for ' + str(damage) + ' pts of damage.', self.turns, libtcod.light_yellow)
			if target.entity.is_dead():
				game.message.new('The ' + target.entity.name + ' dies!', self.turns, libtcod.light_orange)
				self.gain_xp(target.entity.xp)
				self.mks += 1
				target.entity.loot(target.x, target.y)
				target.delete()
			self.combat_skills[self.find_weapon_type()].gain_xp(2)
		else:
			game.message.new('You missed the ' + target.entity.name + '.', self.turns)
			self.combat_skills[self.find_weapon_type()].gain_xp(1)
		self.add_turn()

	# calculates your attack rating
	def attack_rating(self):
		ar = self.strength
		ar += self.dexterity * 0.25
		ar += self.karma * 0.25
		ar += self.combat_skills[self.find_weapon_type()].level * 0.2
		return ar

	# calculates your defense rating
	def defense_rating(self):
		dr = self.dexterity
		dr += self.wisdom * 0.25
		dr += self.karma * 0.25
		return dr

	# drops an item
	def drop_item(self, item, qty=1):
		for i in range(qty):
			for j in xrange(len(self.inventory)):
				if self.inventory[j].name == item.name:
					pos = j
					break
			obj = map.Object(game.char.x, game.char.y, self.inventory[pos].icon, self.inventory[pos].name, self.inventory[pos].color, True, item=self.inventory[pos])
			obj.first_appearance = self.inventory[pos].turn_created
			game.current_map.objects.append(obj)
			obj.send_to_back()
			self.inventory.pop(pos)

		if qty == 1:
			game.message.new('You drop ' + obj.item.article + obj.item.name, game.player.turns, libtcod.red)
		else:
			game.message.new('You drop ' + str(qty) + ' ' + obj.item.plural, game.player.turns, libtcod.red)
		game.player.add_turn()

	# equips an item
	def equip_item(self, item):
		for i in xrange(len(self.inventory)):
			if self.inventory[i].name == item.name:
				item = i
				break

		if self.inventory[item].type == "armor":
			for flags in self.inventory[item].flags:
				if "armor_" in flags:
					flag = flags
			switch = any(flag in obj.flags for obj in self.equipment)
		elif self.inventory[item].type == "ring":
			switch = False
			if sum("armor_ring" in obj.flags for obj in self.equipment) > 1:
				switch = True
		else:
			switch = any(self.inventory[item].type in obj.type for obj in self.equipment)

		if switch:
			for obj in reversed(self.equipment):
				if self.inventory[item].type == "armor":
					if flag in obj.flags:
						self.inventory.append(obj)
						self.equipment.remove(obj)
						old = obj
				else:
					if obj.type == self.inventory[item].type:
						self.inventory.append(obj)
						self.equipment.remove(obj)
						old = obj
						if obj.type == "ring":
							break

		self.equipment.append(self.inventory[item])
		self.add_turn()
		if switch:
			game.message.new("You unequip the " + old.unidentified_name + " before equipping the " + self.inventory[item].unidentified_name, self.turns, libtcod.green)
		else:
			game.message.new("You equip the " + self.inventory[item].unidentified_name, self.turns, libtcod.green)
		self.inventory.pop(item)

	# returns the weapon type
	def find_weapon_type(self):
		weapon_type = 8
		for i in range(len(self.equipment)):
			if "weapon_sword" in self.equipment[i].flags:
				return 0
			if "weapon_axe" in self.equipment[i].flags:
				return 1
			if "weapon_mace" in self.equipment[i].flags:
				return 2
			if "weapon_dagger" in self.equipment[i].flags:
				return 3
			if "weapon_polearm" in self.equipment[i].flags:
				return 4
			if "weapon_staff" in self.equipment[i].flags:
				return 5
			if "weapon_bow" in self.equipment[i].flags:
				return 6
			if "weapon_missile" in self.equipment[i].flags:
				return 7
		return weapon_type

	# stuff to do when you gain a level
	def gain_level(self):
		self.level += 1
		if self.profession == "Fighter":
			hp_increase = libtcod.random_get_int(game.rnd, 2, FIGHTER_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, FIGHTER_MP_GAIN)
			self.stat_gain(50, 15, 5, 10, 20)
		if self.profession == "Rogue":
			hp_increase = libtcod.random_get_int(game.rnd, 2, ROGUE_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, ROGUE_MP_GAIN)
			self.stat_gain(20, 50, 10, 10, 10)
		if self.profession == "Priest":
			hp_increase = libtcod.random_get_int(game.rnd, 2, PRIEST_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, PRIEST_MP_GAIN)
			self.stat_gain(20, 10, 10, 50, 10)
		if self.profession == "Mage":
			hp_increase = libtcod.random_get_int(game.rnd, 2, MAGE_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, MAGE_MP_GAIN)
			self.stat_gain(10, 15, 50, 20, 5)
		if self.profession == "Explorer":
			hp_increase = libtcod.random_get_int(game.rnd, 2, MAGE_HP_GAIN)
			mp_increase = libtcod.random_get_int(game.rnd, 2, MAGE_MP_GAIN)
			self.stat_gain(20, 20, 20, 20, 20)
		self.base_health += hp_increase
		self.base_mana += mp_increase
		self.health += hp_increase
		self.mana += mp_increase
		self.set_max_health()
		self.set_max_mana()

	# raises your xp
	def gain_xp(self, xp):
		self.xp += xp
		if self.xp >= EXPERIENCE_TABLES[self.level]:
			self.gain_level()
			game.message.new('You are now level ' + str(self.level) + '!', self.turns, libtcod.green)

	# heals the amount of health
	def heal_health(self, hp):
		self.health += hp
		if self.health > self.max_health:
			self.health = self.max_health

	# heals the amount of mana
	def heal_mana(self, mp):
		self.mana += mp
		if self.mana > self.max_mana:
			self.mana = self.max_mana

	# calculates your health bonus
	def health_bonus(self):
		hb = self.endurance
		hb += self.karma * 0.25
		return int(hb)

	# returns true when dead
	def is_dead(self):
		if self.health < 1:
			return True
		return False

	# finds out if something in your inventory has expired
	def item_expiration(self):
		for i in range(len(self.inventory) - 1, 0, -1):
			if self.inventory[i].is_expired():
				game.message.new('An item in your inventory just rotted away.', self.turns, libtcod.red)
				self.inventory.pop(i)

	# finds out if an active item in your inventory has expired
	def item_is_active(self):
		for i in range(len(self.inventory) - 1, 0, -1):
			if self.inventory[i].is_active():
				game.message.new('An item in your inventory just rotted away.', self.turns, libtcod.red)
				self.inventory.pop(i)
		for i in range(len(self.equipment) - 1, 0, -1):
			if self.equipment[i].is_active():
				game.message.new('An item in your inventory just rotted away.', self.turns, libtcod.red)
				self.equipment.pop(i)

	# calculates your mana bonus
	def mana_bonus(self):
		mb = self.intelligence
		mb += self.wisdom * 0.75
		mb += self.karma * 0.25
		return int(mb)

	# calculates your max carrying capacity
	def max_carrying_capacity(self):
		cc = self.strength * 2.5
		cc += self.endurance * 1.25
		cc += self.karma * 0.5
		return round(cc, 2)

	# calculates your total score
	def score(self):
		score = 0
		score += (self.strength + self.dexterity + self.intelligence + self.wisdom + self.endurance + self.karma) / 5
		score += sum(c.level for c in self.combat_skills) / 20
		score += self.xp / 5
		score += (self.level - 1) * 50
		score += self.turns / 50
		score += len(game.old_maps) * 10
		score += self.mks * 10
		return score

	# set your max health
	def set_max_health(self):
		self.max_health = self.base_health + self.health_bonus()
		if self.health > self.max_health:
			self.health = self.max_health

	# set your max mana
	def set_max_mana(self):
		self.max_mana = self.base_mana + self.mana_bonus()
		if self.mana > self.max_mana:
			self.mana = self.max_mana

	# stat gain when you raise a level
	def stat_gain(self, st, dx, iq, wi, en):
		fate = libtcod.random_get_int(game.rnd, 1, 100)
		if fate <= st:
			self.strength += 1
		elif fate <= st + dx:
			self.dexterity += 1
		elif fate <= st + dx + iq:
			self.intelligence += 1
		elif fate <= st + dx + iq + wi:
			self.wisdom += 1
		elif fate <= st + dx + iq + wi + en:
			self.endurance += 1

	# reduce your health
	def take_damage(self, damage):
		self.health -= damage

	# unequip an item
	def unequip(self, item):
		self.inventory.append(self.equipment[item])
		self.add_turn()
		game.message.new("You unequip the " + self.equipment[item].unidentified_name, self.turns, libtcod.red)
		self.equipment.pop(item)

	# return carried weight
	def weight_carried(self):
		weight = sum(item.weight for item in self.inventory)
		weight += sum(item.weight for item in self.equipment)
		return round(weight, 2)


class Skill(object):
	def __init__(self, name, level, xp):
		self.name = name
		self.level = level
		self.xp = xp

	# raises your skill level
	def gain_level(self):
		if self.level < 100:
			self.level += 1
			self.xp = 0
			game.message.new('Your ' + self.name + ' skill increased to ' + str(self.level) + '!', game.player.turns, libtcod.light_green)

	# raises your skill xp
	def gain_xp(self, xp):
		if self.level < 100:
			self.xp += xp
			if self.xp >= (self.level + 1) * 5:
				self.xp = 0
				self.level += 1
				game.message.new('Your ' + self.name + ' skill increased to ' + str(self.level) + '!', game.player.turns, libtcod.light_green)


class Time(object):
	def __init__(self):
		self.day = libtcod.random_get_int(game.rnd, 1, 30)
		self.month = libtcod.random_get_int(game.rnd, 1, 12)
		self.year = libtcod.random_get_int(game.rnd, 500, 1000)
		self.hour = 12
		self.minute = 0

	# update the game time
	def update(self, min=1):
		self.minute += min
		if self.minute >= 60:
			self.minute -= 60
			self.hour += 1
		if self.hour >= 24:
			self.hour -= 24
			self.day += 1
		if self.day > 30:
			self.day -= 30
			self.month += 1
		if self.month > 12:
			self.month -= 12
			self.year += 1

	# returns a formatted string of the game time
	def time_to_text(self):
		if self.hour > 11:
			hour = self.hour - 12
			if hour == 0:
				hour = 12
			time = str(hour) + ':' + str(self.minute).rjust(2, "0") + ' pm'
		else:
			if hour == 0:
				hour = 12
			time = str(hour) + ':' + str(self.minute).rjust(2, "0") + ' am'
		if self.day == 1:
			suffix = "st"
		elif self.day == 2:
			suffix = "nd"
		elif self.day == 3:
			suffix = "rd"
		else:
			suffix = "th"
		string = "The time is " + time
		string += ", on the " + str(self.day) + suffix + " day of the month of the " + game.months[self.month - 1]
		string += ", in the year " + str(self.year)
		return string


# output races and classes description during character generation
def character_description(typ, id):
	libtcod.console_set_default_foreground(0, libtcod.white)
	libtcod.console_set_default_background(0, libtcod.black)
	libtcod.console_rect(0, 0, 10, 50, 10, True, libtcod.BKGND_SET)
	if typ == 'race':
		libtcod.console_print_rect(0, 1, 11, 45, 10, RACE_DESC[id])
	if typ == 'class':
		libtcod.console_print_rect(0, 1, 11, 45, 10, CLASS_DESC[id])


# output all options during character generation
def chargen_options(posx, posy, width, options, typ):
	choice = False
	current = 0
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	lerp = 1.0
	descending = True

	while not choice:
		if typ == 'race':
			character_description('race', current)
		if typ == 'class':
			character_description('class', current)
		ev = libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
		libtcod.console_set_default_foreground(0, libtcod.grey)
		libtcod.console_set_default_background(0, libtcod.black)

		for y in range(len(options)):
			if y == current:
				libtcod.console_set_default_foreground(0, libtcod.white)
				color, lerp, descending = util.color_lerp(lerp, descending)
				libtcod.console_set_default_background(0, color)
			else:
				libtcod.console_set_default_foreground(0, libtcod.grey)
				libtcod.console_set_default_background(0, libtcod.black)
			libtcod.console_rect(0, posx, y + posy, width, 1, True, libtcod.BKGND_SET)
			libtcod.console_print_ex(0, posx + 2, y + posy, libtcod.BKGND_SET, libtcod.LEFT, options[y])
		libtcod.console_flush()

		if key.vk == libtcod.KEY_DOWN and ev == libtcod.EVENT_KEY_PRESS:
			current = (current + 1) % len(options)
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_UP and ev == libtcod.EVENT_KEY_PRESS:
			current = (current - 1) % len(options)
			lerp = 1.0
			descending = True
		elif key.vk == libtcod.KEY_ENTER and ev == libtcod.EVENT_KEY_PRESS:
			choice = True
	return current


# main function for character generation
def create_character():
	cancel = False
	while not cancel:
		cs_width = game.SCREEN_WIDTH - 35
		cs = libtcod.console_new(cs_width, game.SCREEN_HEIGHT)
		stats = libtcod.console_new(35, game.SCREEN_HEIGHT)
		show_stats_panel(stats, "")

		libtcod.console_print(cs, 1, 1, 'CHARACTER GENERATION')
		libtcod.console_print(cs, 1, 3, 'Enter a name for your character: _' + game.player.name)
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		game.player.name = messages.input('chargen', cs, 34, 3, stats, min=3, max=17)
		show_stats_panel(stats, "")
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 1, 3, 'Select a gender:')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		game.player.gender = GENDER[chargen_options(1, 5, 10, GENDER, None)]

		show_stats_panel(stats, game.player.gender, 0)
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 1, 3, 'Select a race:')
		libtcod.console_print(cs, 16, 4, 'Modifiers')
		libtcod.console_print(cs, 16, 5, 'None')
		libtcod.console_print(cs, 16, 6, '+2 Int, +1 Wis, -2 Str, -1 End')
		libtcod.console_print(cs, 16, 7, '+2 Str, +3 End, -2 Dex, -2 Int, -1 Wis')
		libtcod.console_print(cs, 16, 8, '+1 Dex, +1 Int, -1 Str, -1 Wis')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		index = chargen_options(1, 5, 12, RACES, 'race')
		game.player.race = RACES[index]

		show_stats_panel(stats, game.player.gender + " " + game.player.race, index * 5)
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 1, 3, 'Select a class:')
		libtcod.console_print(cs, 16, 4, 'Modifiers')
		libtcod.console_print(cs, 16, 5, '+3 Str, +2 End, -2 Int, -1 Wis')
		libtcod.console_print(cs, 16, 6, '+3 Dex, +1 Str, -1 Int, -1 End')
		libtcod.console_print(cs, 16, 7, '+3 Wis, +1 Str, -1 Dex, -1 End')
		libtcod.console_print(cs, 16, 8, '+4 Int, +1 Wis, -2 Str, -1 End')
		libtcod.console_print(cs, 16, 9, 'None')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		indexr = chargen_options(1, 5, 12, CLASSES, 'class')
		game.player.profession = CLASSES[indexr]

		show_stats_panel(stats, game.player.gender + " " + game.player.race + " " + game.player.profession, (index * 5) + indexr + 1, 0)
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 1, 3, 'Options:')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		final_choice = False
		while not final_choice:
			choice = chargen_options(1, 5, 33, ['Reroll stats', 'Keep character and start game', 'Cancel and restart', 'Return to main menu'], None)
			if choice == 0:
				show_stats_panel(stats, game.player.gender + " " + game.player.race + " " + game.player.profession, (index * 5) + indexr + 1, 0)
			if choice == 1:
				final_choice = True
				return "playing"
			if choice == 2:
				game.player.name = ""
				final_choice = True
			if choice == 3:
				final_choice = True
				return "quit"


# output the stats panel
def show_stats_panel(stats, text, attr=-1, roll=-1):
	libtcod.console_set_default_foreground(stats, libtcod.light_red)
	libtcod.console_print(stats, 2, 1, game.player.name)
	libtcod.console_set_default_foreground(stats, libtcod.light_yellow)
	libtcod.console_print(stats, 2, 2, text)
	libtcod.console_set_default_foreground(stats, libtcod.white)
	libtcod.console_print(stats, 16, 4, 'Base  Bonus  Total')
	libtcod.console_print(stats, 2, 5, 'Strength:      ')
	libtcod.console_print(stats, 2, 6, 'Dexterity:     ')
	libtcod.console_print(stats, 2, 7, 'Intelligence:  ')
	libtcod.console_print(stats, 2, 8, 'Wisdom:        ')
	libtcod.console_print(stats, 2, 9, 'Endurance:     ')
	libtcod.console_print(stats, 2, 11, 'Karma:         ')

	if not attr == -1:
		for i in range(5):
			libtcod.console_print_ex(stats, 18, i + 5, libtcod.BKGND_SET, libtcod.RIGHT, str(BASE_STATS[attr][i]))

	if not roll == -1:
		stat = []
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 20))
		for i in range(5):
			libtcod.console_print(stats, 24, i + 5, str(stat[i]))
			libtcod.console_print_ex(stats, 31, i + 5, libtcod.BKGND_SET, libtcod.RIGHT, ' ' + str(BASE_STATS[attr][i] + stat[i]))
		libtcod.console_print_ex(stats, 31, 11, libtcod.BKGND_SET, libtcod.RIGHT, ' ' + str(stat[5]))
		game.player.strength = BASE_STATS[attr][0] + stat[0]
		game.player.dexterity = BASE_STATS[attr][1] + stat[1]
		game.player.intelligence = BASE_STATS[attr][2] + stat[2]
		game.player.wisdom = BASE_STATS[attr][3] + stat[3]
		game.player.endurance = BASE_STATS[attr][4] + stat[4]
		game.player.karma = stat[5]
		starting_stats()

	for i in range(game.SCREEN_HEIGHT):
		libtcod.console_print(stats, 0, i, chr(179))
	libtcod.console_blit(stats, 0, 0, 35, game.SCREEN_HEIGHT, 0, game.SCREEN_WIDTH - 35, 0)
	libtcod.console_flush()


# starting stats and equipment after character generation
def starting_stats():
	game.player.inventory = []
	game.player.gold = libtcod.random_get_int(game.rnd, 1, 50)
	if game.player.profession == "Fighter":
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, FIGHTER_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, FIGHTER_MP_GAIN)
		game.player.inventory.append(copy.deepcopy(game.items.get_item("short sword")))
		game.player.inventory.append(copy.deepcopy(game.items.get_item("leather armor")))
		game.player.combat_skills[0].level = 20
		game.player.combat_skills[1].level = 20
		game.player.combat_skills[2].level = 10
		game.player.combat_skills[3].level = 15
		game.player.combat_skills[4].level = 20
		game.player.combat_skills[8].level = 5

	if game.player.profession == "Rogue":
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, ROGUE_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, ROGUE_MP_GAIN)
		game.player.inventory.append(copy.deepcopy(game.items.get_item("dagger")))
		game.player.inventory.append(copy.deepcopy(game.items.get_item("leather armor")))
		game.player.combat_skills[3].level = 15
		game.player.combat_skills[6].level = 5
		game.player.combat_skills[7].level = 5
		game.player.combat_skills[8].level = 5

	if game.player.profession == "Priest":
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, PRIEST_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, PRIEST_MP_GAIN)
		game.player.inventory.append(copy.deepcopy(game.items.get_item("mace")))
		game.player.inventory.append(copy.deepcopy(game.items.get_item("leather armor")))
		game.player.combat_skills[0].level = 5
		game.player.combat_skills[2].level = 15
		game.player.combat_skills[3].level = 5
		game.player.combat_skills[5].level = 5

	if game.player.profession == "Mage":
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, MAGE_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, MAGE_MP_GAIN)
		game.player.inventory.append(copy.deepcopy(game.items.get_item("quarterstaff")))
		game.player.inventory.append(copy.deepcopy(game.items.get_item("robes")))
		game.player.combat_skills[5].level = 15

	if game.player.profession == "Explorer":
		game.player.base_health = libtcod.random_get_int(game.rnd, 2, EXPLORER_HP_GAIN)
		game.player.base_mana = libtcod.random_get_int(game.rnd, 2, EXPLORER_MP_GAIN)
		game.player.inventory.append(copy.deepcopy(game.items.get_item("dagger")))
		game.player.inventory.append(copy.deepcopy(game.items.get_item("leather armor")))

	game.player.inventory.append(copy.deepcopy(game.items.get_item("torch")))
	game.player.inventory.append(copy.deepcopy(game.items.get_item("torch")))
	game.player.inventory.append(copy.deepcopy(game.items.get_item("ration")))
	game.player.inventory.append(copy.deepcopy(game.items.get_item("torch")))
	game.player.set_max_health()
	game.player.set_max_mana()
	game.player.health = game.player.max_health
	game.player.mana = game.player.max_mana
