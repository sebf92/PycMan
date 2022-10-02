import pygame

class Ready(pygame.sprite.Sprite):
	tiles = pygame.image.load("./sprites/sprites.png")

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		Ready.tiles = Ready.tiles.convert()
		self.image = Ready.tiles.subsurface(pygame.Rect(920,322,110,26))
		self.rect = pygame.Rect(0,0,110,26)

		self.x = x
		self.y = y

	def update(self,time):
		self.rect = pygame.Rect(self.x*16,self.y*16-4,110,26)

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)
