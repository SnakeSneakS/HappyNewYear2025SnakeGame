import webbrowser
import pygame
import sys
import random
from pygame.math import Vector2
from typing import *

pygame.init()

# Define constants
TITLE_FONT = pygame.font.Font(None, 60)
SCORE_FONT = pygame.font.Font(None, 40)

GREEN = (173, 204, 96)
DARK_GREEN = (43, 51, 24)
DARK_BLUE = (70, 130, 180)
DARK_RED = (204, 51, 51)

CELL_SIZE = 30
NUMBER_OF_CELLS = 30
OFFSET = 75
SNAKE_SEGMENT_TEXT_OFFSET = 0
AUTO_MOVE_INTERVAL_SEC = 4

# Define the target phrase
TARGET_PHRASE = "happy_new_year"


class SnakeSegment:
    def __init__(self, position: Vector2, text: str):
        self.position = position  # Vector2型の位置
        self.text = text  # 各セグメントの文字

    def __repr__(self):
        return f"Segment(position={self.position}, text='{self.text}')"


PLAYER_DEFAULT_SEGMENTS = [
    SnakeSegment(Vector2(5, 5), 'H'),
    SnakeSegment(Vector2(4, 5), 'A'),
    SnakeSegment(Vector2(3, 5), 'P'),
    SnakeSegment(Vector2(2, 5), 'P'),
    SnakeSegment(Vector2(1, 5), 'Y'),
]


class Snake:
    def __init__(self,
                 direction=Vector2(1, 0),
                 segments=PLAYER_DEFAULT_SEGMENTS,
                 auto=False,
                 rect_color: Tuple[int, int, int] = DARK_GREEN,
                 text_color: Tuple[int, int, int] = GREEN,
                 ):
        self.direction: Vector2 = direction
        self.segments: List[SnakeSegment] = segments
        self.auto = auto

        self.rect_color = rect_color
        self.text_color = text_color

    def draw(self):
        for segment in self.segments:
            segment_rect = pygame.Rect(OFFSET + segment.position.x * CELL_SIZE,
                                       OFFSET + segment.position.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, self.rect_color, segment_rect, 0, 7)
            text_surface = SCORE_FONT.render(
                segment.text, True, self.text_color)
            screen.blit(text_surface, (segment_rect.x + SNAKE_SEGMENT_TEXT_OFFSET,
                        segment_rect.y + SNAKE_SEGMENT_TEXT_OFFSET))

    def auto_direction(self):
        # ここに自動方向決定のロジックを追加する
        # 現在の方向を基にランダムに新しい方向を決める
        directions = [Vector2(1, 0), Vector2(-1, 0),
                      Vector2(0, 1), Vector2(0, -1)]
        self.direction = random.choice(directions)

    def update(self):
        if self.auto:
            # 自動で方向を決めるロジック
            self.auto_direction()

        new_segments = [
            SnakeSegment(
                position=self.segments[i - 1].position
                if i > 0
                else self.segments[i].position + self.direction,
                text=self.segments[i].text
            )
            for i in range(len(self.segments))
        ]
        self.segments = new_segments

    def add_segment(self, new_text: str):
        last_segment = self.segments[-1]
        new_segment = SnakeSegment(last_segment.position, new_text)
        self.segments.append(new_segment)

    def remove_segment(self, i: int):
        """指定されたインデックスのセグメントを削除し、残りのセグメントを一つずつ前に詰める"""
        if 0 <= i < len(self.segments):
            # 削除した後、インデックス i から後ろのセグメントを一つずつ前に詰める
            for j in range(i + 1, len(self.segments)):
                self.segments[j].position = self.segments[j - 1].position
            del self.segments[i]  # インデックス i のセグメントを削除

    def check_collision_with_another_snake(self, other_snake: "Snake"):
        if len(self.segments) == 0 or len(other_snake.segments) == 0:
            return
        for segment in other_snake.segments[1:] if len(other_snake.segments) > 1 else []:
            if self.segments[0].position == segment.position:
                self.game_over()
                return
        for segment in self.segments[1:] if len(self.segments) > 1 else []:
            if other_snake.segments[0].position == segment.position:
                for s in other_snake.segments:
                    self.add_segment(s.text)
                other_snake.segments = []
                return

    def game_over(self):
        global game
        game.game_over()


