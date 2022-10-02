
def collide_same16block(pacman, element):
	'''
	Collider qui teste si l'element est sur la meme case que pacman
	'''
	if(	pacman.rect.centerx>>4 == element.rect.centerx>>4
		and
		pacman.rect.centery>>4 == element.rect.centery>>4
		):
		return True
	else:
		return False
