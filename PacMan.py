import pygame

class PacMan(pygame.sprite.Sprite):
	NONE	= -1
	LEFT 	= 1
	RIGHT 	= 0
	UP 		= 2
	DOWN 	= 3
	START 	= 4
	DEAD 	= 5

	tiles = pygame.image.load("./sprites/sprites.png")
	imagelist = None

	# left right up down start dead
	anims = [(0,2,False), (2,2,False), (4,2,False), (6,2,False), (8,1,False), (9,11,True)]

	def __init__(self, walls, x, y):
		pygame.sprite.Sprite.__init__(self)

		self.walls = walls # les murs

		if(PacMan.imagelist==None):
			PacMan.imagelist = list()
			PacMan.tiles = PacMan.tiles.convert_alpha()
			PacMan.tiles.set_colorkey((0,0,0))

			img = PacMan.tiles.subsurface(pygame.Rect(16*57,0,32,32)) # right
			PacMan.imagelist.append(img)
			img = PacMan.tiles.subsurface(pygame.Rect(32+16*57,0,32,32))
			PacMan.imagelist.append(img)

			img = PacMan.tiles.subsurface(pygame.Rect(16*57,32,32,32)) # left
			PacMan.imagelist.append(img)
			img = PacMan.tiles.subsurface(pygame.Rect(32+16*57,32,32,32))
			PacMan.imagelist.append(img)

			img = PacMan.tiles.subsurface(pygame.Rect(16*57,64,32,32)) # up
			PacMan.imagelist.append(img)
			img = PacMan.tiles.subsurface(pygame.Rect(32+16*57,64,32,32))
			PacMan.imagelist.append(img)

			img = PacMan.tiles.subsurface(pygame.Rect(16*57,96,32,32)) # down
			PacMan.imagelist.append(img)
			img = PacMan.tiles.subsurface(pygame.Rect(32+16*57,96,32,32))
			PacMan.imagelist.append(img)

			img = PacMan.tiles.subsurface(pygame.Rect(2*32+16*57,0,32,32)) # start
			PacMan.imagelist.append(img)

			for i in range(11): # dead
				img = PacMan.tiles.subsurface(pygame.Rect(i*32+3*32+16*57,0,32,32)) 
				PacMan.imagelist.append(img)


		self.rect = pygame.Rect(0,0,32,32)

		self.x = x
		self.y = y
		self.xpos = x*16
		self.ypos = y*16
		self.xinc = 0
		self.yinc = 0
		self.u = 0
		self.v = 0

		self.nextdirection = PacMan.NONE
		self.state = PacMan.START # START
		self.imageindex = 0
		self.delay = 0

	def update(self,time):
		# on est sur une case du damier
		if(self.xpos%16==0 and self.ypos%16==0):
			self.x = int(self.xpos/16)
			self.y = int(self.ypos/16)

			if(self.x == 28 and self.y == 17 and self.u==1): # nous sommes dans le passage secret a droite
				self.x == 1
				self.xpos = 16
			elif(self.x == 1 and self.y == 17 and self.u==-1): # nous sommes dans le passage secret a gauche
				self.x == 28
				self.xpos = 28*16

			# on test si on peut changer de direction (suite a un appui sur une touche)
			if(self.nextdirection==PacMan.LEFT):
				iswall = self.hasWall(self.x-1,self.y)
				if(iswall==0):
					self.doLeft()
			elif(self.nextdirection==PacMan.RIGHT):
				iswall = self.hasWall(self.x+1,self.y)
				if(iswall==0):
					self.doRight()
			elif(self.nextdirection==PacMan.UP):
				iswall = self.hasWall(self.x,self.y-1)
				if(iswall==0):
					self.doUp()
			elif(self.nextdirection==PacMan.DOWN):
				iswall = self.hasWall(self.x,self.y+1)
				if(iswall==0):
					self.doDown()

			# on test si on entre en collision avec un mur
			iswall = self.hasWall(self.x+self.u,self.y+self.v)
			if(iswall!=0): # si oui, on s'arrete
				self.stop()

		# on déplace le sprite
		self.xpos += self.xinc
		self.ypos += self.yinc

		self.rect = pygame.Rect(self.xpos-8,self.ypos-8,32,32)

		# on selectionne l'image courante
		index, nbimage, deadlysequence = PacMan.anims[self.state]
		self.image = PacMan.imagelist[index+self.imageindex]

		self.delay += time
		if(self.delay>100): # on anime le sprite
			self.delay = 0
			# on passe a l'image suivante
			self.imageindex += 1
			if(self.imageindex==nbimage):
				if(deadlysequence):
					self.kill()
				self.imageindex = 0

	def setXY(self, x, y):
		self.x = x
		self.y = y
		self.xpos = x*16
		self.ypos = y*16
		self.xinc = 0
		self.yinc = 0
		self.u = 0
		self.v = 0
		self.state = PacMan.START

	def getXY(self):
		return (self.x, self.y)

	def getUV(self):
		return (self.u, self.v)

	def setState(self, state):
		'''
		LEFT 	= 0
		RIGHT 	= 1
		UP 		= 2
		DOWN 	= 3
		START 	= 4
		DEAD 	= 5
		'''		
		self.state = state
		self.imageindex = 0
		self.delay = 0

	def goLeft(self):
		if(self.state!=PacMan.DEAD):
			self.nextdirection = PacMan.LEFT
	def goRight(self):
		if(self.state!=PacMan.DEAD):
			self.nextdirection = PacMan.RIGHT
	def goUp(self):
		if(self.state!=PacMan.DEAD):
			self.nextdirection = PacMan.UP
	def goDown(self):
		if(self.state!=PacMan.DEAD):
			self.nextdirection = PacMan.DOWN

	def doLeft(self):
		self.setState(PacMan.LEFT)
		self.xinc = -2
		self.yinc = 0
		self.u = -1
		self.v = 0
		self.nextdirection = PacMan.NONE

	def doRight(self):
		self.setState(PacMan.RIGHT)
		self.xinc = 2
		self.yinc = 0
		self.u = 1
		self.v = 0
		self.nextdirection = PacMan.NONE

	def doUp(self):
		self.setState(PacMan.UP)
		self.xinc = 0
		self.yinc = -2
		self.u = 0
		self.v = -1
		self.nextdirection = PacMan.NONE

	def doDown(self):
		self.setState(PacMan.DOWN)
		self.xinc = 0
		self.yinc = 2
		self.u = 0
		self.v = 1
		self.nextdirection = PacMan.NONE

	def stop(self):
		self.xinc = 0
		self.yinc = 0
		#self.u = 0 # on garde tout de meme les vecteurs pour connaitre l'orientation de pacman meme si il est arreté
		#self.v = 0
		self.nextdirection = PacMan.NONE

	def die(self):
		if(self.state!=PacMan.DEAD):
			self.playDieSound()
			self.stop()
			self.setState(PacMan.DEAD)

	def hasWall(self, x, y):
		sizex = len(self.walls)
		sizey = len(self.walls[0])

		# on teste les cas limites et on les fait apparaitre comme des murs
		if(x<0 or y<0):
			return True
		if(x>=sizex or y>=sizey):
			return True

		return self.walls[x][y]!=0

	def playDieSound(self):
		pygame.mixer.music.load('sounds/death_1.wav') # mort...
		pygame.mixer.music.play()
