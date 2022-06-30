import pygame
import pytmx.pytmx

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
	def __init__(self,pos,surf,groups):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, -4)


def hasAnimation(gid, tmx_data):
	return (gid in tmx_data.tile_properties and tmx_data.tile_properties[gid]['frames'])

class AnimationFrames():
	def __init__(self, gid, tmx_data):
		assert hasAnimation(gid, tmx_data)
		self.frame_end_times = []
		self.frame_images = []
		self.frames = tmx_data.tile_properties[gid]['frames']
		duration = 0
		for frame in self.frames:
			self.frame_images.append(tmx_data.get_tile_image_by_gid(frame.gid))
			duration += frame.duration
			self.frame_end_times.append(duration)

class AnimatedTile(pygame.sprite.Sprite):
	def __init__(self,pos,animation_frames,groups):
		super().__init__(groups)
		self.pos = pos
		self.animation_start = pygame.time.get_ticks()
		self.animation_frames = animation_frames
		self.image = self.animation_frames.frame_images[0]
		self.rect = self.image.get_rect(topleft = self.pos)
		self.hitbox = self.rect.inflate(0, -4)

	def update(self):
		current_time = pygame.time.get_ticks()
		current_duration = current_time - self.animation_start
		if current_duration > self.animation_frames.frame_end_times[-1]:
			self.animation_start = current_time
		else:
			for end, image in zip(self.animation_frames.frame_end_times, self.animation_frames.frame_images):
				if current_duration < end:
					self.image = image
					self.rect = self.image.get_rect(topleft=self.pos)
					self.hitbox = self.rect.inflate(0, -4)
					break

class AnimatedTile2(pygame.sprite.Sprite):
	def __init__(self,pos,tmx_data,groups,frames):
		super().__init__(groups)
		self.pos = pos
		self.animation_start = pygame.time.get_ticks()
		self.duration = 0
		self.frame_ends = []
		self.frame_images = []
		for frame in frames:
			self.frame_images.append(tmx_data.get_tile_image_by_gid(frame.gid))
			self.duration += frame.duration
			self.frame_ends.append(self.duration)

		self.image = self.frame_images[0]
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, -4)

	def update(self):
		current_time = pygame.time.get_ticks()
		current_duration = current_time - self.animation_start
		if current_duration > self.duration:
			self.animation_start = current_time
		else:
			for end, image in zip(self.frame_ends, self.frame_images):
				if current_duration < end:
					self.image = image
					self.rect = self.image.get_rect(topleft=self.pos)
					break

class StaticTile(StandardTile):
	def __init__(self,size,x,y,surface):
		super().__init__(size,x,y)
		self.image = surface