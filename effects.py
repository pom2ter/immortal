import libtcodpy as libtcod
import time
import game
import util


# checks if there are active effects and if someone is in them
def check_active_effects():
	for y in range(game.current_map.map_height):
		for x in range(game.current_map.map_width):
			if 'duration' in game.current_map.tile[x][y]:
				if game.current_map.tile[x][y]['duration'] < game.turns:
					explored = game.current_map.tile_is_explored(x, y)
					game.current_map.set_tile_values(game.current_map.tile[x][y]['name'], x, y)
					if game.current_map.tile_is_invisible(x, y):
						game.current_map.tile[x][y].pop('invisible', None)
					if explored:
						game.current_map.tile[x][y].update({'explored': True})

	for obj in game.current_map.objects:
		if obj.name == 'player':
			if 'type' in game.current_map.tile[game.char.x][game.char.y]:
				if game.current_map.tile[game.char.x][game.char.y]['type'] == 'poison_gas':
					game.message.new('You step into poisonous gas!', game.turns)
					if 'poison' not in game.player.flags:
						dice = util.roll_dice(1, 50)
						if dice > game.player.endurance + (game.player.karma / 2):
							game.message.new('You are poisoned!', game.turns, libtcod.Color(0, 112, 0))
							game.player.flags.append('poison')
				if game.current_map.tile[game.char.x][game.char.y]['type'] == 'sleep_gas':
					if 'sleep' not in game.player.flags:
						game.message.new('You step into sleeping gas!', game.turns)
						dice = util.roll_dice(1, 50)
						if dice > game.player.wisdom + (game.player.karma / 2):
							game.message.new('You fall asleep!', game.turns, libtcod.Color(0, 143, 189))
							game.player.flags.append('sleep')

		elif obj.entity:
			if 'type' in game.current_map.tile[obj.x][obj.y]:
				if game.current_map.tile[obj.x][obj.y]['type'] == 'poison_gas':
					if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
						game.message.new(obj.entity.article.capitalize() + obj.entity.get_name() + ' step into poisonous gas!', game.turns)
					if 'poison' not in obj.entity.flags:
						dice = util.roll_dice(1, 3)
						if dice == 3:
							obj.entity.flags.append('poison')
				if game.current_map.tile[obj.x][obj.y]['type'] == 'sleep_gas':
					if 'sleep' not in obj.entity.flags:
						if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
							game.message.new(obj.entity.article.capitalize() + obj.entity.get_name() + ' step into sleeping gas!', game.turns)
						dice = util.roll_dice(1, 3)
						if dice == 3:
							if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
								game.message.new(obj.entity.article.capitalize() + obj.entity.get_name() + ' falls asleep!', game.turns)
							obj.entity.flags.append('sleep')


# fireball effect
def fireball(x, y, radius):
	path_dijk = util.set_full_explore_map(game.current_map)
	libtcod.dijkstra_compute(path_dijk, x, y)
	for step in range(0, radius + 1):
		player_fov = False
		for i in range(-radius, radius + 1):
			for j in range(-radius, radius + 1):
				if libtcod.map_is_in_fov(game.fov_map, x + i, y + j) and libtcod.dijkstra_get_distance(path_dijk, x + i, y + j) <= step and libtcod.dijkstra_get_distance(path_dijk, x + i, y + j) >= 0:
					(front, back, lerp) = util.render_tiles_animations(x + i, y + j, libtcod.Color(160, 0, 0), libtcod.Color(64, 0, 0), libtcod.Color(0, 0, 0), round(libtcod.random_get_float(game.rnd, 0, 1), 1))
					libtcod.console_put_char_ex(0, game.MAP_X + x - game.curx + i, game.MAP_Y + y - game.cury + j, '*', front, back)
					player_fov = True
		if player_fov:
			libtcod.console_flush()
			time.sleep(0.05)
			player_fov = False

	for obj in game.current_map.objects:
		if obj.name == 'player':
			if libtcod.dijkstra_get_distance(path_dijk, game.char.x, game.char.y) <= radius:
				damage = util.roll_dice(1, 10)
				game.message.new('You are hit by a fireball for ' + str(damage) + ' pts of damage!', game.turns, libtcod.Color(160, 0, 0))
				game.player.take_damage(damage, 'a fireball')
		elif obj.entity:
			if libtcod.dijkstra_get_distance(path_dijk, obj.x, obj.y) <= radius:
				damage = util.roll_dice(1, 10)
				obj.entity.take_damage(obj.x, obj.y, damage, 'a fireball')
				if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
					game.message.new(obj.entity.article.capitalize() + obj.entity.get_name() + ' is hit by a fireball for ' + str(damage) + ' pts of damage!', game.turns)
				elif not obj.entity.is_dead():
					game.message.new('You hear a scream.', game.turns)


# missile attack animation
def missile_attack(sx, sy, dx, dy):
	cx, cy = sx, sy
	if sx == dx:
		char = '|'
	if sy == dy:
		char = chr(196)
	if (sx < dx and sy > dy) or (sx > dx and sy < dy):
		char = '/'
	if (sx < dx and sy < dy) or (sx > dx and sy > dy):
		char = '\\'
	path = util.set_full_explore_map(game.current_map, False)
	libtcod.path_compute(path, sx, sy, dx, dy)
	while not libtcod.path_is_empty(path):
		cx, cy = libtcod.path_walk(path, False)
		libtcod.console_blit(game.con, 0, 0, game.MAP_WIDTH, game.MAP_HEIGHT, 0, game.MAP_X, game.MAP_Y)
		libtcod.console_put_char_ex(0, game.MAP_X + cx - game.curx, game.MAP_Y + cy - game.cury, char, libtcod.light_gray, libtcod.black)
		libtcod.console_flush()
		time.sleep(0.05)


