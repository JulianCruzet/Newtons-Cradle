import unittest
import math
import sys
from unittest.mock import Mock, patch, MagicMock
import pygame

# Import classes and functions from the main file
from NewtonCradle import (
    SimulationParams, Ball, Button, Slider,
    initialize_simulation, resolve_collisions
)


class TestSimulationParams(unittest.TestCase):
    """Test cases for the SimulationParams class"""

    def test_initialization(self):
        """Test that SimulationParams initializes with correct default values"""
        params = SimulationParams()
        self.assertEqual(params.num_balls, 5)
        self.assertEqual(params.ball_radius, 20)
        self.assertEqual(params.ball_mass, 1.0)
        self.assertEqual(params.gravity, 50.0)
        self.assertEqual(params.rod_length, 200)
        self.assertEqual(params.damping, 1.0)
        self.assertEqual(params.initial_angle, math.pi / 4)
        self.assertEqual(params.time_step, 1/60)

    def test_parameter_modification(self):
        """Test that parameters can be modified"""
        params = SimulationParams()
        params.num_balls = 7
        params.gravity = 100.0
        params.damping = 0.95

        self.assertEqual(params.num_balls, 7)
        self.assertEqual(params.gravity, 100.0)
        self.assertEqual(params.damping, 0.95)


class TestBall(unittest.TestCase):
    """Test cases for the Ball class (pendulum physics)"""

    def setUp(self):
        """Set up test fixtures"""
        self.params = SimulationParams()
        self.pivot = (400, 100)
        self.initial_angle = 0
        self.mass = 1.0

    def test_ball_initialization(self):
        """Test that a Ball initializes with correct properties"""
        ball = Ball(self.mass, self.initial_angle, self.pivot)

        self.assertEqual(ball.mass, self.mass)
        self.assertEqual(ball.angle, self.initial_angle)
        self.assertEqual(ball.angular_velocity, 0)
        self.assertEqual(ball.angular_acceleration, 0)
        self.assertEqual(ball.pivot, self.pivot)

    def test_get_position_at_equilibrium(self):
        """Test ball position at equilibrium (angle = 0)"""
        ball = Ball(self.mass, 0, self.pivot)
        pos = ball.get_position()

        # At angle 0, sin(0) = 0, cos(0) = 1
        # x = pivot_x + rod_length * sin(0) = pivot_x
        # y = pivot_y + rod_length * cos(0) = pivot_y + rod_length
        expected_x = self.pivot[0]
        expected_y = self.pivot[1] + self.params.rod_length

        self.assertAlmostEqual(pos[0], expected_x, places=5)
        self.assertAlmostEqual(pos[1], expected_y, places=5)

    def test_get_position_at_angle(self):
        """Test ball position at a specific angle"""
        angle = math.pi / 4  # 45 degrees
        ball = Ball(self.mass, angle, self.pivot)
        pos = ball.get_position()

        expected_x = self.pivot[0] + self.params.rod_length * math.sin(angle)
        expected_y = self.pivot[1] + self.params.rod_length * math.cos(angle)

        self.assertAlmostEqual(pos[0], expected_x, places=5)
        self.assertAlmostEqual(pos[1], expected_y, places=5)

    def test_update_changes_angle(self):
        """Test that update() changes the ball's angle when angular velocity is non-zero"""
        ball = Ball(self.mass, math.pi / 6, self.pivot)
        ball.angular_velocity = 0.1
        initial_angle = ball.angle

        ball.update(self.params.time_step)

        # Angle should have changed
        self.assertNotEqual(ball.angle, initial_angle)

    def test_pendulum_acceleration_at_angle(self):
        """Test that pendulum acceleration is correctly calculated"""
        angle = math.pi / 6
        ball = Ball(self.mass, angle, self.pivot)

        ball.update(self.params.time_step)

        # Expected acceleration: -g * sin(angle) / rod_length
        expected_accel = -self.params.gravity * math.sin(angle) / self.params.rod_length
        self.assertAlmostEqual(ball.angular_acceleration, expected_accel, places=5)

    def test_damping_effect(self):
        """Test that damping affects angular velocity"""
        ball = Ball(self.mass, math.pi / 6, self.pivot)
        ball.angular_velocity = 1.0

        # With damping = 1.0, velocity should be preserved
        ball.update(self.params.time_step)
        self.assertGreater(ball.angular_velocity, 0.99)  # Should be close to original

    def test_energy_conservation_at_equilibrium(self):
        """Test that a ball at rest stays at rest"""
        ball = Ball(self.mass, 0, self.pivot)
        ball.angular_velocity = 0

        for _ in range(10):
            ball.update(self.params.time_step)

        # At equilibrium with no initial velocity, ball should remain at equilibrium
        self.assertAlmostEqual(ball.angle, 0, places=3)
        self.assertAlmostEqual(ball.angular_velocity, 0, places=3)


