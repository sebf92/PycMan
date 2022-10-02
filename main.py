# #####################################################################################
#
# Un exemple de jeu de pacman en Python
#
# https://www.gamasutra.com/view/feature/3938/the_pacman_dossier.php?print=1
# https://www.youtube.com/watch?v=ataGotQ7ir8&list=WL&index=3&t=764s&ab_channel=RetroGameMechanicsExplained
# https://www.youtube.com/watch?v=7O1OYQRqUag&ab_channel=hirudov2d
# #####################################################################################

# Ne pas oublier d'installer les librairies manquantes:
# pip install pygame
# pip install pytmx
# pip install moderngl

import pygame, pytmx ,sys, time

from Gum import Gum
from BigGum import BigGum
from PacMan import PacMan
from Ghost import Ghost
from Life import Life
from Score import Score
from Fruit import Fruit
from Ready import Ready
from FruitScore import FruitScore
from Colliders import collide_same16block
from TextOverlay import TextOverlay
from CRTShader import CRTShader

# Paramètres principaux du jeu
WIDTH = CRTShader.WIDTH
HEIGHT = CRTShader.HEIGHT
FPS = 60 
NBLIFE = 3
FULLSCREEN = True
INVINCIBLE = False
CRTEFFECT = True
TITLE = "PycMan"

# On initialise les variables du jeu
pygame.init()
pygame.mixer.init()
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
if(joystick_count>0):
	joystick = pygame.joystick.Joystick(0)
	joystick.init()
else:
	joystick = None

shader = CRTShader(FULLSCREEN, CRTEFFECT)
screen = shader.getScreen()

if(FULLSCREEN):
	pygame.mouse.set_visible(False)
pygame.display.set_caption(TITLE)

# timing pour les changements de strategie de chemins des fantomes en fonction du temps (en secondes depuis le début de la partie)
timings1 = [(Ghost.SCATTERPATH, 7), (Ghost.CHASEPATH, 20), (Ghost.SCATTERPATH, 7), (Ghost.CHASEPATH, 20), (Ghost.SCATTERPATH, 5), (Ghost.CHASEPATH, 20), (Ghost.SCATTERPATH, 7), (Ghost.CHASEPATH, 9999) ]
timings2 = [(Ghost.SCATTERPATH, 7), (Ghost.CHASEPATH, 20), (Ghost.SCATTERPATH, 7), (Ghost.CHASEPATH, 20), (Ghost.SCATTERPATH, 5), (Ghost.CHASEPATH, 9999) ]
timings3 = [(Ghost.SCATTERPATH, 5), (Ghost.CHASEPATH, 20), (Ghost.SCATTERPATH, 5), (Ghost.CHASEPATH, 20), (Ghost.SCATTERPATH, 5), (Ghost.CHASEPATH, 9999) ]
timings = list()
timings.append(timings1) # level 1
timings.append(timings2) # level 2
timings.append(timings2) # level 3
timings.append(timings2) # level 4
timings.append(timings2) # level 5
timings.append(timings3) # level 6+

# nombre de gums restantes pour que blinky soit forcé en "chase mode" en fonction du niveau
blinkyforcechasemode = [20, 30, 40, 40, 40, 50, 50, 50, 60, 60, 60, 80, 80, 80, 100, 100, 100, 100, 120]

# nombre de gums mangées avant que pinky, inky et clyde sortent de la maison en fonction du niveau
ghostwaitgums = [(0,30,60), (0, 0, 50), (0, 0, 0)]

# les bonus a faire apparaitre en fonction du niveau
fruitbonus = [Fruit.CHERRIES, Fruit.STRAWBERRY, Fruit.PEACH, Fruit.PEACH, Fruit.APPLE, Fruit.APPLE, Fruit.GRAPES, Fruit.GRAPES, Fruit.GALAXIAN, Fruit.GALAXIAN, Fruit.BELL, Fruit.BELL, Fruit.KEY]

# le facteur de vitesse du jeu en fonction du niveau
levelspeed = [0.8,0.9,0.9,0.9,0.9,1.0]

