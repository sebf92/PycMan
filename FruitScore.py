import pygame

class FruitScore(pygame.sprite.Sprite):
	SCORE100 = 0
	SCORE300 = 1
	SCORE500 = 2
	SCORE700 = 3
	SCORE1000 = 4
	SCORE2000 = 5
	SCORE3000 = 6
	SCORE5000 = 7
	TTL = 2000 # TTL en ms

	tiles = pygame.image.load("./sprites/sprites.png")
	scorevalues = [100, 300, 500, 700, 1000, 2000, 3000, 5000]
	imagelist = None
	empty = None

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		if(FruitScore.imagelist==None):
			FruitScore.imagelist = list()
			FruitScore.tiles = FruitScore.tiles.convert_alpha()
			FruitScore.tiles.set_colorkey((0,0,0))
			for i in range(57, 65, 2):
				img = FruitScore.tiles.subsurface(pygame.Rect(16*i,16*18,32,32)).convert_alpha()
				FruitScore.imagelist.append(img)
			img = FruitScore.tiles.subsurface(pygame.Rect(1040,16*18,32,32)).convert_alpha() # 1000
			FruitScore.imagelist.append(img)
			img = FruitScore.tiles.subsurface(pygame.Rect(1036,16*20,32,32)).convert_alpha() # 2000
			FruitScore.imagelist.append(img)
			img = FruitScore.tiles.subsurface(pygame.Rect(1036,16*22,32,32)).convert_alpha() # 3000
			FruitScore.imagelist.append(img)
			img = FruitScore.tiles.subsurface(pygame.Rect(1036,16*24,32,32)).convert_alpha() # 5000
			FruitScore.imagelist.append(img)

			FruitScore.empty = FruitScore.tiles.subsurface(pygame.Rect(1200,48,32,32)).convert_alpha() # carré noir

		self.scoretype = FruitScore.SCORE100
		self.image = FruitScore.imagelist[self.scoretype]
		self.rect = pygame.Rect(0,0,32,32)

		self.currentimage = FruitScore.imagelist[self.scoretype]
		self.x = 0
		self.y = 0

		self.t = 0
		self.flipflop = 0
		self.totaltime = 0


	def update(self,time):

		self.t += time
		self.totaltime += time
		if(self.t>250): #on fait clignoter le score
			self.t=0
			self.flipflop = (self.flipflop+1)%2
			if(self.flipflop==0):
				self.image = self.currentimage
			else:
				self.image = FruitScore.empty

		self.rect = pygame.Rect(self.x*16,self.y*16-8,32,32)

		if(self.totaltime>FruitScore.TTL):
			self.kill()

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setScore(self, score):
		'''
		SCORE100 = 0
		SCORE300 = 1
		SCORE500 = 2
		SCORE700 = 3
		SCORE1000 = 4
		SCORE2000 = 5
		SCORE3000 = 6
		SCORE5000 = 7
		'''
		self.scoretype = score
		self.scoretype = min(max(0, self.scoretype), len(FruitScore.imagelist)-1)
		self.currentimage = FruitScore.imagelist[self.scoretype]
		self.image = self.currentimage

	def getScoreValue(self):
		return FruitScore.scorevalues[self.scoretype]