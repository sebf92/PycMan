import pygame, time, random

# The first bonus fruit appears after 70 dots have been cleared from the maze; the second one appears after 170 dots are cleared
# the amount of time it stays on the screen before disappearing is always between nine and ten seconds
class Fruit(pygame.sprite.Sprite):
	CHERRIES = 0
	STRAWBERRY = 1
	PEACH = 2
	APPLE = 3
	GRAPES = 4
	GALAXIAN = 5
	BELL = 6
	KEY = 7

	TTL = 9+random.randint(0,10)/10

	scores = [100, 300, 500, 700, 1000, 2000, 3000, 5000]
	tiles = pygame.image.load("./sprites/sprites.png")
	imagelist = None

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		if(Fruit.imagelist==None):
			Fruit.imagelist = list()
			Fruit.tiles = Fruit.tiles.convert_alpha()
			Fruit.tiles.set_colorkey((0,0,0))
			for i in range (2,10): # on récupère les fruits dans la map
				img = Fruit.tiles.subsurface(pygame.Rect(i*32+16*57,96,32,32))
				Fruit.imagelist.append(img)


		self.current = 0
		self.image = Fruit.imagelist[self.current]
		self.rect = pygame.Rect(0,0,32,32)

		self.x = x
		self.y = y

		self.deadline = time.time()+Fruit.TTL # moment ou le fruit "meurt/disparait"

	def update(self,t):
		self.image = Fruit.imagelist[self.current]
		self.rect = pygame.Rect(self.x*16,self.y*16-8,32,32)

		if(time.time()>self.deadline):
			self.kill() # timeout, le fruit disparait

	def setXY(self, x, y):
		(self.x, self.y) = (x, y)

	def getXY(self):
		return (self.x, self.y)

	def setFruit(self, nb):
		'''
		CHERRY = 0
		STRAWBERRY = 1
		ORANGE = 2
		APPLE = 3
		GRAPEVINE = 4
		FLAME = 5
		GOLD = 6
		KEY = 7
		'''
		self.current = min(max(0, nb), len(Fruit.imagelist)-1)
		self.image = Fruit.imagelist[self.current]

	def getScore(self):
		return Fruit.scores[self.current]

	def playEatenSound(self):			
		sound = pygame.mixer.Sound("sounds/eat_fruit.wav")
		sound.play()