class TestButton(unittest.TestCase):
    """Test cases for the Button class"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.button = Button(50, 50, 100, 40, "Test Button", (100, 100, 200))

    def test_button_initialization(self):
        """Test that Button initializes with correct properties"""
        self.assertEqual(self.button.rect.x, 50)
        self.assertEqual(self.button.rect.y, 50)
        self.assertEqual(self.button.rect.width, 100)
        self.assertEqual(self.button.rect.height, 40)
        self.assertEqual(self.button.text, "Test Button")
        self.assertEqual(self.button.color, (100, 100, 200))

    def test_hover_color_calculation(self):
        """Test that hover color is brighter than base color"""
        for i in range(3):
            self.assertGreaterEqual(self.button.hover_color[i], self.button.color[i])
            self.assertLessEqual(self.button.hover_color[i], 255)

    def test_is_clicked_with_click_event(self):
        """Test that is_clicked returns True when button is clicked"""
        # Create a mock mouse button down event at button position
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.button = 1  # Left mouse button
        event.pos = (75, 70)  # Inside button

        self.assertTrue(self.button.is_clicked(event))

    def test_is_clicked_outside_button(self):
        """Test that is_clicked returns False when clicking outside button"""
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.button = 1
        event.pos = (200, 200)  # Outside button

        self.assertFalse(self.button.is_clicked(event))

    def test_is_clicked_with_wrong_event_type(self):
        """Test that is_clicked returns False for non-click events"""
        event = Mock()
        event.type = pygame.MOUSEMOTION
        event.button = 1
        event.pos = (75, 70)

        self.assertFalse(self.button.is_clicked(event))


class TestSlider(unittest.TestCase):
    """Test cases for the Slider class"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.slider = Slider(50, 50, 300, 10, 0, 100, 50, "Test Slider", step=1)

    def test_slider_initialization(self):
        """Test that Slider initializes with correct properties"""
        self.assertEqual(self.slider.rect.x, 50)
        self.assertEqual(self.slider.rect.y, 50)
        self.assertEqual(self.slider.rect.width, 300)
        self.assertEqual(self.slider.min_val, 0)
        self.assertEqual(self.slider.max_val, 100)
        self.assertEqual(self.slider.value, 50)
        self.assertEqual(self.slider.label, "Test Slider")
        self.assertEqual(self.slider.step, 1)
        self.assertFalse(self.slider.active)

    def test_slider_value_bounds(self):
        """Test that slider value stays within bounds"""
        # Test initial value
        self.assertGreaterEqual(self.slider.value, self.slider.min_val)
        self.assertLessEqual(self.slider.value, self.slider.max_val)

    def test_handle_event_mouse_down(self):
        """Test slider activation on mouse down"""
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.button = 1
        # Position on slider handle (middle of slider)
        handle_x = self.slider.rect.x + (self.slider.value - self.slider.min_val) / \
                   (self.slider.max_val - self.slider.min_val) * self.slider.rect.width
        handle_y = self.slider.rect.y + self.slider.rect.height // 2
        event.pos = (handle_x, handle_y)

        self.slider.handle_event(event)
        self.assertTrue(self.slider.active)

    def test_handle_event_mouse_up(self):
        """Test slider deactivation on mouse up"""
        self.slider.active = True
        event = Mock()
        event.type = pygame.MOUSEBUTTONUP
        event.button = 1

        self.slider.handle_event(event)
        self.assertFalse(self.slider.active)

    def test_handle_event_mouse_motion(self):
        """Test slider value update on mouse motion when active"""
        self.slider.active = True
        event = Mock()
        event.type = pygame.MOUSEMOTION
        # Move to 75% of the slider
        event.pos = (self.slider.rect.x + int(0.75 * self.slider.rect.width),
                     self.slider.rect.y)

        result = self.slider.handle_event(event)
        self.assertTrue(result)
        # Value should be approximately 75 (75% of 0-100 range)
        self.assertAlmostEqual(self.slider.value, 75, delta=2)

    def test_slider_step_quantization(self):
        """Test that slider values are quantized to step size"""
        slider = Slider(50, 50, 300, 10, 0, 10, 5, "Test", step=0.5)
        slider.active = True

        event = Mock()
        event.type = pygame.MOUSEMOTION
        # Set to a position that would give 5.23, should round to 5.5
        event.pos = (slider.rect.x + int(0.523 * slider.rect.width), slider.rect.y)

        slider.handle_event(event)
        # Value should be a multiple of 0.5
        self.assertEqual(slider.value % 0.5, 0)


