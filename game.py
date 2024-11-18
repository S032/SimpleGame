from numpy import place
import pygame
from typing import Union
import game_objects as objs
from moviepy.editor import VideoFileClip

pygame.init()
screen = pygame.display.set_mode((500, 800), pygame.SRCALPHA)
screen_height = screen.get_height()
screen_width = screen.get_width()
clock = pygame.time.Clock()
running = True
dt = 0
clip = VideoFileClip("gameover.mp4")  # Видео, проигрывающ при смерти
video_finished = False


def speed_up(speed_after: int, new_speed_up_after: int, player: objs.Player, obstacles: objs.Obstacles) -> int:
    # На сколько увеличиться скорость при достаточном кол-во монет
    new_speed = player.speed // 4
    player.speed += new_speed
    obstacles.player_speed += new_speed
    speed_after += new_speed_up_after
    return speed_after


player_params = objs.Player_params()
# Scores
scores = objs.Score(screen, "Arial", 36, "white", pygame.Vector2(0, 0))
# Speedometer
speedometer = objs.Speedometer(
    screen, "Arial", 36, "white", pygame.Vector2(0, 36 + 5))
# Notify
notify = objs.Notification(screen, "Arial", 36, "green", pygame.Vector2(0, 0))
# Water
water = objs.Water(screen, "вода.png")

obstacles_params = objs.Obstacle_params()


# ВОТ ТУТА ОСНОВНЫЕ ПАРАМЕТРЫ -----------------------------------------------------------------------
# Player
player_params.png_path = "сушенная_вобла.png"  # Внешка игрока
player_params.speed = 100  # Скорость игрока
player_params.size = 70  # Размер игрока

# Other
SPEED_UP_AFTER = 35  # Если собрать столько монет то скорость игрока станет больше

# Obstacles and coins
obstacles_params.color = "blue"  # Цвет препятствий
obstacles_params.width = 10  # Ширина препятствий
obstacles_params.gap_size = 160  # Размер дырочки в препятствии

# ------------------------------------------------------------------------------------------------------


NEW_SPEED_AFTER = SPEED_UP_AFTER
player = objs.Player(screen, player_params)
# Trail
trail = objs.Trail(screen, "bubble.png", player, 20, 200)
obstacles = objs.Obstacles(
    screen, player, "coin.png", obstacles_params, player.speed)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            video_finished = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.swap_swap()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.swap_swap()

    screen.fill("purple")

    trail.draw()
    player.draw()
    obstacles.draw()
    scores.draw()
    speedometer.draw(player.speed)
    notify.draw()
    obstacles.move(dt)
    trail.move(dt)
    trail.spawn_part()
    water.draw()
    scores.add(obstacles.coins_collide())
    if obstacles.collide():
        running = False
    player.fly(dt)

    if scores.score == SPEED_UP_AFTER:
        notify.make_notif("скорость увеличена!")
        SPEED_UP_AFTER = speed_up(
            SPEED_UP_AFTER, NEW_SPEED_AFTER, player, obstacles)

    pygame.display.flip()
    dt = clock.tick(60) / 1000  # 60 FPS

if not video_finished:
    objs.play_video(screen, clock, clip)

alpha = 0
apearing_speed = 3
while not video_finished:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            video_finished = True

    screen.fill((0, 0, 0))

    font = pygame.font.SysFont("Arial", 45)
    pos = pygame.Vector2(screen_width // 2, screen_height // 2)

    text_surface = font.render(
        "GAME OVER", True, "red")
    text_rect = text_surface.get_rect(center=(pos.x, pos.y))

    fading_text = text_surface.copy()
    fading_text.set_alpha(alpha)
    screen.blit(fading_text, text_rect)
    alpha += apearing_speed

    scores.draw()
    speedometer.draw(player.speed)

    pygame.display.flip()
    clock.tick(60)  # 60 FPS limit

pygame.quit()
