from numpy._core.defchararray import center
import pygame
import random
import math
import collision_scary_dontlook as collisionZ
from typing import Tuple
from moviepy.editor import VideoFileClip


def play_video(screen, clock, clip):
    for frame in clip.iter_frames(fps=30, dtype="uint8"):
        # Convert frame to surface
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        resized_frame = pygame.transform.scale(
            frame_surface, (screen.get_width(), screen.get_height()))
        # screen.blit(pygame.transform.scale(frame_surface,
        #           (800, 600)), (0, 0))  # Scale to screen
        screen.blit(resized_frame, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        clock.tick(30)  # 30 FPS limit


def resize_image(image, size=50):
    new_width = size
    new_height = int(image.get_height() * (new_width / image.get_width()))

    return pygame.transform.smoothscale(image, (new_width, new_height))


class Water:

    def __init__(self, screen, png_path: str) -> None:
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        png_raw = pygame.image.load(png_path).convert_alpha()
        self.png = pygame.transform.smoothscale(
            png_raw, (self.screen_width, 200))

        self.png_rect = self.png.get_rect()
        self.png_rect.center = (screen.get_width() / 2,
                                screen.get_height() - (200 // 2))

    def draw(self):
        self.screen.blit(self.png, self.png_rect)


class Player_params:
    png_path = "сушенная_вобла.png"
    speed = 100
    size = 50


class Player:

    def __init__(self, screen, player_params: Player_params) -> None:
        self.height = screen.get_height() / 5
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.size = player_params.size
        self.speed = player_params.speed
        self.load_png(player_params.png_path)

    def load_png(self, png_path: str) -> None:
        png_raw = pygame.image.load(png_path).convert_alpha()
        self.png = resize_image(png_raw, self.size)
        self.png_rect = self.png.get_rect()
        self.png_rect.center = (self.screen.get_width() / 2,
                                self.screen.get_height() / 4)

        self.rotated_90_deg = pygame.transform.rotate(self.png, 90)
        self.player_height = self.rotated_90_deg.get_height()
        self.player_width = self.rotated_90_deg.get_width()

        self.angle = 225
        self.png_left = pygame.transform.rotate(self.png, self.angle)
        self.angle = 315
        self.png_right = pygame.transform.rotate(self.png, self.angle)
        self.png = self.png_right

        self.png_turned_rect = self.png.get_rect(center=self.png_rect.center)

    def get_pos(self) -> Tuple[int, int]:
        return self.png_rect.center

    def get_png_rect(self) -> pygame.Rect:
        return self.png_rect

    def get_size(self) -> int:
        return self.size

    def fly(self, dt: int) -> Tuple[int, int]:

        if (self.angle == 225):
            self.png_rect.x -= self.speed * dt
            self.png_turned_rect.x -= self.speed * dt
        elif (self.angle == 315):
            self.png_rect.x += self.speed * dt
            self.png_turned_rect.x += self.speed * dt
        else:
            print("invalid angle!")

        if self.png_rect.left < 0:
            self.png_rect.left = 0
            self.png_turned_rect.left = 0
        elif self.png_rect.right > self.screen_width:
            self.png_rect.right = self.screen_width
            self.png_turned_rect.right = self.screen_width
        if self.png_rect.top < 0:
            self.png_rect.top = 0
        elif self.png_rect.bottom > self.screen_height:
            self.png_rect.bottom = self.screen_height
            self.png_turned_rect.bottom = self.screen_height
        return self.png_rect.center

    def swap_swap(self):
        if self.angle == 225:
            self.png = self.png_right
            self.angle = 315
            return

        if self.angle == 315:
            self.png = self.png_left
            self.angle = 225
            return

    def draw(self):
        self.screen.blit(self.png, self.png_turned_rect)


class Trail:

    class Trailik:
        rect = pygame.Rect(0, 0, 0, 0)
        pos = pygame.Vector2(0, 0)

    def __init__(self, screen, png_path: str, player: Player, size: int, length: int) -> None:
        self.screen = screen
        self.player = player
        self.image = pygame.image.load(png_path).convert_alpha()
        self.image = resize_image(self.image, size)
        self.length = length
        self.parts = []

    def spawn_part(self):
        if len(self.parts) > self.length - 1:
            self.parts.pop(0)
        part = self.Trailik()
        part.rect = self.image.get_rect(
            center=self.player.png_rect.center).copy()
        pos_x = self.player.png_rect.centerx
        pos_y = self.player.png_rect.centery
        part.pos = pygame.Vector2(pos_x, pos_y)
        self.parts.append(part)

    def move(self, dt):
        for i in range(len(self.parts)):
            self.parts[i].pos.y -= self.player.speed * dt

    def draw(self):
        for part in self.parts:
            part.rect.center = (int(part.pos.x), int(part.pos.y))
            self.screen.blit(self.image, part.rect)


class Notification:

    def __init__(self, screen, font: str, size: int, color: str, pos: pygame.Vector2) -> None:
        self.font = pygame.font.SysFont(font, size)
        self.score = 0
        self.pos = pos
        self.pos.x = screen.get_width() - 80
        self.color = color
        self.screen = screen
        self.alpha = 0
        self.fade_speed = 3
        self.padding = 10

        self.text_surface = self.font.render(
            "Hello, this message will fade!", True, self.color)
        self.text_rect = self.text_surface.get_rect(center=(pos.x, pos.y))

    def make_notif(self, notif_text: str):
        self.alpha = 255
        self.text_surface = self.font.render(notif_text, True, self.color)
        width = self.text_surface.get_width()
        self.pos.x = self.screen.get_width() - width - self.padding
        self.pos.y = self.padding

    def draw(self):
        if self.alpha > 0:
            fading_text = self.text_surface.copy()
            fading_text.set_alpha(self.alpha)
            self.screen.blit(fading_text, self.pos)
            self.alpha -= self.fade_speed


class Speedometer:

    def __init__(self, screen, font: str, size: int, color: str, pos: pygame.Vector2) -> None:
        self.font = pygame.font.SysFont(font, size)
        self.score = 0
        self.pos = pos
        self.color = color
        self.screen = screen

    def draw(self, player_speed: int):
        text_string = "Speed: " + str(player_speed)
        text = self.font.render(text_string, True, self.color)
        self.screen.blit(text, self.pos)


class Score:

    def __init__(self, screen, font: str, size: int, color: str, pos: pygame.Vector2) -> None:
        self.font = pygame.font.SysFont(font, size)
        self.score = 0
        self.pos = pos
        self.color = color
        self.screen = screen

    def add(self, points):
        self.score += points

    def draw(self):
        text_string = "Score: " + str(self.score)
        text = self.font.render(text_string, True, self.color)
        text_rect = text.get_rect()
        self.screen.blit(text, text_rect)


class Coin:

    def __init__(self, screen, image, pos: pygame.Vector2) -> None:
        self.height = screen.get_height() / 5
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.pos = pos
        self.png = image
        self.png_rect = self.png.get_rect()
        self.png_rect.center = (int(pos.x), int(pos.y))
        self.visibility = True

    def new_pos(self, pos: pygame.Vector2) -> None:
        self.pos.y = pos.y
        self.pos.x = pos.x

    def move(self, speed: int) -> None:
        self.pos.y -= speed

    def draw(self) -> None:
        self.png_rect.center = (int(self.pos.x), int(self.pos.y))
        if self.visibility:
            self.screen.blit(self.png, self.png_rect)

    def spawn_coin(self) -> None:
        self.visibility = True

    def despawn_coin(self) -> None:
        self.visibility = False

    def collide(self, player: Player) -> int:
        if not self.visibility:
            return 0

        rotated_player_corners = collisionZ.get_rotated_corners(
            player.png_rect, player.angle)
        collision = collisionZ.check_collision(
            rotated_player_corners, self.png_rect)
        if collision:
            return 5
        return 0


class Obstacle_params:
    width = 2
    color = "blue"
    gap_size = 2


class Obstacle:

    def __init__(self, screen, params: Obstacle_params, player_speed: int, y_pos: int) -> None:
        self.y_pos = y_pos
        self.color = params.color
        self.width = params.width
        self.gap_width = params.gap_size
        self.obstacle_speed = player_speed
        self.screen = screen
        self.screen_height = screen.get_height()
        self.screen_width = screen.get_width()
        self.generate_heights()

    def get_color(self) -> str:
        return self.color

    def get_y_pos(self) -> int:
        return self.y_pos

    def generate_heights(self):
        self.left_width = random.randint(
            50, self.screen_width - self.gap_width - 50)
        self.right_width = self.screen_width - self.left_width - self.gap_width

    def move(self, speed: int):
        self.y_pos -= speed

    def draw(self):
        self.left_rect = pygame.Rect(
            0, self.y_pos, self.left_width, self.width)
        right_x_pos = self.screen_width - self.right_width
        self.right_rect = pygame.Rect(
            right_x_pos, self.y_pos, self.right_width, self.width)
        pygame.draw.rect(self.screen, self.color, self.left_rect)
        pygame.draw.rect(self.screen, self.color, self.right_rect)

    def collide(self, player: Player):
        # here1
        correct_rect = player.png_rect.copy()
        correct_rect.center
        if player.angle == 225:
            rotated_player_corners = collisionZ.get_rotated_corners(
                correct_rect, 260)
        else:
            rotated_player_corners = collisionZ.get_rotated_corners(
                correct_rect, player.angle)

        collision_left = collisionZ.check_collision(
            rotated_player_corners, self.left_rect)
        collision_right = collisionZ.check_collision(
            rotated_player_corners, self.right_rect)
        return collision_left or collision_right


class Obstacles:

    def __init__(self, screen, player: Player, coin_png_path: str, obstacle_params: Obstacle_params, player_speed: int) -> None:
        self.screen = screen
        self.screen_height = screen.get_height()
        self.screen_width = screen.get_width()
        self.coin_png_path = coin_png_path
        self.player = player
        self.player_height = player.player_height
        self.player_width = player.player_width
        self.player_speed = player_speed
        self.obs_params = obstacle_params
        self.step = self.obs_params.width + \
            (self.player_height * 3)
        self.create_obstacles()
        self.create_coins()

    def create_obstacles(self) -> None:
        self.obstacles_list = []
        start_pos = self.screen_height

        for y_pos in range(start_pos, self.screen_height * 2, self.step):
            obstacle = Obstacle(self.screen, self.obs_params,
                                self.player_speed,  y_pos)
            self.obstacles_list.append(obstacle)

    def load_coin_image(self):
        png_raw = pygame.image.load(self.coin_png_path).convert_alpha()
        self.coin_png = resize_image(png_raw, self.obs_params.gap_size // 4)

    def create_coins(self):
        self.load_coin_image()

        self.coins_list = []
        for obstacle in self.obstacles_list:
            x = obstacle.left_width + (obstacle.gap_width // 2)
            y = obstacle.y_pos + (obstacle.width // 2)
            coin_pos = pygame.Vector2(x, y)
            coin = Coin(self.screen, self.coin_png, coin_pos)
            self.coins_list.append(coin)

    def move(self, dt: int) -> None:
        def move_first_to_end(arr):
            if not arr:
                return arr
            return arr[1:] + [arr[0]]

        speed = self.player_speed * dt

        for obstacle in self.obstacles_list:
            obstacle.move(speed)

        for coin in self.coins_list:
            coin.move(speed)

        width = self.obs_params.width
        if self.obstacles_list[0].y_pos + width < 0:
            self.obstacles_list[0].y_pos = self.obstacles_list[-1].y_pos + \
                self.step
            self.obstacles_list[0].generate_heights()

            x = self.obstacles_list[0].left_width + \
                (self.obstacles_list[0].gap_width // 2)
            y = self.obstacles_list[0].y_pos + \
                (self.obstacles_list[0].width // 2)
            coin_pos = pygame.Vector2(x, y)
            self.coins_list[0].new_pos(coin_pos)
            self.coins_list[0].spawn_coin()

            self.coins_list = move_first_to_end(self.coins_list)
            self.obstacles_list = move_first_to_end(self.obstacles_list)

    def draw(self) -> None:
        for obstacle in self.obstacles_list:
            obstacle.draw()

        for coin in self.coins_list:
            coin.draw()

    def coins_collide(self) -> int:
        score = 0
        for coin in self.coins_list:
            score = coin.collide(self.player)
            if score != 0:
                coin.despawn_coin()
                return score
        return score

    def collide(self) -> bool:

        for obstacle in self.obstacles_list:
            if obstacle.collide(self.player):
                return True
        return False
