import pygame

class Gum(pygame.sprite.Sprite):
	tiles = pygame.image.load("./sprites/sprites.png")
	sound1 = None
	sound2 = None

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		if(self.sound1 == None):
			self.sound1 = pygame.mixer.Sound("sounds/munch_1.wav")
			self.sound2 = pygame.mixer.Sound("sounds/munch_2.wav")

		Gum.tiles = Gum.tiles.convert()
		self.image = Gum.tiles.subsurface(pygame.Rect(16,16,16,16))
		self.rect = pygame.Rect(0,0,16,16)

		self.x = x
		self.y = y


	def update(self,time):
		self.rect = pygame.Rect(self.x*16,self.y*16,16,16)

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def playSound1(self):			
		self.sound1.play()

	def playSound2(self):			
		self.sound2.play()
