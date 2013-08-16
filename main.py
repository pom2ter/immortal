import libtcodpy as libtcod
import os
from game import Game


def run():
	os.putenv("SDL_VIDEO_CENTERED", "1")
	if not os.path.exists('saves'):
		os.makedirs('saves')
	if not os.path.exists('maps'):
		os.makedirs('maps')
	libtcod.sys_set_fps(400)
	Game()

if __name__ == '__main__':
	run()
