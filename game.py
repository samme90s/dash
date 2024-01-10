import sys

import pygame

from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('python')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'player': load_image('entities/player.png')
        }
        directories = ['decor',
                       'grass',
                       'large_decor',
                       'stone']
        for directory in directories:
            self.assets[directory] = load_images('tiles/' + directory)

        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.scroll = [0, 0]

    def run(self):
        while True:
            self.clear()
            self.handle_tilemap()
            self.handle_player()
            self.handle_events()

            self.screen.blit(pygame.transform.scale(
                self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

    def clear(self):
        self.display.fill((14, 219, 248))

    def handle_tilemap(self):
        self.tilemap.render(self.display, offset=self.scroll)

    def handle_player(self):
        self.player.update(self.tilemap,
                           (self.movement[1] - self.movement[0], 0))
        self.player.render(self.display, offset=self.scroll)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Keys should be arrow keys instead and preferably x and z for
            # other actions. This is more universal for different keyboard
            # layouts, but for my sake I'll use WASD.
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self.movement[0] = True
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.movement[1] = True
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    self.player.velocity[1] = -3
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self.movement[0] = False
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.movement[1] = False


Game().run()