class Game:
    def __init__(self):
        self.__init__game__()

    def draw(self):
        self.snake.draw()  # 自分の蛇を描画
        for enemy in self.enemies:
            enemy.draw()  # 敵の蛇を描画

    def update(self):
        if self.state == "RUNNING":
            self.move()
            self.check_collision_with_edges()
            self.check_collision_with_snakes()
            self.time += 1  # プレイヤーの蛇が動くたびにスコアが増える

    def move(self):
        self.snake.update()  # 自分の蛇を動かす
        for enemy in self.enemies:
            enemy.update()  # 敵の蛇を動かす

    def check_collision_with_snakes(self):
        # 自分の蛇と敵の蛇同士の衝突チェック
        for enemy in self.enemies:
            if len(enemy.segments) > 0:
                self.snake.check_collision_with_another_snake(enemy)

    def check_collision_with_edges(self):
        for snake in [self.snake] + self.enemies:  # 自分の蛇と敵の蛇すべてをチェック
            if len(snake.segments) > 0:
                if snake.segments[0].position.x >= NUMBER_OF_CELLS:
                    snake.segments[0].position.x = 0
                elif snake.segments[0].position.x < 0:
                    snake.segments[0].position.x = NUMBER_OF_CELLS - 1
                if snake.segments[0].position.y >= NUMBER_OF_CELLS:
                    snake.segments[0].position.y = 0
                elif snake.segments[0].position.y < 0:
                    snake.segments[0].position.y = NUMBER_OF_CELLS - 1

    def game_over(self):
        self.__init__game__()
        self.state = "STOPPED"

    def __init__game__(self):
        self.snake = Snake(
            rect_color=DARK_BLUE,
        )  # 自分の蛇
        self.enemies = [  # 敵の蛇
            Snake(
                rect_color=DARK_RED,
                segments=[
                    SnakeSegment(Vector2(10, 10), '_'),
                    SnakeSegment(Vector2(9, 10), 'N'),
                    SnakeSegment(Vector2(8, 10), 'E'),
                    SnakeSegment(Vector2(7, 10), 'W'),
                    SnakeSegment(Vector2(6, 10), '_'),
                ]
            ),
            Snake(
                rect_color=DARK_RED,
                segments=[
                    SnakeSegment(Vector2(15, 15), 'Y'),
                    SnakeSegment(Vector2(14, 15), 'E'),
                    SnakeSegment(Vector2(13, 15), 'A'),
                ]
            ),
            Snake(
                rect_color=DARK_RED,
                segments=[
                    SnakeSegment(Vector2(20, 20), 'R'),
                    SnakeSegment(Vector2(19, 20), '_'),
                    SnakeSegment(Vector2(18, 20), '2'),
                    SnakeSegment(Vector2(17, 20), '0'),
                    SnakeSegment(Vector2(16, 20), '2'),
                    SnakeSegment(Vector2(15, 20), '5'),
                ]
            ),
            # Snake(
            #    rect_color=DARK_RED,
            #    segments=[
            #        SnakeSegment(Vector2(19, 7), '_'),
            #        SnakeSegment(Vector2(18, 7), 'よ'),
            #        SnakeSegment(Vector2(17, 7), 'い'),
            #    ]
            # ),
            # Snake(
            #    rect_color=DARK_RED,
            #    segments=[
            #        SnakeSegment(Vector2(19, 13), 'お'),
            #        SnakeSegment(Vector2(18, 13), 'と'),
            #        SnakeSegment(Vector2(17, 13), 'し'),
            #        SnakeSegment(Vector2(16, 13), 'を'),
            #        SnakeSegment(Vector2(15, 13), '。'),
            #    ]
            # ),
        ]
        self.state = "RUNNING"
        self.time = 0
        self.target_phrase = TARGET_PHRASE

    def check_finished(self) -> bool:
        for s in self.enemies:
            if len(s.segments) != 0:
                return False
        return True


screen = pygame.display.set_mode(
    (2 * OFFSET + CELL_SIZE * NUMBER_OF_CELLS, 2 * OFFSET + CELL_SIZE * NUMBER_OF_CELLS))

pygame.display.set_caption("Snake Game: Happy New Year!")

clock = pygame.time.Clock()

game = Game()

SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200)
tweet_button = None


# button
button_size = 50
left_bottom_x = OFFSET // 2  # 左下の基準X座標
left_bottom_y = OFFSET + CELL_SIZE * NUMBER_OF_CELLS - 3 * button_size  # 左下の基準Y座標
up_button = pygame.Rect(left_bottom_x + button_size,
                        left_bottom_y, button_size, button_size)
