
import pygame
from game_data import levels


class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed):
        super().__init__()
        self.image = pygame.Surface((100, 80))
        if status == 'available':
            self.image.fill('red')
        else:
            self.image.fill('gray')
        self.rect = self.image.get_rect(center=pos)
        self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed / 2),
                                          self.rect.centery - (icon_speed / 2),
                                          icon_speed,
                                          icon_speed)


class Icon(pygame.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.pos = pos
        self.image = pygame.Surface((20, 20))
        self.image.fill('blue')
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos


class Overworld:
    def __init__(self, start_level, max_level, surface) -> None:

        # setup
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level

        # movement logic
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.moving = False

        # sprites
        self.setup_nodes()
        self.setup_icon()

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = Node(
                    node_data['node_pos'], 'available', self.speed)
                self.nodes.add(node_sprite)
            else:
                node_sprite = Node(node_data['node_pos'], 'locked', self.speed)
            self.nodes.add(node_sprite)

    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[
                           self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data('next')
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level > 0:
                self.move_direction = self.get_movement_data('previous')
                self.current_level -= 1
                self.moving = True

    def get_movement_data(self, target):
        start = pygame.math.Vector2(
            self.nodes.sprites()[self.current_level].rect.center)

        if target == 'next':
            end = pygame.math.Vector2(
                self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(
                self.nodes.sprites()[self.current_level - 1].rect.center)
        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def draw_paths(self):
        points = [node['node_pos']
                  for index, node in enumerate(levels.values()) if index <= self.max_level]
        pygame.draw.lines(surface=self.display_surface,
                          color='red', closed=False, points=points, width=6)

    def run(self):
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.nodes.draw(self.display_surface)
        self.draw_paths()
        self.icon.draw(self.display_surface)
