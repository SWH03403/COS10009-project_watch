import pygame
from pygame import Surface
from pygame.time import Clock

def main() -> None:
	pygame.init()
	screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
	pygame.display.set_caption("Game")
	pygame.mouse.set_visible(True)
	clock = Clock()

	background = Surface(screen.get_size())
	background = background.convert()
	background.fill((0, 0, 0))

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: break

		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]: break
		elif keys[pygame.K_q]: break

		screen.blit(background, (0, 0))
		pygame.display.flip()
		clock.tick(60)

	pygame.quit()

if __name__ == "__main__":
	main()
