import __future__
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

CELL_SIZE = 25
NUMBER_OF_CELLS = 30
OFFSET = 75
SNAKE_SEGMENT_TEXT_OFFSET = 1

# Define the target phrase
TARGET_PHRASE = "happy_new_year"


class Food:
    def __init__(self, position: Vector2, text: str):
        self.position = position
        self.text = text

    def draw(self):
        food_rect = pygame.Rect(OFFSET + self.position.x * CELL_SIZE,
                                OFFSET + self.position.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, DARK_GREEN, food_rect)
        text_surface = SCORE_FONT.render(self.text, True, GREEN)
        screen.blit(text_surface, (food_rect.x + SNAKE_SEGMENT_TEXT_OFFSET,
                    food_rect.y + SNAKE_SEGMENT_TEXT_OFFSET))


class SnakeSegment:
    def __init__(self, position: Vector2, text: str):
        self.position = position  # Vector2型の位置
        self.text = text  # 各セグメントの文字

    def __repr__(self):
        return f"Segment(position={self.position}, text='{self.text}')"


PLAYER_DEFAULT_SEGMENTS = [
    SnakeSegment(Vector2(5, 5), 'S'),
    SnakeSegment(Vector2(4, 5), 'N'),
    SnakeSegment(Vector2(3, 5), 'A'),
    SnakeSegment(Vector2(2, 5), 'K'),
    SnakeSegment(Vector2(1, 5), 'E'),
]


class Snake:
    def __init__(self, direction=Vector2(1, 0), segments=PLAYER_DEFAULT_SEGMENTS):
        self.direction: Vector2 = direction
        self.segments: List[SnakeSegment] = segments

    def draw(self):
        for segment in self.segments:
            segment_rect = pygame.Rect(OFFSET + segment.position.x * CELL_SIZE,
                                       OFFSET + segment.position.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, DARK_GREEN, segment_rect, 0, 7)
            text_surface = SCORE_FONT.render(segment.text, True, GREEN)
            screen.blit(text_surface, (segment_rect.x + SNAKE_SEGMENT_TEXT_OFFSET,
                        segment_rect.y + SNAKE_SEGMENT_TEXT_OFFSET))

    def update(self):
        # head_segment = self.segments[0]
        # new_head_position = head_segment.position + self.direction
        # new_head_segment = SnakeSegment(
        #    new_head_position, head_segment.text)
        # self.segments.insert(0, new_head_segment)
        # self.segments.pop()
        self.segments = [
            SnakeSegment(
                position=self.segments[i - 1].position
                if i > 0
                else self.segments[i].position+self.direction,
                text=self.segments[i].text
            )
            for i
            in range(len(self.segments))
        ]

    def add_segment(self, new_text):
        last_segment = self.segments[-1]
        new_segment = SnakeSegment(last_segment.position, new_text)
        self.segments.append(new_segment)


class Game:
    def __init__(self):
        self.snake = Snake()
        self.available_food = ["snake_case",
                               "hello_world", "new_year", "good_morning"]
        self.food = Food(
            position=self.generate_random_available_pos(),
            text=random.choice(self.available_food))
        self.state = "RUNNING"
        self.score = 0
        self.target_phrase = TARGET_PHRASE

    def draw(self):
        self.food.draw()
        self.snake.draw()

    def update(self):
        if self.state == "RUNNING":
            self.snake.update()
            self.check_collision_with_food()
            self.check_collision_with_edges()
            # self.check_collision_with_tail()

    def check_collision_with_food(self):
        if self.snake.segments[0].position == self.food.position:
            self.snake.add_segment(self.food.text)
            self.food = Food(
                position=self.generate_random_available_pos(),
                text=random.choice(self.available_food))
            self.score += 1

    def check_collision_with_edges(self):
        if self.snake.segments[0].position.x >= NUMBER_OF_CELLS:
            self.snake.segments[0].position.x = 0
        elif self.snake.segments[0].position.x < 0:
            self.snake.segments[0].position.x = NUMBER_OF_CELLS - 1
        if self.snake.segments[0].position.y >= NUMBER_OF_CELLS:
            self.snake.segments[0].position.y = 0
        elif self.snake.segments[0].position.y < 0:
            self.snake.segments[0].position.y = NUMBER_OF_CELLS - 1

    def game_over(self):
        self.snake = Snake()  # Snakeをリセット
        self.food.position = self.generate_random_available_pos()
        self.state = "STOPPED"
        self.score = 0

    def check_collision_with_tail(self):
        headless_body = self.snake.segments[1:]
        if self.snake.segments[0].position in [s.position for s in headless_body]:
            self.game_over()

    def generate_random_cell(self):
        x = random.randint(0, NUMBER_OF_CELLS - 1)
        y = random.randint(0, NUMBER_OF_CELLS - 1)
        return Vector2(x, y)

    def generate_random_available_pos(self):
        # attempts = 0
        position = self.generate_random_cell()
        # while position in [s.position for s in self.snake.segments] and attempts < 100:
        while position in [s.position for s in self.snake.segments]:
            position = self.generate_random_cell()
            # attempts += 1
        # return position if attempts < 100 else self.generate_random_cell()  # 最大試行回数を超えた場合は再生成
        return position


screen = pygame.display.set_mode(
    (2 * OFFSET + CELL_SIZE * NUMBER_OF_CELLS, 2 * OFFSET + CELL_SIZE * NUMBER_OF_CELLS))

pygame.display.set_caption("Snake Game: Happy New Year!")

clock = pygame.time.Clock()

game = Game()

SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200)

while True:
    for event in pygame.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game.state == "STOPPED":
                game.state = "RUNNING"
            if event.key == pygame.K_UP and game.snake.direction != Vector2(0, 1):
                game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and game.snake.direction != Vector2(0, -1):
                game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT and game.snake.direction != Vector2(1, 0):
                game.snake.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1, 0):
                game.snake.direction = Vector2(1, 0)

    # Drawing
    screen.fill(GREEN)
    pygame.draw.rect(screen, GREEN,
                     (OFFSET - 5, OFFSET - 5, CELL_SIZE * NUMBER_OF_CELLS + 10, CELL_SIZE * NUMBER_OF_CELLS + 10), 5)
    game.draw()
    title_surface = TITLE_FONT.render("Happy New Year Snake", True, DARK_GREEN)
    score_surface = SCORE_FONT.render(f"Score: {game.score}", True, DARK_GREEN)
    screen.blit(title_surface, (OFFSET - 5, 20))
    screen.blit(score_surface, (OFFSET - 5, OFFSET +
                CELL_SIZE * NUMBER_OF_CELLS + 10))

    pygame.display.update()
    clock.tick(60)