# poison gas effect
def poison_gas(x, y, radius, duration):
	path_dijk = util.set_full_explore_map(game.current_map)
	libtcod.dijkstra_compute(path_dijk, x, y)
	for i in range(-radius, radius + 1):
		for j in range(-radius, radius + 1):
			if libtcod.dijkstra_get_distance(path_dijk, x + i, y + j) <= radius and libtcod.dijkstra_get_distance(path_dijk, x + i, y + j) >= 0:
				game.current_map.tile[x + i][y + j].update({'icon': game.current_map.tile[x + i][y + j]['icon'], 'back_light_color': libtcod.Color(0, 224, 0), 'back_dark_color': libtcod.Color(0, 112, 0), 'lerp': round(libtcod.random_get_float(game.rnd, 0, 1), 1), 'duration': game.turns + duration, 'type': 'poison_gas'})
				for obj in game.current_map.objects:
					if obj.item is None:
						if obj.x == x + i and obj.y == y + j:
							if obj.name == 'player':
								game.message.new('You are caught in a poisonous cloud!', game.turns)
								if 'poison' not in game.player.flags:
									dice = util.roll_dice(1, 50)
									if dice > game.player.endurance + (game.player.karma / 2):
										game.message.new('You are poisoned!', game.turns, libtcod.Color(0, 112, 0))
										game.player.flags.append('poison')
							else:
								if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
									game.message.new(obj.entity.article.capitalize() + obj.entity.get_name() + ' is caught in a poisonous cloud!', game.turns)
								if 'poison' not in obj.entity.flags:
									dice = util.roll_dice(1, 3)
									if dice == 3:
										obj.entity.flags.append('poison')


# sleeping gas effect
def sleeping_gas(x, y, radius, duration):
	path_dijk = util.set_full_explore_map(game.current_map)
	libtcod.dijkstra_compute(path_dijk, x, y)
	for i in range(-radius, radius + 1):
		for j in range(-radius, radius + 1):
			if libtcod.dijkstra_get_distance(path_dijk, x + i, y + j) <= radius and libtcod.dijkstra_get_distance(path_dijk, x + i, y + j) >= 0:
				game.current_map.tile[x + i][y + j].update({'icon': game.current_map.tile[x + i][y + j]['icon'], 'back_light_color': libtcod.Color(115, 220, 225), 'back_dark_color': libtcod.Color(0, 143, 189), 'lerp': round(libtcod.random_get_float(game.rnd, 0, 1), 1), 'duration': game.turns + duration, 'type': 'sleep_gas'})
				for obj in game.current_map.objects:
					if obj.item is None:
						if obj.x == x + i and obj.y == y + j:
							if obj.name == 'player':
								game.message.new('You are caught in a sleeping cloud!', game.turns)
								if 'sleep' not in game.player.flags:
									dice = util.roll_dice(1, 50)
									if dice > game.player.wisdom + (game.player.karma / 2):
										game.message.new('You fall asleep!', game.turns, libtcod.Color(0, 143, 189))
										game.player.flags.append('sleep')
							else:
								if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
									game.message.new(obj.entity.article.capitalize() + obj.entity.get_name() + ' is caught in a sleeping cloud!', game.turns)
								if 'sleep' not in obj.entity.flags:
									dice = util.roll_dice(1, 3)
									if dice == 3:
										if libtcod.map_is_in_fov(game.fov_map, obj.x, obj.y):
											game.message.new(obj.entity.article.capitalize() + obj.entity.get_name() + ' falls asleep!', game.turns)
										obj.entity.flags.append('sleep')


# victim becomes stuck
def stuck(x, y, victim='You'):
	for obj in game.current_map.objects:
		if obj.x == x and obj.y == y and not obj.item:
			if victim == 'You':
				if not 'stuck' in game.player.flags:
					game.player.flags.append('stuck')
				game.message.new('You are stuck in a bear trap!', game.turns)
				game.player.take_damage(util.roll_dice(1, 10), 'a bear trap')
			else:
				dice = util.roll_dice(1, 10)
				obj.entity.flags.append('stuck')
				obj.entity.take_damage(obj.x, obj.y, dice, 'a bear trap')
				if libtcod.map_is_in_fov(game.fov_map, x, y):
					game.message.new(victim + ' is stuck in a bear trap!', game.turns)
				elif not obj.entity.is_dead():
					game.message.new('You hear a scream.', game.turns)


# teleports to a random location on the same map
def teleportation(x, y, victim='You'):
	victims = []
	for obj in game.current_map.objects:
		if obj.x == x and obj.y == y:
			victims.append(obj)
			if (obj.entity and obj.entity.is_above_ground()) or (obj.name == 'player' and game.player.is_above_ground()):
				victims.pop()
	dx = libtcod.random_get_int(game.rnd, 0, game.current_map.map_width - 1)
	dy = libtcod.random_get_int(game.rnd, 0, game.current_map.map_height - 1)
	while game.current_map.tile_is_blocked(dx, dy):
		dx = libtcod.random_get_int(game.rnd, 0, game.current_map.map_width - 1)
		dy = libtcod.random_get_int(game.rnd, 0, game.current_map.map_height - 1)
	for i in range(len(victims)):
		victims[i].x = dx
		victims[i].y = dy
	if victim == 'You':
		game.message.new('You just got teleported to a random location!', game.turns)
	else:
		if libtcod.map_is_in_fov(game.fov_map, x, y):
			game.message.new(victim + ' just disappeared!', game.turns)
	game.fov_recompute = True
