import pygame
import pytmx.pytmx
from pytmx import TiledTileLayer, TiledObjectGroup

from settings import *
from pytmx.util_pygame import load_pygame
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
		#self.visible_sprites = YSortCameraGroup()
		self.visible_sprites = pygame.sprite.Group()
		self.obstacle_sprites = pygame.sprite.Group()

		# attack sprites
		self.attackable_sprites = pygame.sprite.Group()

		# sprite setup
		self.map_tmx = load_pygame('../resources/tiled_data/map.tmx')
		self.create_map()

		# user interface 
		self.ui = UI()

		# particles
		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)

	def create_map(self):
		# cycle through all layers
		print(self.map_tmx.tile_properties)
		for layer in self.map_tmx.visible_layers:
			if isinstance(layer, TiledTileLayer):
				for x,y,gid in layer:
					# for x, y, surf in layer.tiles():
					surf = self.map_tmx.get_tile_image_by_gid(gid)
					if surf:
						pos = (x * TILESIZE, y * TILESIZE)
						if layer.Obstacle:
							groups = [self.visible_sprites, self.obstacle_sprites]
						else:
							groups = self.visible_sprites
						if hasAnimation(gid, self.map_tmx):# gid in self.map_tmx.tile_properties:
							animation_frames = AnimationFrames(gid,self.map_tmx)
							AnimatedTile(pos=pos, animation_frames=animation_frames,groups=[self.visible_sprites, self.obstacle_sprites])
						else:
							StandardTile(pos=pos, surf=surf, groups=groups)
			if isinstance(layer, TiledObjectGroup):
				for obj in layer:
					pos = (obj.x,obj.y)
					if hasAnimation(obj.gid, self.map_tmx):
						animation_frames = AnimationFrames(obj.gid,self.map_tmx)
						AnimatedTile(pos=pos, animation_frames=animation_frames,groups=[self.visible_sprites, self.obstacle_sprites])
					else:
						StandardTile(pos=pos, surf=obj.image, groups=[self.visible_sprites, self.obstacle_sprites])

		# for gid, props in self.map_tmx.tile_properties.items():

		# if image == self.map_tmx.get_tile_image_by_gid(props['frames'][0].gid):
					# 	image = self.map_tmx.get_tile_image_by_gid(props['frames'][self.current_anim_index].gid)
					# 	self.surface.blit(image, (x * 16, y * 16))
					# else:
					# 	self.surface.blit(image, ((x * 16) + layer.offsetx, (y * 16) + layer.offsety))




		test= self.map_tmx.objects

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
		for player in self.players:
			if player.is_main_player:
				self.ui.display(player)

		self.visible_sprites.draw(self.display_surface)

		self.player_controller.update()
		self.visible_sprites.update()
		# for player in self.players:
		# 	self.visible_sprites.enemy_update(player)
		# 	self.player_attack_logic(player)
		

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
