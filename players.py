import libtcodpy as libtcod
import game
import util

RACES = ["Human", "Elf", "Dwarf", "Halfling"]
CLASSES = ["Fighter", "Rogue", "Priest", "Mage"]
GENDER = ["Male", "Female"]
COMBAT_SKILLS = ['Sword', 'Axe', 'Mace', 'Dagger', 'Polearm', 'Staff', 'Bow', 'Missile', 'Hands']
BASE_STATS = [[9, 9, 9, 9, 9], [12, 9, 7, 8, 11], [10, 12, 8, 9, 8], [10, 8, 9, 12, 8], [7, 9, 13, 10, 8],
				[7, 9, 11, 10, 8], [10, 9, 9, 9, 10], [8, 12, 10, 10, 7], [8, 8, 11, 13, 7], [5, 9, 15, 11, 7],
				[11, 7, 7, 8, 12], [14, 7, 5, 7, 14], [12, 10, 6, 8, 11], [12, 6, 7, 11, 11], [9, 7, 11, 9, 11],
				[8, 10, 8, 10, 9], [11, 10, 6, 9, 11], [9, 13, 7, 10, 8], [9, 9, 8, 13, 8], [6, 10, 12, 11, 8],
				]
EXPERIENCE_TABLES = [0, 10, 250, 500, 800, 1250, 1750, 2450, 3250, 4150, 5200, 6400, 7800, 9400, 11200, 13200, 16400, 18800, 21400, 24200, 27000]
FIGHTER_HP_GAIN = 10
FIGHTER_MP_GAIN = 2
ROGUE_HP_GAIN = 8
ROGUE_MP_GAIN = 4
PRIEST_HP_GAIN = 7
PRIEST_MP_GAIN = 8
MAGE_HP_GAIN = 5
MAGE_MP_GAIN = 10


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
		self.combat_skills = [Skill('Sword', 0, 0), Skill('Axe', 0, 0), Skill('Mace', 0, 0), Skill('Dagger', 0, 0), Skill('Polearm', 0, 0),
								Skill('Staff', 0, 0), Skill('Bow', 0, 0), Skill('Missile', 0, 0), Skill('Hands', 0, 0)]

	def add_turn(self):
		self.turns += 1
		game.player_move = True
		game.redraw_gui = True
		if self.turns % (50 - self.endurance) == 0:
			self.health += 1
			if self.health > self.max_health:
				self.health = self.max_health
		self.item_degradation()

	def item_degradation(self):
		for i in range(0, len(self.inventory)):
			if self.inventory[i].type == "corpse" and (self.turns - self.inventory[i].turn_spawned > 500):
				game.message.new('An item in your inventory just rotted away.', self.turns, libtcod.red)
				self.inventory.pop(i)
				break

	def equip(self, item):
		self.equipment.append(self.inventory[item])
		self.add_turn()
		game.message.new("You equip the " + self.inventory[item].unidentified_name, self.turns, libtcod.green)
		self.inventory.pop(item)

	def unequip(self, item):
		self.inventory.append(self.equipment[item])
		self.add_turn()
		game.message.new("You unequip the " + self.equipment[item].unidentified_name, self.turns, libtcod.red)
		self.equipment.pop(item)

	def find_weapon_type(self):
		weapon_type = 8
		for i in range(0, len(self.equipment)):
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

	def attack_rating(self):
		ar = self.strength
		ar += self.dexterity * 0.25
		ar += self.karma * 0.25
		ar += self.combat_skills[self.find_weapon_type()].level * 0.2
		return ar

	def defense_rating(self):
		dr = self.dexterity
		dr += self.wisdom * 0.25
		dr += self.karma * 0.25
		return dr

	def carrying_capacity(self):
		cc = self.strength * 2.5
		cc += self.endurance * 1.25
		cc += self.karma * 0.5
		return cc

	def health_bonus(self):
		hb = self.endurance
		hb += self.karma * 0.25
		return int(hb)

	def mana_bonus(self):
		mb = self.intelligence
		mb += self.wisdom * 0.75
		mb += self.karma * 0.25
		return int(mb)

	def set_max_health(self):
		self.max_health = self.base_health + self.health_bonus()
		if self.health > self.max_health:
			self.health = self.max_health

	def set_max_mana(self):
		self.max_mana = self.base_mana + self.mana_bonus()
		if self.mana > self.max_mana:
			self.mana = self.max_mana

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
		self.carrying_capacity()

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
		self.base_health += hp_increase
		self.base_mana += mp_increase
		self.health += hp_increase
		self.mana += mp_increase
		self.set_max_health()
		self.set_max_mana()

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
			for i in range(0, len(self.equipment)):
				if self.equipment[i].type == "weapon":
					damage = self.equipment[i].dice.roll_dice()
			if damage == 0:
				damage = util.roll_dice(1, 4, 1, 0)
			game.message.new('You hit the ' + target.entity.name + ' for ' + str(damage) + ' pts of damage.', self.turns)
			target.entity.health -= damage
			if target.entity.health < 1:
				game.message.new('The ' + target.entity.name + ' dies!', self.turns, libtcod.light_orange)
				self.xp += target.entity.xp
				if self.xp >= EXPERIENCE_TABLES[self.level]:
					self.gain_level()
					game.message.new('You are now level ' + str(self.level) + '!', self.turns, libtcod.green)
				target.entity.loot(target.x, target.y)
				target.delete()
			self.combat_skills[self.find_weapon_type()].gain_xp(2)
		else:
			game.message.new('You missed the ' + target.entity.name + '.', self.turns)
			self.combat_skills[self.find_weapon_type()].gain_xp(1)
		self.add_turn()

	def score(self):
		score, skills = 0, 0
		score += (self.strength + self.dexterity + self.intelligence + self.wisdom + self.endurance + self.karma) / 5
		for i in range(0, len(self.combat_skills)):
			skills += self.combat_skills[i].level
		score += skills / 20
		score += self.xp / 5
		score += (self.level - 1) * 50
		score += self.turns / 50
		score += len(game.old_maps) * 10
		return score


