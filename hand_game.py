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

# Fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# Game variables
player_radius = 30
player_pos = [WIDTH // 2, HEIGHT // 2]
enemy_radius = 25
enemy_pos = [WIDTH + 100, random.randint(50, HEIGHT - 50)]
speed_levels = {'Easy': 3, 'Medium': 6, 'Hard': 9}
level_selected = False
game_over = False
score = 0
selected_level = None

# Level selection
button_rects = {
    'Easy': pygame.Rect(WIDTH // 2 - 80, 160, 160, 40),
    'Medium': pygame.Rect(WIDTH // 2 - 80, 210, 160, 40),
    'Hard': pygame.Rect(WIDTH // 2 - 80, 260, 160, 40)
}

def draw_level_menu(selected=None):
    screen.fill((10, 10, 10))
    title = font.render("Select Difficulty", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    for level, rect in button_rects.items():
        color = (100, 255, 100) if level == 'Easy' else (255, 255, 100) if level == 'Medium' else (255, 100, 100)
        border_color = (255, 255, 255) if selected == level else (0, 0, 0)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, border_color, rect, 3)
        label = small_font.render(level, True, (0, 0, 0))
        screen.blit(label, (rect.x + rect.width // 2 - label.get_width() // 2, rect.y + 5))

    pygame.display.flip()

# Game loop
running = True
enemy_speed = 0
while running:
    if not level_selected:
        draw_level_menu(selected_level)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for level, rect in button_rects.items():
                    if rect.collidepoint(mouse_pos):
                        enemy_speed = speed_levels[level]
                        level_selected = True
                        selected_level = level
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                selected_level = None
                for level, rect in button_rects.items():
                    if rect.collidepoint(mouse_pos):
                        selected_level = level
        continue

    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

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
            score += 1  # increase score when enemy dodged

        # Collision detection
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < (player_radius + enemy_radius):
            game_over = True

        # Draw player and enemy
        pygame.draw.circle(screen, (0, 255, 0), player_pos, player_radius)
        pygame.draw.circle(screen, (255, 0, 0), enemy_pos, enemy_radius)

        # Display score
        score_text = small_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

    else:
        text = font.render("Game Over", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        restart_text = small_font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
        screen.blit(restart_text, (WIDTH // 2 - 160, HEIGHT // 2 + 40))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reset game state
            enemy_pos = [WIDTH + 100, random.randint(50, HEIGHT - 50)]
            score = 0
            game_over = False
        elif keys[pygame.K_q]:
            running = False

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
sys.exit()
