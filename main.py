import pygame
from pygame.locals import *
import cv2
import mediapipe as mp
import random
import math

pygame.init()

# Game Constants
WIDTH = 900
HEIGHT = 600
fps = 30
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
red = (255, 0, 0)
yellow = (255, 255, 0)
pygame.display.set_caption('Flappy Space')
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 20)

# Flappy Bird variables
player_x = 255
player_y = 255
y_change = 0
jump_height = 4  # Decreased jump height
gravity = 0.5  # Decreased gravity
obstacles = [400, 700, 1000, 1300, 1600]
generate_places = True
y_positions = []
game_over = False
speed = 2
score = 0
high_score = 0
stars = []
waiting_for_space = True
firstClose = True

# Hand Detection variables
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Hand gesture status
perfect_close_count = 0
imperfect_close_count = 0
highest_perfect_close = 0  # Track highest perfect close count
tmp_imperfect = 0
gesture_improving = True

# Function to draw Flappy Bird player
def draw_player(x_pos, y_pos):
    global y_change
    mouth = pygame.draw.circle(screen, gray, (x_pos + 25, y_pos + 15), 12)
    play = pygame.draw.rect(screen, white, [player_x, player_y, 30, 30], 0, 12)
    eye = pygame.draw.circle(screen, black, (x_pos + 24, y_pos + 12), 5)
    jetpack = pygame.draw.rect(screen, white, [x_pos - 20, y_pos, 18, 28], 3, 2)
    if y_change < 0:
        flame1 = pygame.draw.rect(screen, red, [x_pos - 20, y_pos + 29, 7, 20], 0, 2)
        flame_yellow = pygame.draw.rect(screen, yellow, [x_pos - 18, y_pos + 30, 3, 18], 0, 2)
        flame2 = pygame.draw.rect(screen, red, [x_pos - 10, y_pos + 29, 7, 20], 0, 2)
        flame2_yellow = pygame.draw.rect(screen, yellow, [x_pos - 8, y_pos + 30, 3, 18], 0, 2)
    return play

# Function to draw obstacles
def draw_obstacles(obst, y_pos, play):
    global game_over
    for i in range(len(obst)):
        y_coord = y_pos[i]
        top_rect = pygame.draw.rect(screen, gray, [obst[i], 0, 30, y_coord], )
        top2 = pygame.draw.rect(screen, gray, [obst[i] - 3, y_coord - 20, 36, 20], 0, 5)
        bot_rect = pygame.draw.rect(screen, gray, [obst[i], y_coord + 200, 30, HEIGHT - (y_coord + 70)], )
        bot2 = pygame.draw.rect(screen, gray, [obst[i] - 3, y_coord + 200, 36, 20], 0, 5)
        if top_rect.colliderect(player) or bot_rect.colliderect(player):
            game_over = True

# Function to draw stars for background
def draw_stars(stars):
    global total
    for i in range(total - 1):
        pygame.draw.rect(screen, white, [stars[i][0], stars[i][1], 3, 3], 0, 2)
        stars[i][0] -= .5
        if stars[i][0] < -3:
            stars[i][0] = WIDTH + 3
            stars[i][1] = random.randint(0, HEIGHT)
    return stars

# Main game loop
running = True
cap = cv2.VideoCapture(0)  # Initialize video capture
while running:
    timer.tick(fps)
    screen.fill(black)

    # Generate stars and obstacles
    if generate_places:
        for i in range(len(obstacles)):
            y_positions.append(random.randint(0, 300))
        total = 100
        for i in range(total):
            x_pos = random.randint(0, WIDTH)
            y_pos = random.randint(0, HEIGHT)
            stars.append([x_pos, y_pos])
        generate_places = False

    # Draw stars and player
    stars = draw_stars(stars)
    player = draw_player(player_x, player_y)
    draw_obstacles(obstacles, y_positions, player)

    # Check if the player hits the window borders
    if player_y <= 0 or player_y >= HEIGHT - 30:
        game_over = True

    # Hand Gesture Recognition
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Process hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x, y = hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y
            x1, y1 = hand_landmarks.landmark[12].x, hand_landmarks.landmark[12].y

            distance = math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)

            if y1 > y:
                if firstClose:
                    waiting_for_space = False
                    firstClose = False
                elif not waiting_for_space and not game_over:
                    y_change = -jump_height
                if y1 > 0.4:
                    perfect_close_count += 1
                    # Update highest perfect close count
                    if perfect_close_count > highest_perfect_close:
                        highest_perfect_close = perfect_close_count
                elif not waiting_for_space and game_over:
                    # Reset game state
                    player_y = 255
                    player_x = 255
                    y_change = 0
                    generate_places = True
                    obstacles = [400, 700, 1000, 1300, 1600]
                    y_positions = []
                    score = 0
                    game_over = False
                    perfect_close_count = 0
                    imperfect_close_count = 0
            else:
                if y1 < 0.2:
                    imperfect_close_count += 1
                    perfect_close_count = 0

            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

    # Display hand detection results
    cv2.imshow('MediaPipe Hands', image)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw game elements and update game logic
    if waiting_for_space:
        start_text = font.render('Close your hand to Start', True, white)
        screen.blit(start_text, (300, 200))
    else:
        if player_y + y_change < HEIGHT - 30:
            player_y += y_change
            y_change += gravity
        else:
            player_y = HEIGHT - 30

        for i in range(len(obstacles)):
            if not game_over:
                obstacles[i] -= speed
                if obstacles[i] < -30:
                    obstacles.remove(obstacles[i])
                    y_positions.remove(y_positions[i])
                    obstacles.append(random.randint(obstacles[-1] + 280, obstacles[-1] + 320))
                    y_positions.append(random.randint(0, 300))
                    score += 1
        if score > high_score:
            high_score = score

        if game_over:
            game_over_text = font.render('Game Over!! Close Hand to Restart!', True, white)
            screen.blit(game_over_text, (200, 200))

        score_text = font.render('Score: ' + str(score), True, white)
        screen.blit(score_text, (10, 450))
        high_score_text = font.render('High Score: ' + str(high_score), True, white)
        screen.blit(high_score_text, (10, 470))

        perfect_close_text = font.render('Perfect Closes: ' + str(perfect_close_count), True, white)
        screen.blit(perfect_close_text, (10, 490))

        highest_perfect_close_text = font.render('Highest Perfect Closes: ' + str(highest_perfect_close), True, white)
        screen.blit(highest_perfect_close_text, (10, 510))

        if perfect_close_count == 0:
            comment_text = font.render('Keep practicing to improve!', True, white)
            gesture_improving = False
        else:
            comment_text = font.render('Great job! Keep it up!', True, white)
        screen.blit(comment_text, (10, 530))

        # Check for hand gesture to restart the game
        if game_over and perfect_close_count > 0:
            player_y = 255
            player_x = 255
            y_change = 0
            generate_places = True
            obstacles = [400, 700, 1000, 1300, 1600]
            y_positions = []
            score = 0
            game_over = False
            perfect_close_count = 0
            imperfect_close_count = 0

    pygame.display.flip()
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
pygame.quit()