class Skill(object):
	def __init__(self, name, level, xp):
		self.name = name
		self.level = level
		self.xp = xp

	def gain_xp(self, xp):
		if self.level < 100:
			self.xp += xp
			if self.xp >= (self.level + 1) * 5:
				self.xp = 0
				self.level += 1
				game.message.new('Your ' + self.name + ' skill increased to ' + str(self.level) + '!', game.player.turns, libtcod.light_green)

	def gain_level(self):
		if self.level < 100:
			self.level += 1
			self.xp = 0
			game.message.new('Your ' + self.name + ' skill increased to ' + str(self.level) + '!', game.player.turns, libtcod.light_green)


def create_character():
	cancel = False
	key = libtcod.Key()
	while not cancel:
		cs_width = game.SCREEN_WIDTH - 35
		cs = libtcod.console_new(cs_width, game.SCREEN_HEIGHT)
		stats = libtcod.console_new(35, game.SCREEN_HEIGHT)
		show_stats(stats, "")

		libtcod.console_print(cs, 0, 0, 'CHARACTER GENERATION')
		libtcod.console_print(cs, 0, 2, 'Enter a name for your character: _' + game.player.name)
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		game.player.name = game.message.input('chargen', cs, 33, 2, stats)
		show_stats(stats, "")
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 0, 2, 'Select a gender:')
		libtcod.console_print(cs, 0, 4, '1) Male')
		libtcod.console_print(cs, 0, 5, '2) Female')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		gender_choice = False
		while not gender_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			index = key.c - ord('1')
			if index >= 0 and index < len(GENDER):
				game.player.gender = GENDER[index]
				gender_choice = True

		show_stats(stats, game.player.gender, 0)
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 0, 2, 'Select a race:')
		libtcod.console_print(cs, 15, 3, 'Modifiers')
		libtcod.console_print(cs, 0, 4, '1) Human       None')
		libtcod.console_print(cs, 0, 5, '2) Elf         +2 Int, +1 Wis, -2 Str, -1 End')
		libtcod.console_print(cs, 0, 6, '3) Dwarf       +2 Str, +3 End, -2 Dex, -2 Int, -1 Wis')
		libtcod.console_print(cs, 0, 7, '4) Halfling    +1 Dex, +1 Wis, -1 Str, -1 Int')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		race_choice = False
		while not race_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			index = key.c - ord('1')
			if index >= 0 and index < len(RACES):
				game.player.race = RACES[index]
				race_choice = True

		show_stats(stats, game.player.gender + " " + game.player.race, index * 5)
		libtcod.console_rect(cs, 0, 2, cs_width, game.SCREEN_HEIGHT, True, libtcod.BKGND_SET)
		libtcod.console_print(cs, 0, 2, 'Select a class:')
		libtcod.console_print(cs, 15, 3, 'Modifiers')
		libtcod.console_print(cs, 0, 4, '1) Fighter     +3 Str, +2 End, -2 Int, -1 Wis')
		libtcod.console_print(cs, 0, 5, '2) Rogue       +3 Dex, +1 Str, -1 Int, -1 End')
		libtcod.console_print(cs, 0, 6, '3) Priest      +3 Wis, +1 Str, -1 Dex, -1 End')
		libtcod.console_print(cs, 0, 7, '4) Mage        +4 Int, +1 Wis, -2 Str, -1 End')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		class_choice = False
		while not class_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			indexr = key.c - ord('1')
			if indexr >= 0 and indexr < len(CLASSES):
				game.player.profession = CLASSES[indexr]
				class_choice = True

		show_stats(stats, game.player.gender + " " + game.player.race + " " + game.player.profession, (index * 5) + indexr + 1, 0)
		libtcod.console_print(cs, 0, 11, '(r)eroll')
		libtcod.console_print(cs, 0, 12, '(k)eep character and start game')
		libtcod.console_print(cs, 0, 13, '(c)ancel and restart')
		libtcod.console_print(cs, 0, 14, '<ESC> Return to main menu')
		libtcod.console_blit(cs, 0, 0, cs_width, game.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()

		final_choice = False
		while not final_choice:
			libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse(), True)
			if key.vk == libtcod.KEY_ESCAPE:
				final_choice = True
				return "quit"
			if chr(key.c) == 'r':
				show_stats(stats, game.player.gender + " " + game.player.race + " " + game.player.profession, (index * 5) + indexr + 1, 0)
			if chr(key.c) == 'k':
				final_choice = True
				return "playing"
			if chr(key.c) == 'c':
				game.player.name = ""
				final_choice = True


