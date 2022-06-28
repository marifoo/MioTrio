import pygame 
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self,pos,groups,sprite_type,surface = pygame.Surface((TILESIZE,TILESIZE))):
		super().__init__(groups)
		#self.sprite_type = sprite_type
		y_offset = HITBOX_OFFSET[sprite_type]
		self.image = surface
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,y_offset)



class StandardTile(pygame.sprite.Sprite):
	def __init__(self,size,x,y):
		super().__init__()
		self.image = pygame.Surface((size,size))
		self.rect = self.image.get_rect(topleft = (x,y))

class StaticTile(StandardTile):
	def __init__(self,size,x,y,surface):
		super().__init__(size,x,y)
		self.image = surface