import libtcodpy as libtcod
import game
import worldgen


# generate x number of worlds and output stats and averages for each terrain types
def worldgentest(nb):
	t_mountain_peak, h_mountain_peak, l_mountain_peak = 0, 0, 50000
	t_mountains, h_mountains, l_mountains = 0, 0, 50000
	t_high_hills, h_high_hills, l_high_hills = 0, 0, 50000
	t_low_hills, h_low_hills, l_low_hills = 0, 0, 50000
	t_forest, h_forest, l_forest = 0, 0, 50000
	t_plains, h_plains, l_plains = 0, 0, 50000
	t_coast, h_coast, l_coast = 0, 0, 50000
	t_shore, h_shore, l_shore = 0, 0, 50000
	t_sea, h_sea, l_sea = 0, 0, 50000
	t_ocean, h_ocean, l_ocean = 0, 0, 50000
	f = open('data/worldstats.txt', 'w')

	for i in range(nb):
		mountain_peak = 0
		mountains = 0
		high_hills = 0
		low_hills = 0
		forest = 0
		plains = 0
		coast = 0
		shore = 0
		sea = 0
		ocean = 0
		worldgen.World()

		for x in range(game.WORLDMAP_WIDTH):
			for y in range(game.WORLDMAP_HEIGHT):
				cellheight = libtcod.heightmap_get_value(game.heightmap, x, y)
				if cellheight >= game.terrain['Mountain Peak']['elevation']:
					mountain_peak += 1
				elif cellheight >= game.terrain['Mountains']['elevation']:
					mountains += 1
				elif cellheight >= game.terrain['High Hills']['elevation']:
					high_hills += 1
				elif cellheight >= game.terrain['Low Hills']['elevation']:
					low_hills += 1
				elif cellheight >= game.terrain['Forest']['elevation']:
					forest += 1
				elif cellheight >= game.terrain['Plains']['elevation']:
					plains += 1
				elif cellheight >= game.terrain['Coast']['elevation']:
					coast += 1
				elif cellheight >= game.terrain['Shore']['elevation']:
					shore += 1
				elif cellheight >= game.terrain['Sea']['elevation']:
					sea += 1
				else:
					ocean += 1

		t_mountain_peak += mountain_peak
		if h_mountain_peak < mountain_peak:
			h_mountain_peak = mountain_peak
		if l_mountain_peak > mountain_peak:
			l_mountain_peak = mountain_peak

		t_mountains += mountains
		if h_mountains < mountains:
			h_mountains = mountains
		if l_mountains > mountains:
			l_mountains = mountains

		t_high_hills += high_hills
		if h_high_hills < high_hills:
			h_high_hills = high_hills
		if l_high_hills > high_hills:
			l_high_hills = high_hills

		t_low_hills += low_hills
		if h_low_hills < low_hills:
			h_low_hills = low_hills
		if l_low_hills > low_hills:
			l_low_hills = low_hills

		t_forest += forest
		if h_forest < forest:
			h_forest = forest
		if l_forest > forest:
			l_forest = forest

		t_plains += plains
		if h_plains < plains:
			h_plains = plains
		if l_plains > plains:
			l_plains = plains

		t_coast += coast
		if h_coast < coast:
			h_coast = coast
		if l_coast > coast:
			l_coast = coast

		t_shore += shore
		if h_shore < shore:
			h_shore = shore
		if l_shore > shore:
			l_shore = shore

		t_sea += sea
		if h_sea < sea:
			h_sea = sea
		if l_sea > sea:
			l_sea = sea

		t_ocean += ocean
		if h_ocean < ocean:
			h_ocean = ocean
		if l_ocean > ocean:
			l_ocean = ocean

		f.write('World #' + str(i + 1) + '\n')
		f.write('----------------------\n')
		f.write('Mountain Peak: ' + str(mountain_peak) + '\n')
		f.write('Mountains: ' + str(mountains) + '\n')
		f.write('High Hills: ' + str(high_hills) + '\n')
		f.write('Low Hills: ' + str(low_hills) + '\n')
		f.write('Forest: ' + str(forest) + '\n')
		f.write('Plains: ' + str(plains) + '\n')
		f.write('Coast: ' + str(coast) + '\n')
		f.write('Shore: ' + str(shore) + '\n')
		f.write('Sea: ' + str(sea) + '\n')
		f.write('Ocean: ' + str(ocean) + '\n')
		f.write('\n')

	f.write('Totals\n')
	f.write('----------------------\n')
	f.write('Mountain Peak: ' + str(t_mountain_peak) + ' (Avg: ' + str("{0:.2f}".format(float(t_mountain_peak) / nb)) + ', High: ' + str(h_mountain_peak) + ', Low: ' + str(l_mountain_peak) + ')' + '\n')
	f.write('Mountains: ' + str(t_mountains) + ' (Avg: ' + str("{0:.2f}".format(float(t_mountains) / nb)) + ', High: ' + str(h_mountains) + ', Low: ' + str(l_mountains) + ')' + '\n')
	f.write('High Hills: ' + str(t_high_hills) + ' (Avg: ' + str("{0:.2f}".format(float(t_high_hills) / nb)) + ', High: ' + str(h_high_hills) + ', Low: ' + str(l_high_hills) + ')' + '\n')
	f.write('Low Hills: ' + str(t_low_hills) + ' (Avg: ' + str("{0:.2f}".format(float(t_low_hills) / nb)) + ', High: ' + str(h_low_hills) + ', Low: ' + str(l_low_hills) + ')' + '\n')
	f.write('Forest: ' + str(t_forest) + ' (Avg: ' + str("{0:.2f}".format(float(t_forest) / nb)) + ', High: ' + str(h_forest) + ', Low: ' + str(l_forest) + ')' + '\n')
	f.write('Plains: ' + str(t_plains) + ' (Avg: ' + str("{0:.2f}".format(float(t_plains) / nb)) + ', High: ' + str(h_plains) + ', Low: ' + str(l_plains) + ')' + '\n')
	f.write('Coast: ' + str(t_coast) + ' (Avg: ' + str("{0:.2f}".format(float(t_coast) / nb)) + ', High: ' + str(h_coast) + ', Low: ' + str(l_coast) + ')' + '\n')
	f.write('Shore: ' + str(t_shore) + ' (Avg: ' + str("{0:.2f}".format(float(t_shore) / nb)) + ', High: ' + str(h_shore) + ', Low: ' + str(l_shore) + ')' + '\n')
	f.write('Sea: ' + str(t_sea) + ' (Avg: ' + str("{0:.2f}".format(float(t_sea) / nb)) + ', High: ' + str(h_sea) + ', Low: ' + str(l_sea) + ')' + '\n')
	f.write('Ocean: ' + str(t_ocean) + ' (Avg: ' + str("{0:.2f}".format(float(t_ocean) / nb)) + ', High: ' + str(h_ocean) + ', Low: ' + str(l_ocean) + ')' + '\n')
	f.write('\n')
	f.close()
