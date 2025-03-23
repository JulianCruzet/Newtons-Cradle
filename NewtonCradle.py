import pygame
import sys
import math
from pygame.locals import *

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Newton's Cradle Simulation")

# Colors
WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)
GRAY     = (200, 200, 200)
BLUE     = (50, 100, 200)
DARK_GRAY = (80, 80, 80)

# Simulation parameters (damping is fixed to 1.0 for perfect energy conservation)
class SimulationParams:
    def __init__(self):
        self.num_balls = 5
        self.ball_radius = 20
        self.ball_mass = 1.0      # adjustable via slider
        self.gravity = 50.0       # adjustable via slider
        self.rod_length = 200
        self.damping = 1.0        # Set to 1.0 to avoid any energy loss
        self.initial_angle = math.pi / 4  # initial angle (radians) for the rightmost ball
        self.time_step = 1/60     # fixed time step (60 FPS)

params = SimulationParams()

# Ball class: each ball is a pendulum attached to its pivot.
class Ball:
    def __init__(self, mass, initial_angle, pivot):
        self.mass = mass
        self.angle = initial_angle
        self.angular_velocity = 0
        self.angular_acceleration = 0
        self.pivot = pivot  # (x, y) position of the pivot

    def update(self, dt):
        # Pendulum dynamics (using a simple symplectic Euler integrator):
        self.angular_acceleration = -params.gravity * math.sin(self.angle) / params.rod_length
        self.angular_velocity += self.angular_acceleration * dt
        # Multiply by damping; here damping is 1.0 so energy is conserved.
        self.angular_velocity *= params.damping
        self.angle += self.angular_velocity * dt

    def get_position(self):
        # Compute ball center from its pivot and current angle.
        x = self.pivot[0] + params.rod_length * math.sin(self.angle)
        y = self.pivot[1] + params.rod_length * math.cos(self.angle)
        return (x, y)

# Initialize balls along a horizontal support.
# All balls start at equilibrium (angle = 0) except the rightmost, which is raised.
def initialize_simulation():
    balls = []
    origin_x = WIDTH // 2
    origin_y = 100  # y-coordinate of the support (pivots)
    spacing = 2 * params.ball_radius  # spacing so balls just touch at equilibrium
    start_x = origin_x - ((params.num_balls - 1) / 2) * spacing
    for i in range(params.num_balls):
        initial_angle = params.initial_angle if i == params.num_balls - 1 else 0
        pivot = (start_x + i * spacing, origin_y)
        balls.append(Ball(params.ball_mass, initial_angle, pivot))
    return balls

# Iterative collision resolution that swaps angular velocities.
# For equal masses, this is energy-conserving.
def resolve_collisions(balls):
    tolerance = 1.0  # extra pixels allowed for contact
    max_iter = 10    # maximum iterations per frame
    n = len(balls)
    for _ in range(max_iter):
        collision_found = False
        # Loop over adjacent pairs (from rightmost to leftmost).
        for i in range(n - 1, 0, -1):
            ball_right = balls[i]
            ball_left  = balls[i - 1]
            pos_right = ball_right.get_position()
            pos_left  = ball_left.get_position()
            dx = pos_right[0] - pos_left[0]
            if dx < 2 * params.ball_radius + tolerance:
                # Approximate horizontal velocity: v ~ L * ω  (assuming small angles so cos(angle) ~ 1)
                v_right = params.rod_length * ball_right.angular_velocity
                v_left  = params.rod_length * ball_left.angular_velocity
                # If the relative velocity is negative (right ball moving toward left ball), swap velocities.
                if (v_right - v_left) < 0:
                    ball_left.angular_velocity, ball_right.angular_velocity = ball_right.angular_velocity, ball_left.angular_velocity
                    collision_found = True
        if not collision_found:
            break

# Draw the support bar, rods, and balls.
def draw(screen, balls):
    screen.fill(WHITE)
    if balls:
        left_pivot = balls[0].pivot[0]
        right_pivot = balls[-1].pivot[0]
        origin_y = balls[0].pivot[1]
        support_rect = (left_pivot - 20, origin_y - 10, (right_pivot - left_pivot) + 40, 10)
        pygame.draw.rect(screen, DARK_GRAY, support_rect)
    for ball in balls:
        ball_pos = ball.get_position()
        pygame.draw.line(screen, GRAY, ball.pivot, ball_pos, 2)
        pygame.draw.circle(screen, BLUE, (int(ball_pos[0]), int(ball_pos[1])), params.ball_radius)
        pygame.draw.circle(screen, BLACK, (int(ball_pos[0]), int(ball_pos[1])), params.ball_radius, 1)

