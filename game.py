import sys

import pygame


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('python')
        self.screen = pygame.display.set_mode((640, 480))

        self.clock = pygame.time.Clock()

        self.img = pygame.image.load('data/images/clouds/cloud_1.png')
        # The black background will be rendered as transparent,
        # i.e. one specfic color should be rendered transparent.
        self.img.set_colorkey((0, 0, 0))

        self.img_pos = [160, 260]
        self.movement = [False, False]

        self.collision_area = pygame.Rect(50, 50, 300, 50)

    def run(self):
        while True:
            # Clear screen
            self.screen.fill((14, 219, 248))

            # Shortcut can be used here called splat operator, which spreads
            # out the arguments:
            # pygame.Rect(*self.img_pos, *self.img.get_size())
            img_r = pygame.Rect(self.img_pos[0],
                                self.img_pos[1],
                                self.img.get_width(),
                                self.img.get_height())
            if img_r.colliderect(self.collision_area):
                pygame.draw.rect(self.screen,
                                 (0, 100, 255),
                                 self.collision_area)
            else:
                pygame.draw.rect(self.screen,
                                 (0, 50, 255),
                                 self.collision_area)

            self.img_pos[1] += (self.movement[1] - self.movement[0]) * 5
            self.screen.blit(self.img, self.img_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Keys should be arrow keys instead and preferably x and z for
                # other actions. This is more universal for different keyboard
                # layouts, but for my sake I'll use WASD. I could add both...
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.movement[0] = True
                    if event.key == pygame.K_s:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.movement[0] = False
                    if event.key == pygame.K_s:
                        self.movement[1] = False

            pygame.display.update()
            self.clock.tick(60)


Game().run()
