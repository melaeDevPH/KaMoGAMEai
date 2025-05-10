import cv2
import mediapipe as mp
import pygame
import sys
import random

# Initialize MediaPipe and Pygame
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Gesture Game")

cap = cv2.VideoCapture(0)
clock = pygame.time.Clock()

# Player setup
player_radius = 30
player_pos = [WIDTH // 2, HEIGHT // 2]

# Enemy setup
enemy_radius = 25
enemy_pos = [WIDTH + 100, random.randint(50, HEIGHT - 50)]
enemy_speed = 5

font = pygame.font.SysFont(None, 48)
game_over = False

# Game loop
running = True
while running:
    screen.fill((30, 30, 30))

    # Handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # Webcam capture
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        # Hand tracking
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_tip.x * WIDTH)
            y = int(index_tip.y * HEIGHT)
            player_pos = [x, y]

        # Move enemy
        enemy_pos[0] -= enemy_speed
        if enemy_pos[0] < -enemy_radius:
            enemy_pos[0] = WIDTH + 100
            enemy_pos[1] = random.randint(50, HEIGHT - 50)

        # Collision detection
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < (player_radius + enemy_radius):
            game_over = True

        # Draw elements
        pygame.draw.circle(screen, (0, 255, 0), player_pos, player_radius)
        pygame.draw.circle(screen, (255, 0, 0), enemy_pos, enemy_radius)
    else:
        text = font.render("Game Over", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
sys.exit()