class TestInitializeSimulation(unittest.TestCase):
    """Test cases for the initialize_simulation function"""

    @patch('NewtonCradle.params')
    def test_correct_number_of_balls(self, mock_params):
        """Test that initialize_simulation creates the correct number of balls"""
        mock_params.num_balls = 5
        mock_params.ball_radius = 20
        mock_params.ball_mass = 1.0
        mock_params.initial_angle = math.pi / 4

        balls = initialize_simulation()
        self.assertEqual(len(balls), 5)

    @patch('NewtonCradle.params')
    def test_rightmost_ball_raised(self, mock_params):
        """Test that the rightmost ball is raised to initial_angle"""
        mock_params.num_balls = 5
        mock_params.ball_radius = 20
        mock_params.ball_mass = 1.0
        mock_params.initial_angle = math.pi / 4

        balls = initialize_simulation()
        # Rightmost ball (last in list) should have initial angle
        self.assertAlmostEqual(balls[-1].angle, math.pi / 4, places=5)

    @patch('NewtonCradle.params')
    def test_other_balls_at_equilibrium(self, mock_params):
        """Test that all balls except rightmost start at equilibrium"""
        mock_params.num_balls = 5
        mock_params.ball_radius = 20
        mock_params.ball_mass = 1.0
        mock_params.initial_angle = math.pi / 4

        balls = initialize_simulation()
        # All balls except the last should have angle = 0
        for i in range(len(balls) - 1):
            self.assertEqual(balls[i].angle, 0)

    @patch('NewtonCradle.params')
    def test_balls_have_correct_mass(self, mock_params):
        """Test that all balls have the correct mass"""
        mock_params.num_balls = 3
        mock_params.ball_radius = 20
        mock_params.ball_mass = 2.5
        mock_params.initial_angle = math.pi / 4

        balls = initialize_simulation()
        for ball in balls:
            self.assertEqual(ball.mass, 2.5)

    @patch('NewtonCradle.params')
    def test_ball_spacing(self, mock_params):
        """Test that balls are spaced correctly"""
        mock_params.num_balls = 3
        mock_params.ball_radius = 20
        mock_params.ball_mass = 1.0
        mock_params.initial_angle = 0

        balls = initialize_simulation()
        # All balls at equilibrium, check horizontal spacing
        expected_spacing = 2 * mock_params.ball_radius

        for i in range(len(balls) - 1):
            spacing = balls[i + 1].pivot[0] - balls[i].pivot[0]
            self.assertAlmostEqual(spacing, expected_spacing, places=5)


class TestResolveCollisions(unittest.TestCase):
    """Test cases for the resolve_collisions function"""

    @patch('NewtonCradle.params')
    def test_velocity_swap_on_collision(self, mock_params):
        """Test that velocities are swapped when balls collide"""
        mock_params.ball_radius = 20
        mock_params.rod_length = 200

        # Create two balls close together with different velocities
        ball1 = Ball(1.0, 0, (100, 100))
        ball2 = Ball(1.0, 0, (140, 100))  # Exactly 2*radius apart

        ball1.angular_velocity = 0
        ball2.angular_velocity = -0.1  # Moving toward ball1

        balls = [ball1, ball2]
        resolve_collisions(balls)

        # Velocities should be swapped
        self.assertAlmostEqual(ball1.angular_velocity, -0.1, places=5)
        self.assertAlmostEqual(ball2.angular_velocity, 0, places=5)

    @patch('NewtonCradle.params')
    def test_no_collision_when_separated(self, mock_params):
        """Test that no collision occurs when balls are separated"""
        mock_params.ball_radius = 20
        mock_params.rod_length = 200

        # Create two balls far apart
        ball1 = Ball(1.0, 0, (100, 100))
        ball2 = Ball(1.0, 0, (200, 100))  # Far apart

        initial_v1 = 0.1
        initial_v2 = 0.2
        ball1.angular_velocity = initial_v1
        ball2.angular_velocity = initial_v2

        balls = [ball1, ball2]
        resolve_collisions(balls)

        # Velocities should remain unchanged
        self.assertAlmostEqual(ball1.angular_velocity, initial_v1, places=5)
        self.assertAlmostEqual(ball2.angular_velocity, initial_v2, places=5)

    @patch('NewtonCradle.params')
    def test_no_collision_when_moving_apart(self, mock_params):
        """Test that no collision occurs when balls are moving apart"""
        mock_params.ball_radius = 20
        mock_params.rod_length = 200

        ball1 = Ball(1.0, 0, (100, 100))
        ball2 = Ball(1.0, 0, (140, 100))

        ball1.angular_velocity = -0.1  # Moving left
        ball2.angular_velocity = 0.1   # Moving right (away from ball1)

        balls = [ball1, ball2]
        initial_v1 = ball1.angular_velocity
        initial_v2 = ball2.angular_velocity

        resolve_collisions(balls)

        # Velocities should remain unchanged (moving apart)
        self.assertAlmostEqual(ball1.angular_velocity, initial_v1, places=5)
        self.assertAlmostEqual(ball2.angular_velocity, initial_v2, places=5)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
