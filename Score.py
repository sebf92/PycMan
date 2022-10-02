import pygame

class Score(pygame.sprite.Sprite):
	SCORE200 = 0
	SCORE400 = 1
	SCORE800 = 2
	SCORE1600 = 3
	TTL = 2000 # TTL en ms

	tiles = pygame.image.load("./sprites/sprites.png")
	scorevalues = [200, 400, 800, 1600]
	imagelist = None
	empty = None

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		if(Score.imagelist==None):
			Score.imagelist = list()
			Score.tiles = Score.tiles.convert_alpha()
			Score.tiles.set_colorkey((0,0,0))
			for i in range(57, 65, 2):
				img = Score.tiles.subsurface(pygame.Rect(16*i,16*16,32,32)).convert_alpha() # 200
				Score.imagelist.append(img)
			Score.empty = Score.tiles.subsurface(pygame.Rect(1200,48,32,32)).convert_alpha() # carré noir

		self.scoretype = Score.SCORE200
		self.image = Score.imagelist[self.scoretype]
		self.rect = pygame.Rect(0,0,32,32)

		self.currentimage = Score.imagelist[self.scoretype]
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
				self.image = Score.empty

		self.rect = pygame.Rect(self.x*16-8,self.y*16-8,32,32)

		if(self.totaltime>Score.TTL):
			self.kill()

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setScore(self, score):
		'''
		SCORE200 = 0
		SCORE400 = 1
		SCORE800 = 2
		SCORE1600 = 3
		'''
		self.scoretype = score
		self.scoretype = min(max(0, self.scoretype), len(Score.imagelist)-1)
		self.currentimage = Score.imagelist[self.scoretype]
		self.image = self.currentimage

	def getScoreValue(self):
		return Score.scorevalues[self.scoretype]