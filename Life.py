import pygame

class Life(pygame.sprite.Sprite):
	LEFT = 1174
	TOP = 36
	WIDTH = 20
	HEIGHT=22

	spriteSheet = pygame.image.load("./sprites/sprites.png")
	laserSound = None

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.rect = pygame.Rect(0,0,Life.WIDTH,Life.HEIGHT)
		self.image = Life.spriteSheet.subsurface(pygame.Rect(Life.LEFT,Life.TOP,Life.WIDTH,Life.HEIGHT))
		self.mask = pygame.mask.from_surface(self.image)


	def update(self,time):
		nop = 1


	def setPosition(self, x,y):
		self.rect = pygame.Rect(x,y,Life.WIDTH, Life.HEIGHT)