def show_stats(stats, text, attr=-1, roll=-1):
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
		for i in range(0, 5):
			libtcod.console_print_ex(stats, 18, i + 5, libtcod.BKGND_SET, libtcod.RIGHT, str(BASE_STATS[attr][i]))

	if not roll == -1:
		stat = []
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 6))
		stat.append(libtcod.random_get_int(game.rnd, 0, 19))
		for i in range(0, 5):
			libtcod.console_print(stats, 24, i + 5, str(stat[i]))
			libtcod.console_print_ex(stats, 31, i + 5, libtcod.BKGND_SET, libtcod.RIGHT, ' ' + str(BASE_STATS[attr][i] + stat[i]))
		libtcod.console_print_ex(stats, 31, 11, libtcod.BKGND_SET, libtcod.RIGHT, ' ' + str(stat[5]))
		game.player.strength = BASE_STATS[attr][0] + stat[0]
		game.player.dexterity = BASE_STATS[attr][1] + stat[1]
		game.player.intelligence = BASE_STATS[attr][2] + stat[2]
		game.player.wisdom = BASE_STATS[attr][3] + stat[3]
		game.player.endurance = BASE_STATS[attr][4] + stat[4]
		game.player.karma = stat[5]
		game.player.gold = libtcod.random_get_int(game.rnd, 1, 50)

		if game.player.profession == "Fighter":
			game.player.base_health = libtcod.random_get_int(game.rnd, 2, FIGHTER_HP_GAIN)
			game.player.base_mana = libtcod.random_get_int(game.rnd, 2, FIGHTER_MP_GAIN)
		if game.player.profession == "Rogue":
			game.player.base_health = libtcod.random_get_int(game.rnd, 2, ROGUE_HP_GAIN)
			game.player.base_mana = libtcod.random_get_int(game.rnd, 2, ROGUE_MP_GAIN)
		if game.player.profession == "Priest":
			game.player.base_health = libtcod.random_get_int(game.rnd, 2, PRIEST_HP_GAIN)
			game.player.base_mana = libtcod.random_get_int(game.rnd, 2, PRIEST_MP_GAIN)
		if game.player.profession == "Mage":
			game.player.base_health = libtcod.random_get_int(game.rnd, 2, MAGE_HP_GAIN)
			game.player.base_mana = libtcod.random_get_int(game.rnd, 2, MAGE_MP_GAIN)
		game.player.set_max_health()
		game.player.set_max_mana()
		game.player.health = game.player.max_health
		game.player.mana = game.player.max_mana

	for i in range(0, game.SCREEN_HEIGHT):
		libtcod.console_print(stats, 0, i, chr(179))
	libtcod.console_blit(stats, 0, 0, 35, game.SCREEN_HEIGHT, 0, game.SCREEN_WIDTH - 35, 0)
	libtcod.console_flush()
