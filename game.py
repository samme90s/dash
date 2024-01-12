import sys

import pygame

from scripts.clouds import Clouds
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
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'player': load_image('entities/player.png'),
            'stone': load_images('tiles/stone'),
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.scroll = [0, 0]
        self.render_scroll = [0, 0]

    def run(self):
        while True:
            # Order is important here!
            self.clear()
            self.handle_scroll()
            self.handle_clouds()
            self.handle_tilemap()
            self.handle_player()
            self.handle_events()

            self.screen.blit(pygame.transform.scale(
                self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

    def clear(self):
        self.display.blit(self.assets['background'], (0, 0))

    def handle_scroll(self):
        self.scroll[0] += (self.player.rect().centerx -
                           self.display.get_width() / 2 -
                           self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery -
                           self.display.get_height() / 2 -
                           self.scroll[1]) / 30
        self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

    def handle_clouds(self):
        self.clouds.update()
        self.clouds.render(self.display, offset=self.render_scroll)

    def handle_tilemap(self):
        self.tilemap.render(self.display, offset=self.render_scroll)

    def handle_player(self):
        self.player.update(self.tilemap,
                           (self.movement[1] - self.movement[0], 0))
        self.player.render(self.display, offset=self.render_scroll)

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