while True:
	# ##################################################
	# ##################################################
	# Ecran d'accueil
	# ##################################################
	# ##################################################
	pygame.mixer.music.load('sounds/Pac-man theme remix.mp3')
	splashscreen = pygame.image.load("./background/splashscreen.png")
	screen.blit(splashscreen, (0, 0))

	pygame.mixer.music.play(loops=-1)
	clock = pygame.time.Clock()
	next = False
	while not next:
		# on limite l'affichage à FPS images par secondes
		currenttime = clock.tick(FPS)	

		# on gère les evenements clavier
		###################
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				pygame.quit()
				sys.exit(0)
			elif event.type == pygame.JOYBUTTONDOWN:
				next = True
			elif event.type == pygame.KEYDOWN:
				# on quitte si on appui sur la touche ESC
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit(0)
				else:
					next = True


		# et on met à jour l'affichage ecran
		shader.render()

	pygame.mixer.music.fadeout(1000)
	screen.fill((0,0,0))

	extralife = False
	currentnblife = NBLIFE
	currentLevel = 0
	score = 0
	while True: # on boucle sur les niveaux
		tm = pytmx.load_pygame('level.tmx')
		tileWidth = tm.tilewidth
		tileHeight = tm.tileheight
		playfield = pygame.Rect((0, 0), (tm.width*tileWidth, tm.height*tileHeight))

		# on prépare la liste des gums et des supergums
		allgums = pygame.sprite.RenderClear()
		gommes = tm.get_layer_by_name("gommes")
		for x, y, image in gommes.tiles():
			gum = Gum(x, y)
			allgums.add(gum)

		allbiggums = pygame.sprite.RenderClear()
		gommes = tm.get_layer_by_name("supergommes")
		for x, y, image in gommes.tiles():
			gum = BigGum(x, y)
			allbiggums.add(gum)

		bonusscore = pygame.sprite.RenderClear()

		# On charge le niveau
		while True: # On recommence le niveau tant qu'il reste des vies

			# on crée une grosse image qui contient tout le playfield
			buffer = pygame.Surface((playfield.width, playfield.height))
			buffer.fill((0,0,0))
			background = pygame.Surface((playfield.width, playfield.height))
			background.fill((0,0,0))

			# on dessine le playfield
			# Les murs
			walls = [[0 for y in range(37)] for x in range(30)]
			layer = tm.get_layer_by_name("murs")
			for x, y, image in layer.tiles():
				buffer.blit(image,(x*tileWidth,y*tileHeight))
				background.blit(image,(x*tileWidth,y*tileHeight))
				walls[x][y] = 1 # on marque la case comme étant occupée par un mur

			layer = tm.get_layer_by_name("porte")
			for x, y, image in layer.tiles():
				buffer.blit(image,(x*tileWidth,y*tileHeight))
				background.blit(image,(x*tileWidth,y*tileHeight))
				walls[x][y] = 2 # on marque la case comme étant occupée par une porte

			# on initialise les textes
			textgroup = pygame.sprite.RenderClear()
			scoreoverlay = TextOverlay()
			scoreoverlay.setPosition(180, 0)
			scoreoverlay.setText(str(0).zfill(6))
			textgroup.add(scoreoverlay)
			leveloverlay = TextOverlay()
			leveloverlay.setPosition(20, 540)
			leveloverlay.setText('')
			textgroup.add(leveloverlay)

			# on initialise les vies
			lifegroup = pygame.sprite.RenderClear()
			for i in range (currentnblife):
				life = Life()
				life.setPosition(440-i*24, 550)
				lifegroup.add(life)

			# on initialise PacMan
			pacmangroup = pygame.sprite.RenderClear()
			pacman = PacMan(walls,15,26)
			pacmangroup.add(pacman)

			# on initialise le groupe qui contient les bonus
			fruitbonusgroup = pygame.sprite.RenderClear()

			# pinky, inky et clyde
			pinkywaitgums, inkywaitgums, clydewaitgums = ghostwaitgums[min(currentLevel, len(ghostwaitgums)-1)]

			#	BLINKYGHOST = 0 # Red
			#	PINKYGHOST 	= 1 # Pink
			#	INKYGHOST 	= 2 # Cyan
			#	CLYDEGHOST	= 3 # Orange

			lockedghostgroup = pygame.sprite.RenderClear()
			ghostgroup = pygame.sprite.RenderClear()

			blinky = Ghost(Ghost.BLINKYGHOST, pacman, ghostgroup, walls, 15, 14) # Red
			blinky.setNbGums(0)
			blinky.closeDoor()
			blinky.activateScatterPath()
			ghostgroup.add(blinky)

			ghost = Ghost(Ghost.CLYDEGHOST, pacman, ghostgroup, walls, 13, 18) # Orange
			ghost.setNbGums(clydewaitgums)
			ghost.closeDoor()
			ghost.activateScatterPath()
			lockedghostgroup.add(ghost)

			ghost = Ghost(Ghost.INKYGHOST, pacman, ghostgroup, walls, 15, 18) # Cyan
			ghost.setNbGums(inkywaitgums)
			ghost.closeDoor()
			ghost.activateScatterPath()
			lockedghostgroup.add(ghost)

			ghost = Ghost(Ghost.PINKYGHOST, pacman, ghostgroup, walls, 17, 18) # Pink
			ghost.setNbGums(pinkywaitgums)
			ghost.closeDoor()
			ghost.activateScatterPath()
			lockedghostgroup.add(ghost)

			timing = timings[min(currentLevel, len(timings)-1)] # on récupère les timings du niveau courant
			currenttimingsequence = 0 # on démarre à 0
			currentpath, currenttiming = timing[currenttimingsequence]
			currenttiming = time.time()+currenttiming # on calcule le timing
			for g in ghostgroup: # on change la stratégie de chemin
				g.setCurrentPathMode(currentpath)

			# on colle le logo Ready
			ready = Ready(12, 20)
			bonusscore.add(ready)

			# on calcule le nombre d'images par seconde en fonction du niveau
			LEVELFPS = int(FPS * levelspeed[min(currentLevel, len(levelspeed)-1)])

			# ##################################################
			# ##################################################
			# Boucle principale du jeu
			# ##################################################
			# ##################################################
			clock = pygame.time.Clock()
			winstatus = None
			nbgums = 0
			intromusic = False
			isinghostmode = False
			nbghosteaten = 0
			nbfruitbonus = 0
			leveloverlay.setText('Level '+str(currentLevel+1))
			while winstatus==None:
				# on a dépassé les 10000 points? on gagne une vie
				if(score>10000 and not extralife):
					extralife = True # une seule fois par partie...
					sound = pygame.mixer.Sound("sounds/extend.wav") # on joue un son
					sound.play()
					currentnblife += 1 #on ajoute une vie
					life = Life() # on ajoute une vie dans le groupe de sprite
					life.setPosition(440-(currentnblife-1)*24, 550)
					lifegroup.add(life)

				# on affiche un bonus a 70 et 170 pacgums mangées
				if(nbgums>=70 and nbfruitbonus==0):
					# on affiche le premier bonus
					fruit = Fruit(14, 20)
					fruit.setFruit(currentLevel)
					fruitbonusgroup.add(fruit)
					nbfruitbonus += 1
				elif(nbgums>=170 and nbfruitbonus==1):
					# on affiche le deuxieme bonus
					fruit = Fruit(14, 20)
					fruit.setFruit(currentLevel)
					fruitbonusgroup.add(fruit)
					nbfruitbonus += 1

				# on libère les fantomes en fonction du nombre de pacgums mangées
				for g in lockedghostgroup:
					trigger = g.getNbGums()
					if(nbgums>=trigger):
						g.launchGhost()
						ghostgroup.add(g)
						lockedghostgroup.remove(g)

				# on gère les strategies de chemin
				t = time.time()
				if(t>currenttiming): # on est arrivé au bout du timing
					currenttimingsequence += 1
					currenttimingsequence = min(currenttimingsequence, len(timing)-1)
					currentpath, currenttiming = timing[currenttimingsequence]
					currenttiming = time.time()+currenttiming # on calcule le timing
					for g in ghostgroup: # on change la stratégie de chemin régulierement
						if(len(allgums)+len(allbiggums)<blinkyforcechasemode[currentLevel] and g.getGhostType()==Ghost.BLINKYGHOST): # il reste peu de gums et le fantome est BLINKY
							g.forceChasePathMode() # on force le mode
						else:
							g.setCurrentPathMode(currentpath) # on prend le mode courant
					for g in lockedghostgroup: # on change la stratégie de chemin régulierement
						g.setCurrentPathMode(currentpath) # on prend le mode courant

				if(len(allgums)+len(allbiggums)<blinkyforcechasemode[currentLevel] and g.getGhostType()==Ghost.BLINKYGHOST): # il reste peu de gums et le fantome est BLINKY
					blinky.forceChasePathMode() # on force le mode

				# on limite l'affichage à FPS images par secondes
				currenttime = clock.tick(LEVELFPS)	
				
				# on gère les evenements clavier
				###################
				for event in pygame.event.get():
					if event.type == pygame.QUIT: 
						pygame.quit()
						sys.exit(0)
					elif event.type == pygame.JOYBUTTONDOWN:
						if event.button == 11: # UP
							pacman.goUp()
						elif event.button == 12: # DOWN
							pacman.goDown()
						elif event.button == 13: # LEFT
							pacman.goLeft()
						elif event.button == 14: # RIGHT
							pacman.goRight()
					elif event.type == pygame.KEYDOWN:
						# on quitte si on appui sur la touche ESC
						if event.key == pygame.K_ESCAPE:
							pygame.quit()
							sys.exit(0)
						elif event.key == pygame.K_UP:
							pacman.goUp()
						elif event.key == pygame.K_DOWN:
							pacman.goDown()
						elif event.key == pygame.K_LEFT:
							pacman.goLeft()
						elif event.key == pygame.K_RIGHT:
							pacman.goRight()

				# on met a jour les positions
				pacmangroup.update(currenttime)
				ghostgroup.update(currenttime)
				lockedghostgroup.update(currenttime)
				allgums.update(currenttime)
				allbiggums.update(currenttime)
				fruitbonusgroup.update(currenttime)

				# on teste les collisions

				# avec les bonus
				collisionlist = pygame.sprite.spritecollide(pacman,fruitbonusgroup,True, collide_same16block)
				for fbonus in collisionlist:
					score += fbonus.getScore()
					fbonus.playEatenSound()
					# on affiche le score du bonus
					gx, gy = fbonus.getXY()
					bscore = FruitScore()
					bscore.setXY(gx, gy)
					bscore.setScore(currentLevel)
					score += bscore.getScoreValue()
					bonusscore.add(bscore)

				# avec les pacgums
				collisionlist = pygame.sprite.spritecollide(pacman,allgums,True, collide_same16block)
				for gum in collisionlist:
					score += 10
					nbgums += 1
					if(isinghostmode):
						gum.playSound2()
					else:
						gum.playSound1()


				# avec les grosses pacgums
				collisionlist = pygame.sprite.spritecollide(pacman,allbiggums,True, collide_same16block)
				for gum in collisionlist:
					gum.playSound()
					score += 50
					nbgums += 1
					for ghost in ghostgroup:
						if(ghost.getMode()!=Ghost.MODEEYE): # on le bascule en fantome apeuré sauf si il est deja mort
							ghost.ghostMode()
					for ghost in lockedghostgroup:
						if(ghost.getMode()!=Ghost.MODEEYE): # on le bascule en fantome apeuré sauf si il est deja mort
							ghost.ghostMode()

				# avec les fantomes
				collisionlist = pygame.sprite.spritecollide(pacman,ghostgroup,False, collide_same16block)
				for ghost in collisionlist:
					if(ghost.getMode()==Ghost.MODEGHOST or ghost.getMode()==Ghost.MODEBLINKINGGHOST):
						# le fantome est en mode GHOST, pacman le mange
						ghost.eyeMode()
						nbghosteaten += 1
						# on affiche le bonus
						gx, gy = ghost.getXY()
						bscore = Score()
						bscore.setXY(gx, gy)
						bscore.setScore(nbghosteaten-1)
						score += bscore.getScoreValue()
						bonusscore.add(bscore)

					elif(ghost.getMode()==Ghost.MODESTANDARD and not INVINCIBLE):
						# le fantome est en mode STANDARD, pacman est mort...
						pacman.die()
						for g in ghostgroup:
							g.stop()

				# on met a jour le score et les vies
				scoreoverlay.setText(str(score).zfill(6))
				textgroup.update(currenttime)
				lifegroup.update(currenttime)
				bonusscore.update(currenttime)

				# on efface l'ecran
				pacmangroup.clear(buffer, background)
				allgums.clear(buffer, background)
				allbiggums.clear(buffer, background)
				ghostgroup.clear(buffer, background)
				lockedghostgroup.clear(buffer, background)
				textgroup.clear(buffer, background)
				lifegroup.clear(buffer, background)
				bonusscore.clear(buffer, background)
				fruitbonusgroup.clear(buffer, background)

				# on affiche les sprites
				textgroup.draw(buffer)
				lifegroup.draw(buffer)
				allgums.draw(buffer)
				allbiggums.draw(buffer)
				ghostgroup.draw(buffer)
				lockedghostgroup.draw(buffer)
				fruitbonusgroup.draw(buffer)
				pacmangroup.draw(buffer)
				bonusscore.draw(buffer)

				# on centre l'image a l'ecran
				xoffset = (WIDTH-playfield.width)/2
				yoffset = (HEIGHT-playfield.height)/2
				screen.blit(buffer, (xoffset, yoffset))

				# et on met à jour l'affichage ecran
				#pygame.display.flip()
				shader.render()

				if(len(pacmangroup)==0):
					# perdu
					winstatus = False
				if(len(allgums)==0 and len(allbiggums)==0):
					winstatus = True

				if(intromusic==False):
					intromusic = True
					pygame.mixer.music.load('sounds/game_start.wav')
					pygame.mixer.music.play()
					while pygame.mixer.music.get_busy():
						pygame.event.poll() # on purge les evenements durant la musique d'intro
						clock.tick(10) # on attend un peu
					bonusscore.remove (ready)
					pygame.mixer.music.load('sounds/siren_1.wav') # on lance le bruit de fond du jeu en mode standard...
					pygame.mixer.music.play(loops=-1)

				# Gestion de la sirene en fonction de l'état courant du jeu
				res = False
				for g in ghostgroup:
					if(g.getMode()==Ghost.MODEGHOST or g.getMode()==Ghost.MODEBLINKINGGHOST):
						res = True # mode Ghost si au moins un des fantomes est Ghost
						break
				if(res!=isinghostmode): # changement de mode
					isinghostmode = res
					if(isinghostmode):
						pygame.mixer.music.load('sounds/siren_3.wav') # on lance le bruit de fond du jeu en mode ghost...
						pygame.mixer.music.play(loops=-1)
					else:
						pygame.mixer.music.load('sounds/siren_1.wav') # on lance le bruit de fond du jeu en mode standard...
						pygame.mixer.music.play(loops=-1)
						nbghosteaten = 0


			if(winstatus==True):
				currentLevel += 1 # on passe au niveau suivant
				pygame.mixer.music.stop()
				pygame.mixer.music.load('sounds/intermission.wav') # on lance la musique de fin
				pygame.mixer.music.play()
				while pygame.mixer.music.get_busy(): # on attend la fin du bruitage
					clock.tick(10) # on attend un peu
			if(winstatus==False):
				currentnblife -= 1 # on perd une vie
				time.sleep(2)
				pygame.mixer.music.stop()
			if(currentnblife==0 or winstatus==True):
				break # on sort de la boucle infinie si on a perdu toutes les vies ou que l'on a terminé le niveau
		if(currentnblife==0):
			break # on sort de la boucle infinie si on a perdu toutes les vies
