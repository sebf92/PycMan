import pygame

class BigGum(pygame.sprite.Sprite):
	tiles = pygame.image.load("./sprites/sprites.png")
	sound = None

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		if(self.sound == None):
			self.sound = pygame.mixer.Sound("sounds/power_pellet.wav")

		BigGum.tiles = BigGum.tiles.convert()
		BigGum.tiles.set_colorkey((0,0,0))
		self.image1 = BigGum.tiles.subsurface(pygame.Rect(16,3*16,16,16)).convert_alpha() # big gum
		self.image2 = BigGum.tiles.subsurface(pygame.Rect(1200,48,16,16)).convert_alpha() # carré noir

		self.image = self.image1
		self.rect = pygame.Rect(0,0,16,16)

		self.x = x
		self.y = y

		self.t = 0
		self.flipflop = 0


	def update(self,time):

		self.t += time
		if(self.t>250): #on fait clignoter la gomme
			self.t=0
			self.flipflop = (self.flipflop+1)%2
			if(self.flipflop==0):
				self.image = self.image1
			else:
				self.image = self.image2

		self.rect = pygame.Rect(self.x*16,self.y*16,16,16)

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def playSound(self):			
		self.sound.play()

