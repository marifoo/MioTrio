import pygame 
from settings import *
from tile import *
from player import PlayerController
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer

class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()
		self.game_paused = False

		# sprite group setup
		self.visible_sprites_L0 = YSortCameraGroup() # floor
		self.visible_sprites_L1 = YSortCameraGroup() # walls
		self.visible_sprites_L2 = YSortCameraGroup() # deco
		self.visible_sprites_L3 = YSortCameraGroup() # anything else
		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		# attack sprites
		self.attackable_sprites = pygame.sprite.Group()

		# tileset sprites
		self.tileset = import_cut_graphics('../resources/tilesets/dungeontileset-extended.png')

		# sprite setup
		self.create_map()

		# user interface 
		self.ui = UI()

		# particles
		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)


	def create_map(self):
		layouts = {
			'map_Background': import_csv_layout('../resources/maps/map_Background.csv'),
			#'map_Coins': import_csv_layout('../resources/maps/map_Coins.csv'),
			'map_Floor': import_csv_layout('../resources/maps/map_Floor.csv'),
			'map_FloorTraps': import_csv_layout('../resources/maps/map_FloorTraps.csv'),
			'map_FloorDecoration': import_csv_layout('../resources/maps/map_FloorDecoration.csv'),
			'map_Interaction': import_csv_layout('../resources/maps/map_Interaction.csv'),
			'map_WallDecoration': import_csv_layout('../resources/maps/map_WallDecoration.csv'),
			'map_Walls': import_csv_layout('../resources/maps/map_Walls.csv')
		}

		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						#if style == 'map_Background':
						#	Tile((x, y), [self.visible_sprites], 'visible')

						if style == "map_Floor":
							Tile((x, y), [self.visible_sprites], 'visible', self.tileset[int(col)])
						elif style == 'map_Walls':
							Tile((x, y), [self.visible_sprites,self.obstacle_sprites], 'boundary', self.tileset[int(col)])
						elif style == 'map_WallDecoration' or style == 'map_FloorDecoration':
							Tile((x, y), [self.visible_sprites], 'visible', self.tileset[int(col)])
						elif style == "map_Interaction":
							Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'visible', self.tileset[int(col)])
						elif style == "map_FloorTraps":
							Tile((x, y), [self.visible_sprites], 'visible', self.tileset[int(col)])
						else:
							Tile((x, y), [self.visible_sprites], 'visible', self.tileset[int(col)])

		self.player_controller = PlayerController(3, 60, 60, self.visible_sprites,
												  self.obstacle_sprites,
												  self.create_attack,
												  self.destroy_attack,
												  self.create_magic)
		self.players = self.player_controller.players

	def create_attack(self, player):
		player.current_attack = Weapon(player,[self.visible_sprites,player.attack_sprites])

	def create_magic(self, player, style, strength, cost):
		if style == 'heal':
			self.magic_player.heal(player,strength,cost,[self.visible_sprites])
		if style == 'flame':
			self.magic_player.flame(player,cost,[self.visible_sprites,player.attack_sprites])

	def destroy_attack(self, player):
		if player.current_attack:
			player.current_attack.kill()
		player.current_attack = None

	def player_attack_logic(self, player):
		if player.attack_sprites:
			for attack_sprite in player.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'grass':
							pos = target_sprite.rect.center
							offset = pygame.math.Vector2(0,75)
							for leaf in range(randint(3,6)):
								self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
							target_sprite.kill()
						else:
							target_sprite.get_damage(player,attack_sprite.sprite_type)

	def damage_player(self,player,amount,attack_type):
		if player.vulnerable:
			player.health -= amount
			player.vulnerable = False
			player.hurt_time = pygame.time.get_ticks()
			self.animation_player.create_particles(attack_type,player.rect.center,[self.visible_sprites])

	def trigger_death_particles(self,pos,particle_type):
		self.animation_player.create_particles(particle_type,pos,self.visible_sprites)

	def run(self):
		# center cam and draw UI
		for player in self.players:
			if player.is_main_player:
				self.visible_sprites.custom_draw(player)
				self.ui.display(player)

		self.player_controller.update()

		# update game (based on sprite overlaps etc)
		self.visible_sprites.update()
		for player in self.players:
			self.visible_sprites.enemy_update(player)
			self.player_attack_logic(player)
		

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		# creating the floor
		self.floor_surf = pygame.image.load('../resources/maps/test_map.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self,player):

		# getting the offset 
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		# drawing the floor
		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		# for sprite in self.sprites():
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)