# UI Elements: Button and Slider classes.
class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 200)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 30, 255),
                            min(color[1] + 30, 255),
                            min(color[2] + 30, 255))
        self.active_color = color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=5)
        else:
            pygame.draw.rect(screen, self.active_color, self.rect, border_radius=5)
        font = pygame.font.SysFont(None, 24)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, step=1):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.step = step
        self.active = False
        self.handle_radius = 10

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=3)
        handle_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_y = self.rect.y + self.rect.height // 2
        pygame.draw.circle(screen, BLUE, (int(handle_x), int(handle_y)), self.handle_radius)
        font = pygame.font.SysFont(None, 20)
        label_surf = font.render(f"{self.label}: {self.value:.2f}", True, BLACK)
        label_rect = label_surf.get_rect(x=self.rect.x, y=self.rect.y - 25)
        screen.blit(label_surf, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
            handle_y = self.rect.y + self.rect.height // 2
            handle_rect = pygame.Rect(handle_x - self.handle_radius, handle_y - self.handle_radius,
                                      2 * self.handle_radius, 2 * self.handle_radius)
            if handle_rect.collidepoint(event.pos):
                self.active = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.active = False
        elif event.type == pygame.MOUSEMOTION and self.active:
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
            self.value = self.min_val + (self.max_val - self.min_val) * rel_x / self.rect.width
            if self.step != 0:
                self.value = round(self.value / self.step) * self.step
            self.value = max(self.min_val, min(self.max_val, self.value))
            return True
        return False

# Create UI elements.
start_button = Button(50, HEIGHT - 60, 100, 40, "Start/Pause", (50, 150, 50))
reset_button = Button(170, HEIGHT - 60, 100, 40, "Reset", (150, 50, 50))
sliders = [
    Slider(50, HEIGHT - 240, 300, 10, 2, 10, params.num_balls, "Number of Balls", 1),
    Slider(50, HEIGHT - 200, 300, 10, 10, 30, params.ball_radius, "Ball Radius", 1),
    Slider(400, HEIGHT - 240, 300, 10, 1, 100, params.gravity, "Gravity", 0.1),
    Slider(400, HEIGHT - 200, 300, 10, 100, 300, params.rod_length, "Rod Length", 1),
    Slider(50, HEIGHT - 160, 300, 10, 0.1, 10, params.ball_mass, "Ball Mass", 0.1),
    # Note: Damping slider is here, but for perfect energy conservation set it to 1.0.
    Slider(400, HEIGHT - 160, 300, 10, 0.9, 1, params.damping, "Damping", 0.001),
    Slider(400, HEIGHT - 120, 300, 10, 0, math.pi/2, params.initial_angle, "Initial Angle (rad)", 0.01)
]

# Main loop.
def main():
    clock = pygame.time.Clock()
    running = True
    simulation_running = False
    balls = initialize_simulation()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if start_button.is_clicked(event):
                simulation_running = not simulation_running
            if reset_button.is_clicked(event):
                params.num_balls    = int(sliders[0].value)
                params.ball_radius  = sliders[1].value
                params.gravity      = sliders[2].value
                params.rod_length   = sliders[3].value
                params.ball_mass    = sliders[4].value
                params.damping      = sliders[5].value  # For perfect conservation, set to 1.0.
                params.initial_angle = sliders[6].value
                balls = initialize_simulation()
                simulation_running = False
            for slider in sliders:
                slider.handle_event(event)
        
        if simulation_running:
            for ball in balls:
                ball.update(params.time_step)
            resolve_collisions(balls)
        
        draw(screen, balls)
        start_button.draw(screen)
        reset_button.draw(screen)
        for slider in sliders:
            slider.draw(screen)
        
        font = pygame.font.SysFont(None, 36)
        title_surf = font.render("Newton's Cradle Simulation", True, BLACK)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 40))
        screen.blit(title_surf, title_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
