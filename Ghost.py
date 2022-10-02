import pygame, random, time

class Ghost(pygame.sprite.Sprite):
	BLINKYGHOST = 0 # Red
	PINKYGHOST 	= 1 # Pink
	INKYGHOST 	= 2 # Cyan
	CLYDEGHOST	= 3 # Orange

	NONE	= -1
	RIGHT 	= 0
	LEFT 	= 1
	UP 		= 2
	DOWN 	= 3
	GHOST 	= 4
	BLINKINGGHOST 	= 5
	EYERIGHT= 6
	EYELEFT	= 7
	EYEUP 	= 8
	EYEDOWN = 9

	MODESTANDARD 	= 0
	MODEEYE 		= 6
	MODEGHOST 		= 4
	MODEBLINKINGGHOST = 5

	GHOSTPATH 	= 1
	CHASEPATH 	= 2
	SCATTERPATH = 3
	EYEPATH 	= 4 # retourne à la maison
	EXITPATH 	= 5 # sort de la maison

	tiles = pygame.image.load("./sprites/sprites.png")

	# right left up down ghost blinking_ghost eyeright eyeleft eyeup eyedown
	anims = [(0,2,False), (2,2,False), (4,2,False), (6,2,False), (8,2,False), (8,4,False), (12,1,False), (13,1,False), (14,1,False), (15,1,False)]
	#				blinky pinky inky clyde
	scatterpoints = [(26,0),(3,0),(27,33),(2,33)]

	def __init__(self, ghosttype, pacman, ghostgroup, walls, x, y):
		pygame.sprite.Sprite.__init__(self)

		self.ghosttype = ghosttype
		self.walls = walls # les murs
		self.pacman = pacman # pacman
		self.ghostgroup = ghostgroup #le groupe qui contient tous les fantomes

		self.imagelist = list()
		Ghost.tiles = Ghost.tiles.convert_alpha()
		Ghost.tiles.set_colorkey((0,0,0))

		self.empty = Ghost.tiles.subsurface(pygame.Rect(1200,48,32,32)).convert_alpha() # carré noir

		img = Ghost.tiles.subsurface(pygame.Rect(0*32+16*57,32*self.ghosttype+32*4,32,32)) # right
		self.imagelist.append(img)
		img = Ghost.tiles.subsurface(pygame.Rect(1*32+16*57,32*self.ghosttype+32*4,32,32))
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(2*32+16*57,32*self.ghosttype+32*4,32,32)) # left
		self.imagelist.append(img)
		img = Ghost.tiles.subsurface(pygame.Rect(3*32+16*57,32*self.ghosttype+32*4,32,32))
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(4*32+16*57,32*self.ghosttype+32*4,32,32)) # up
		self.imagelist.append(img)
		img = Ghost.tiles.subsurface(pygame.Rect(5*32+16*57,32*self.ghosttype+32*4,32,32))
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(6*32+16*57,32*self.ghosttype+32*4,32,32)) # down
		self.imagelist.append(img)
		img = Ghost.tiles.subsurface(pygame.Rect(7*32+16*57,32*self.ghosttype+32*4,32,32))
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(8*32+16*57,32*4,32,32)) # ghost
		self.imagelist.append(img)
		img = Ghost.tiles.subsurface(pygame.Rect(9*32+16*57,32*4,32,32)) # ghost 
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(10*32+16*57,32*4,32,32)) # ghostblink
		self.imagelist.append(img)
		img = Ghost.tiles.subsurface(pygame.Rect(11*32+16*57,32*4,32,32)) # ghostblink
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(8*32+16*57,32*5,32,32)) # eyeright
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(9*32+16*57,32*5,32,32)) # eyeleft
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(10*32+16*57,32*5,32,32)) # eyeup
		self.imagelist.append(img)

		img = Ghost.tiles.subsurface(pygame.Rect(11*32+16*57,32*5,32,32)) # eyedown
		self.imagelist.append(img)

		self.rect = pygame.Rect(0,0,32,32)

		self.currentDirection = -1
		self.currentMode = Ghost.MODESTANDARD
		self.x = x
		self.y = y
		self.xpos = x*16
		self.ypos = y*16
		self.u = 0
		self.v = 0
		self.velocity = 2

		self.state = 0 # START
		self.imageindex = 0
		self.delay = 0
		self.nbgums = 0
		self.firstExit = False

		self.ghosttimer = 0

		self.scatterx = 0
		self.scattery = 0
		self.currentPathMode = Ghost.SCATTERPATH
		self.levelpathmode = Ghost.SCATTERPATH

		self.doorisopen = False
		self.pausetimer = 0

		self.activateScatterPath()
		self.doRight()

	def update(self,currenttime):
		if(self.currentMode == Ghost.MODEGHOST):
			t = time.time()
			if(t-self.ghosttimer>0):
				self.setMode(Ghost.MODEBLINKINGGHOST)
		if(self.currentMode == Ghost.MODEBLINKINGGHOST):
			t = time.time()
			if(t-self.ghosttimer>0):
				self.resetState()

		timesec = time.time()
		if(timesec>self.pausetimer): # on est pas en mode pause
			# on est sur une case du damier
			if(self.xpos%16==0 and self.ypos%16==0):
				self.x = int(self.xpos/16)
				self.y = int(self.ypos/16)

				if(self.currentPathMode==Ghost.EXITPATH):
					# nous sommes en mode "sortie de la maison"
					if((self.x >= 14 or self.x <= 18) and self.y == 14):
						# nous venons de sortir
						self.setMode(Ghost.MODESTANDARD) # on reinitialise le layout du fantome
						self.closeDoor() # on ferme la porte
						self.resetPath() # on repasse en mode courant
				elif(self.currentPathMode==Ghost.EYEPATH):
					# nous sommes en mode "retour a la maison"
					if(self.x == 15 and self.y == 18):
						# nous sommes arrivés
						self.setMode(Ghost.MODESTANDARD) # on reinitialise le layout du fantome
						self.activateExitPath() # on passe en mode sortie

				if(self.x == 28 and self.y == 17 and self.currentDirection==Ghost.RIGHT): # nous sommes dans le passage secret a droite
					self.x == 1
					self.xpos = 16
				elif(self.x == 1 and self.y == 17 and self.currentDirection==Ghost.LEFT): # nous sommes dans le passage secret a gauche
					self.x == 28
					self.xpos = 28*16

				if(self.currentPathMode==Ghost.GHOSTPATH):
					self.moveGhostPath()
				elif(self.currentPathMode==Ghost.CHASEPATH):
					self.moveChasePath()
				elif(self.currentPathMode==Ghost.SCATTERPATH):
					self.moveScatterPath()
				elif(self.currentPathMode==Ghost.EYEPATH):
					self.moveScatterPath()
				elif(self.currentPathMode==Ghost.EXITPATH):
					self.moveScatterPath()
				
			# on déplace le sprite
			self.xpos += self.u*self.velocity
			self.ypos += self.v*self.velocity

		self.rect = pygame.Rect(self.xpos-8,self.ypos-8,32,32)

		# on selectionne l'image courante
		st = self.state
		if(self.currentMode==Ghost.MODESTANDARD or self.currentMode==Ghost.MODEEYE):
			st += self.currentDirection
		index, nbimage, deadlysequence = Ghost.anims[st]
		self.image = self.imagelist[index+self.imageindex]

		self.delay += currenttime
		if(self.delay>100): # on anime le sprite
			self.delay = 0
			# on passe a l'image suivante
			self.imageindex += 1
			if(self.imageindex==nbimage):
				if(deadlysequence):
					self.kill()
				self.imageindex = 0

		# si on est en mode pause on cache le sprite
		if(self.pausetimer !=0 and timesec<self.pausetimer):
			self.image = self.empty

	def moveGhostPath(self): # mode aleatoire
		reversedirection = self.getReverseDirection()
		availabledirections = self.getAvailableDirections(reversedirection)
		nextdirection = self.getRandomDirection(availabledirections)
		if(nextdirection==Ghost.LEFT):
			self.doLeft()
		elif(nextdirection==Ghost.RIGHT):
			self.doRight()
		elif(nextdirection==Ghost.UP):
			self.doUp()
		elif(nextdirection==Ghost.DOWN):
			self.doDown()

	def moveScatterPath(self): # mode plus court chemin vers un point de reference
		x = self.x
		y = self.y
		distance = 9999999
		direction = None
		reversedirection = self.getReverseDirection()

		# on calcule le chemin le plus court vers le point de référence sur les directions potentielles (sachant qu'on a pas le droit de faire demi tour)
		if(not self.hasWall(x+1,y) and reversedirection!=Ghost.RIGHT): # A droite
			d = self.getDistanceToScatter2(x+1,y)
			if(d<distance):
				distance = d
				direction = Ghost.RIGHT

		if(not self.hasWall(x,y+1) and reversedirection!=Ghost.DOWN): # En bas
			d = self.getDistanceToScatter2(x,y+1)
			if(d<distance):
				distance = d
				direction = Ghost.DOWN

		if(not self.hasWall(x-1,y) and reversedirection!=Ghost.LEFT): # A gauche
			d = self.getDistanceToScatter2(x-1,y)
			if(d<distance):
				distance = d
				direction = Ghost.LEFT

		if(not self.hasWall(x,y-1) and reversedirection!=Ghost.UP): # En haut
			d = self.getDistanceToScatter2(x,y-1)
			if(d<distance):
				distance = d
				direction = Ghost.UP

		# on redirige le fantome
		if(direction==Ghost.LEFT):
			self.doLeft()
		elif(direction==Ghost.RIGHT):
			self.doRight()
		elif(direction==Ghost.UP):
			self.doUp()
		elif(direction==Ghost.DOWN):
			self.doDown()

	def moveChasePath(self): # mode poursuite
		if(self.ghosttype==Ghost.BLINKYGHOST): # Red
			# le rouge poursuit pacman
			(x,y) = self.getBlinkyChasePoint()
			self.setScatterPoint(x, y)
			self.moveScatterPath()
		elif(self.ghosttype==Ghost.PINKYGHOST): # Rose
			# le rose poursuit "presque" pacman: avec un décalage de 4 tiles en avant (+un petit bug si pacman va vers le haut)
			(x,y) = self.getPinkyChasePoint()
			self.setScatterPoint(x, y)
			self.moveScatterPath()
		elif(self.ghosttype==Ghost.CLYDEGHOST): # Orange
			# le orange poursuit pacman sauf si il est proche de lui, il repasse alors en mode "scatter" vers son point d'origine
			(x,y) = self.getClydeChasePoint()
			self.setScatterPoint(x, y)
			self.moveScatterPath()
		else:
			# le bleu prend Pacman en etau avec le rouge: C'est le point opposé au Rouge par rapport au point de chasse de pinky
			(x,y) = self.getInkyChasePoint()
			self.setScatterPoint(x, y)
			self.moveScatterPath()

	def getBlinkyChasePoint(self):
		# le rouge poursuit pacman
		(x,y) = self.pacman.getXY()
		return (x,y)

	def getClydeChasePoint(self):
		# le orange poursuit pacman sauf si il est proche de lui, il repasse alors en mode "scatter" vers son point d'origine
		(pacmanx,pacmany) = self.pacman.getXY()
		distance2 = (self.x-pacmanx)*(self.x-pacmanx)+(self.y-pacmany)*(self.y-pacmany) # calcul de la distance2 entre pacman et le fantome
		if(distance2<64): # si la distance est < 8
			# mode scatter
			(x,y) = self.scatterpoints[self.ghosttype]
			return (x,y)
		else:
			return (pacmanx, pacmany) # sinon mode poursuite de pacman

	def getPinkyChasePoint(self):
		# le rose poursuit "presque" pacman: avec un décalage de 4 tiles en avant (+un petit bug si pacman va vers le haut)
		(x,y) = self.pacman.getXY()
		(u,v) = self.pacman.getUV()
		x += u*4 
		y += v*4
		if(v<0): # si pacman monte alors on décale le point de référence pour simuler le bug d'overflow dans pacman
			x-=4
		return (x,y)

	def getInkyChasePoint(self):
		# le bleu prend Pacman en etau avec le rouge: C'est le point opposé au Rouge par rapport au point de chasse de pinky
		(pinkyx,pinkyy) = self.getPinkyChasePoint() # pinky
		for g in self.ghostgroup:
			if(g.getGhostType()==Ghost.BLINKYGHOST):
				(blinkyx, blinkyy) = g.getXY() # blinky
		
		deltax = pinkyx-blinkyx # on calcule le point symétrique de blinky par rapport à pinky
		deltay = pinkyy-blinkyy

		x = pinkyx-deltax
		y = pinkyy-deltay

		return (x,y)

	def getGhostType(self):
		return self.ghosttype

	def moveEyePath(self): # rentre dans la maison
		self.moveScatterPath()

	def moveExitPath(self): # sort de la maison
		self.moveScatterPath()

	def getXY(self):
		return (self.x, self.y)

	def getMode(self):
		return self.currentMode

	def setMode(self, mode):
		if(self.currentMode != mode):
			self.currentMode = mode
			self.imageindex = 0
			self.delay = 0
			if(mode==Ghost.MODEGHOST):
				self.ghosttimer = time.time()+10 #current time in seconds
				self.state = Ghost.GHOST
				self.reverseDirection()
				self.velocity = 1
			if(mode==Ghost.MODEBLINKINGGHOST):
				self.ghosttimer = time.time()+5 #current time in seconds
				self.state = Ghost.BLINKINGGHOST
			if(mode==Ghost.MODESTANDARD):
				self.ghosttimer = 0
				self.state = Ghost.RIGHT
				self.velocity = 2
				self.realignSprite() # on realigne le sprite sur la grille car on change sa velocité et on veut etre sur d'etre sur un multiple de 16 pour les collisions
			if(mode==Ghost.MODEEYE):
				self.ghosttimer = 0
				self.state = Ghost.EYERIGHT
				self.reverseDirection()
				self.velocity = 4
				self.realignSprite() # on realigne le sprite sur la grille car on change sa velocité et on veut etre sur d'etre sur un multiple de 16 pour les collisions
			

	def exitMode(self):
		self.setMode(self.MODESTANDARD)
		self.activateExitPath()
		self.openDoor()

	def launchGhost(self):
		if(not self.firstExit):
			self.firstExit = True
			self.realignSprite()
			self.exitMode()

	def ghostMode(self):
		self.setMode(self.MODEGHOST)
		self.activateGhostPath()

	def eyeMode(self):
		self.playGhostEatenSound()
		self.setMode(self.MODEEYE)
		self.activateEyePath()
		self.openDoor()
		self.pausetimer = time.time()+2 # sprite immobile durant 2 secondes

	def doRight(self):
		if(self.currentDirection!=Ghost.RIGHT):
			self.currentDirection = Ghost.RIGHT
			self.u = 1
			self.v = 0

	def doLeft(self):
		if(self.currentDirection!=Ghost.LEFT):
			self.currentDirection = Ghost.LEFT
			self.u = -1
			self.v = 0

	def doUp(self):
		if(self.currentDirection!=Ghost.UP):
			self.currentDirection = Ghost.UP
			self.u = 0
			self.v = -1

	def doDown(self):
		if(self.currentDirection!=Ghost.DOWN):
			self.currentDirection = Ghost.DOWN
			self.u = 0
			self.v = 1

	def stop(self):
		self.u = 0
		self.v = 0

	def getAvailableDirections(self, excludedirection=-1):
		r = list()
		if(self.walls[self.x+1][self.y]==0 and not excludedirection==Ghost.RIGHT):
			r.append(Ghost.RIGHT)
		if(self.walls[self.x-1][self.y]==0 and not excludedirection==Ghost.LEFT):
			r.append(Ghost.LEFT)
		if(self.walls[self.x][self.y-1]==0 and not excludedirection==Ghost.UP):
			r.append(Ghost.UP)
		if(self.walls[self.x][self.y+1]==0 and not excludedirection==Ghost.DOWN):
			r.append(Ghost.DOWN)
		return r

	def getRandomDirection(self, availabledirections):
		'''
		availabledirections
		Is a list, can be right, left, up, down
		'''
		r = random.randint(0, len(availabledirections)-1)
		return availabledirections[r]


	def reverseDirection(self):
		r = self.getReverseDirection()
		if(r==self.LEFT):
			self.doLeft()
		elif(r==self.RIGHT):
			self.doRight()
		elif(r==self.UP):
			self.doUp()
		elif(r==self.DOWN):
			self.doDown()

	def getReverseDirection(self):
		reversedirection = -1
		if(self.currentDirection == self.RIGHT):
			reversedirection = self.LEFT
		elif(self.currentDirection == self.LEFT):
			reversedirection = self.RIGHT
		elif(self.currentDirection == self.DOWN):
			reversedirection = self.UP
		elif(self.currentDirection == self.UP):
			reversedirection = self.DOWN
		return reversedirection

	def resetState(self):
		self.state = Ghost.RIGHT
		self.imageindex = 0
		self.setMode(Ghost.MODESTANDARD)
		self.setPath(self.levelpathmode)

	def realignSprite(self):
		if(self.xpos%16>=8):
			self.xpos += 16-self.xpos%16
		else:
			self.xpos -= self.xpos%16

		if(self.ypos%16>=8):
			self.ypos += 16-self.ypos%16
		else:
			self.ypos -= self.ypos%16

	def setScatterPoint(self,x,y):
		x = max(x,0)
		y = max(y,0)

		self.scatterx = x
		self.scattery = y

	def setPath(self, pathmode):
		self.currentPathMode = pathmode

	def resetPath(self):
		self.currentPathMode = self.levelpathmode

	def activateEyePath(self):
		self.setScatterPoint(15, 18)
		self.currentPathMode = self.EYEPATH

	def activateExitPath(self):
		self.setScatterPoint(15, 14)
		self.currentPathMode = self.EXITPATH

	def activateChasePath(self):
		self.currentPathMode = self.CHASEPATH

	def activateScatterPath(self):
		self.currentPathMode = self.SCATTERPATH
		(self.scatterx, self.scattery) = Ghost.scatterpoints[self.ghosttype]

	def activateGhostPath(self):
		self.currentPathMode = self.GHOSTPATH

	def setNbGums(self, nb):
		self.nbgums = nb

	def getNbGums(self):
		return self.nbgums

	def hasWall(self, x, y):
		sizex = len(self.walls)
		sizey = len(self.walls[0])

		# on teste les cas limites et on les fait apparaitre comme des murs
		if(x<0 or y<0):
			return True
		if(x>=sizex or y>=sizey):
			return True

		if(self.walls[x][y]==2):
			test = True

		if(self.isOpenDoor()):
			return self.walls[x][y]==1
		else:
			return self.walls[x][y]!=0

	def openDoor(self):
		self.doorisopen = True

	def closeDoor(self):
		self.doorisopen = False

	def isOpenDoor(self):
		return self.doorisopen

	def getDistanceToScatter2(self, x, y):
		return (x-self.scatterx)*(x-self.scatterx)+(y-self.scattery)*(y-self.scattery)

	def forceChasePathMode(self):
		if(self.currentPathMode == Ghost.SCATTERPATH):
			self.levelpathmode = Ghost.CHASEPATH
			self.activateChasePath()

	def setCurrentPathMode(self, levelpathmode):
		self.levelpathmode = levelpathmode
		# on bascule le path immédiatement si nous sommes sur un chemin "standard"
		if(self.currentPathMode == Ghost.SCATTERPATH or self.currentPathMode == Ghost.CHASEPATH):
			if(levelpathmode == Ghost.SCATTERPATH):
				self.activateScatterPath()
				self.reverseDirection()
			elif(levelpathmode == Ghost.CHASEPATH):
				self.activateChasePath()
				self.reverseDirection()

	def playGhostEatenSound(self):			
		sound = pygame.mixer.Sound("sounds/eat_ghost.wav")
		sound.play()