down_button = pygame.Rect(left_bottom_x + button_size,
                          left_bottom_y + 2 * button_size, button_size, button_size)
left_button = pygame.Rect(
    left_bottom_x, left_bottom_y + button_size, button_size, button_size)
right_button = pygame.Rect(left_bottom_x + 2 * button_size,
                           left_bottom_y + button_size, button_size, button_size)


# ボタン描画の関数


def draw_buttons():
    pygame.draw.rect(screen, (200, 200, 200), up_button)
    pygame.draw.rect(screen, (200, 200, 200), down_button)
    pygame.draw.rect(screen, (200, 200, 200), left_button)
    pygame.draw.rect(screen, (200, 200, 200), right_button)

    # ボタン上の文字
    up_text = SCORE_FONT.render("UP", True, (0, 0, 0))
    down_text = SCORE_FONT.render("DOWN", True, (0, 0, 0))
    left_text = SCORE_FONT.render("LEFT", True, (0, 0, 0))
    right_text = SCORE_FONT.render("RIGHT", True, (0, 0, 0))

    screen.blit(up_text, (up_button.x + 5, up_button.y + 5))
    screen.blit(down_text, (down_button.x + 5, down_button.y + 5))
    screen.blit(left_text, (left_button.x + 5, left_button.y + 5))
    screen.blit(right_text, (right_button.x + 5, right_button.y + 5))


while True:
    for event in pygame.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()

            # snake auto direction logic
            for e in game.enemies:
                if e.auto == True:
                    e.auto = False
                    continue
                if int(pygame.time.get_ticks()/1000) % int(random.random()*AUTO_MOVE_INTERVAL_SEC+AUTO_MOVE_INTERVAL_SEC) == 0:
                    e.auto = True
                    continue

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game.state == "STOPPED":
                game.state = "RUNNING"

            if event.key == pygame.K_UP:
                game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN:
                game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT:
                game.snake.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT:
                game.snake.direction = Vector2(1, 0)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game.state == "STOPPED":
                game.state = "RUNNING"

            # タッチ位置で方向ボタンの押下を判定
            if up_button.collidepoint(event.pos):
                game.snake.direction = Vector2(0, -1)
            elif down_button.collidepoint(event.pos):
                game.snake.direction = Vector2(0, 1)
            elif left_button.collidepoint(event.pos):
                game.snake.direction = Vector2(-1, 0)
            elif right_button.collidepoint(event.pos):
                game.snake.direction = Vector2(1, 0)

            # tweet button
            if tweet_button is not None and tweet_button.collidepoint(event.pos):
                webbrowser.open(
                    f"https://twitter.com/intent/tweet?text=%23%E3%81%82%E3%81%91%E3%81%8A%E3%82%81%E3%83%98%E3%83%93%E3%82%B2%E3%83%BC%E3%83%A02025%0ATime:%20{game.time}%0AResult:%20{''.join([s.text for s in game.snake.segments])}%0A%20https%3A%2F%2Fgithub.com%2FSnakeSneakS%2FHappyNewYear2025SnakeGame")

    # Drawing
    screen.fill(GREEN)
    pygame.draw.rect(screen, GREEN,
                     (OFFSET - 5, OFFSET - 5, CELL_SIZE * NUMBER_OF_CELLS + 10, CELL_SIZE * NUMBER_OF_CELLS + 10), 5)
    game.draw()
    title_surface = TITLE_FONT.render(
        "Happy New Year Snake Game", True, DARK_GREEN)
    score_surface = SCORE_FONT.render(f"Time: {game.time}", True, DARK_GREEN)
    screen.blit(title_surface, (OFFSET - 5, 20))
    screen.blit(score_surface, (OFFSET - 5, OFFSET +
                CELL_SIZE * NUMBER_OF_CELLS + 10))

    # 仮想ボタンを描画
    draw_buttons()

    if game.check_finished():
        tweet_button = pygame.Rect(
            CELL_SIZE*NUMBER_OF_CELLS, 10, 120, 60)
        pygame.draw.rect(screen, (0, 0, 255), tweet_button)
        text = TITLE_FONT.render("Tweet", True, (255, 255, 255))
        screen.blit(text, (tweet_button.x, tweet_button.y))

    pygame.display.update()
    clock.tick(60)
