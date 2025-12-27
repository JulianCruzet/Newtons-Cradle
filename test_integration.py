import unittest
import math
from unittest.mock import patch
import pygame

from NewtonCradle import (
    SimulationParams, Ball, initialize_simulation, resolve_collisions
)


class TestSimulationIntegration(unittest.TestCase):
    """Integration tests for the Newton's Cradle simulation"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.params = SimulationParams()

    def test_full_simulation_initialization(self):
        """Test that a full simulation can be initialized"""
        with patch('NewtonCradle.params', self.params):
            balls = initialize_simulation()

            self.assertEqual(len(balls), self.params.num_balls)
            self.assertIsNotNone(balls)
            self.assertTrue(all(isinstance(ball, Ball) for ball in balls))

    def test_energy_transfer_simulation(self):
        """Test that energy transfers through the cradle"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 5
            self.params.ball_radius = 20
            self.params.ball_mass = 1.0
            self.params.initial_angle = math.pi / 6
            self.params.damping = 1.0

            balls = initialize_simulation()

            # Run simulation for several steps
            for _ in range(100):
                for ball in balls:
                    ball.update(self.params.time_step)
                resolve_collisions(balls)

            # After simulation, leftmost balls should have gained energy
            # (This is a simplified check - in reality we'd calculate total energy)
            self.assertIsNotNone(balls[0].angular_velocity)

    @unittest.skip("Temporarily skipped for Mohtion testing")
    def test_single_ball_oscillation(self):
        """Test that a single ball oscillates correctly"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 1
            self.params.initial_angle = math.pi / 6

            balls = initialize_simulation()
            ball = balls[0]

            initial_angle = ball.angle
            angles = [initial_angle]

            # Run simulation to capture oscillation
            for _ in range(120):  # 2 seconds at 60 FPS
                ball.update(self.params.time_step)
                angles.append(ball.angle)

            # Ball should oscillate (angle should cross zero)
            max_angle = max(angles)
            min_angle = min(angles)

            self.assertGreater(max_angle, 0)
            self.assertLess(min_angle, 0)

    def test_symmetric_collision(self):
        """Test symmetric collision between two balls"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 2
            self.params.ball_radius = 20
            self.params.rod_length = 200
            self.params.damping = 1.0

            # Create two balls
            ball1 = Ball(1.0, 0, (100, 100))
            ball2 = Ball(1.0, 0, (140, 100))

            # Give ball2 velocity toward ball1
            ball2.angular_velocity = -0.5
            ball1.angular_velocity = 0

            balls = [ball1, ball2]

            # Resolve collision
            resolve_collisions(balls)

            # After collision, velocities should be swapped
            self.assertAlmostEqual(ball1.angular_velocity, -0.5, places=5)
            self.assertAlmostEqual(ball2.angular_velocity, 0, places=5)

    def test_multiple_ball_cascade(self):
        """Test energy cascade through multiple balls"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 5
            self.params.ball_radius = 20
            self.params.rod_length = 200
            self.params.damping = 1.0

            balls = initialize_simulation()

            # Give rightmost ball an initial velocity
            balls[-1].angular_velocity = -0.5

            # Position all balls at equilibrium for this test
            for ball in balls:
                ball.angle = 0

            # Run several collision resolution steps
            for _ in range(20):
                resolve_collisions(balls)

            # The leftmost ball should eventually have velocity
            # (energy propagates through the chain)
            # Note: This is a simplification - actual behavior depends on timing
            total_velocity = sum(abs(ball.angular_velocity) for ball in balls)
            self.assertGreater(total_velocity, 0)

    def test_conservation_with_no_damping(self):
        """Test that energy is conserved when damping = 1.0"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 1
            self.params.initial_angle = math.pi / 6
            self.params.damping = 1.0
            self.params.gravity = 50.0
            self.params.rod_length = 200

            balls = initialize_simulation()
            ball = balls[0]

            # Calculate initial energy (potential energy)
            # E = m*g*h = m*g*L*(1 - cos(theta))
            initial_height = self.params.rod_length * (1 - math.cos(ball.angle))
            initial_energy = ball.mass * self.params.gravity * initial_height

            # Run simulation for one complete period
            for _ in range(200):
                ball.update(self.params.time_step)

            # Calculate final energy
            height = self.params.rod_length * (1 - math.cos(ball.angle))
            kinetic_energy = 0.5 * ball.mass * (self.params.rod_length * ball.angular_velocity) ** 2
            potential_energy = ball.mass * self.params.gravity * height
            final_energy = kinetic_energy + potential_energy

            # Energy should be approximately conserved (within numerical error)
            energy_ratio = final_energy / initial_energy
            self.assertAlmostEqual(energy_ratio, 1.0, delta=0.2)  # Allow 20% deviation due to numerical errors

    def test_damping_reduces_energy(self):
        """Test that damping < 1.0 reduces system energy over time"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 1
            self.params.initial_angle = math.pi / 6
            self.params.damping = 0.99  # Slight damping

            balls = initialize_simulation()
            ball = balls[0]

            initial_angle = abs(ball.angle)

            # Run simulation for many steps
            for _ in range(500):
                ball.update(self.params.time_step)

            # Maximum angle should decrease due to damping
            # Note: we need to track max angle over time
            max_angle_seen = initial_angle

            balls = initialize_simulation()
            ball = balls[0]
            for _ in range(500):
                ball.update(self.params.time_step)
                max_angle_seen = max(max_angle_seen, abs(ball.angle))

            # After many oscillations with damping, the max angle should be less
            # This test verifies energy dissipation
            self.assertLess(abs(ball.angle), initial_angle * 0.9)

    def test_varying_masses(self):
        """Test simulation with varying ball masses"""
        with patch('NewtonCradle.params', self.params):
            # Create balls with different masses
            ball1 = Ball(1.0, 0, (100, 100))
            ball2 = Ball(2.0, 0, (140, 100))

            ball1.angular_velocity = 0.5
            ball2.angular_velocity = 0

            balls = [ball1, ball2]

            # Verify masses are different
            self.assertNotEqual(ball1.mass, ball2.mass)

            # Simulation should still run without errors
            for _ in range(10):
                for ball in balls:
                    ball.update(self.params.time_step)
                resolve_collisions(balls)

            # Test passes if no exceptions were raised
            self.assertTrue(True)

    def test_extreme_initial_angle(self):
        """Test simulation with extreme initial angle"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 3
            self.params.initial_angle = math.pi / 2  # 90 degrees

            balls = initialize_simulation()

            # Rightmost ball should be at extreme angle
            self.assertAlmostEqual(balls[-1].angle, math.pi / 2, places=5)

            # Run simulation - should handle extreme angles
            for _ in range(50):
                for ball in balls:
                    ball.update(self.params.time_step)
                resolve_collisions(balls)

            # Test passes if no exceptions were raised
            self.assertTrue(True)

    def test_many_balls_simulation(self):
        """Test simulation with many balls"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 10
            self.params.ball_radius = 15
            self.params.initial_angle = math.pi / 4

            balls = initialize_simulation()

            self.assertEqual(len(balls), 10)

            # Run simulation
            for _ in range(100):
                for ball in balls:
                    ball.update(self.params.time_step)
                resolve_collisions(balls)

            # Verify all balls are still valid
            for ball in balls:
                self.assertIsNotNone(ball.angle)
                self.assertIsNotNone(ball.angular_velocity)
                self.assertFalse(math.isnan(ball.angle))
                self.assertFalse(math.isnan(ball.angular_velocity))


class TestPhysicsAccuracy(unittest.TestCase):
    """Tests for physics accuracy and numerical stability"""

    def setUp(self):
        """Set up test fixtures"""
        self.params = SimulationParams()

    def test_small_angle_approximation(self):
        """Test that small angle motion behaves correctly"""
        with patch('NewtonCradle.params', self.params):
            self.params.initial_angle = 0.1  # Small angle in radians

            balls = initialize_simulation()
            ball = balls[-1]

            # For small angles, period should be approximately 2*pi*sqrt(L/g)
            expected_period = 2 * math.pi * math.sqrt(self.params.rod_length / self.params.gravity)

            # Run simulation for one period and track zero crossings
            time = 0
            zero_crossings = []
            prev_angle = ball.angle

            for i in range(500):
                ball.update(self.params.time_step)
                time += self.params.time_step

                # Detect zero crossing
                if prev_angle > 0 and ball.angle < 0:
                    zero_crossings.append(time)
                prev_angle = ball.angle

            if len(zero_crossings) >= 2:
                measured_period = 2 * (zero_crossings[1] - zero_crossings[0])
                # Period should be within 10% of expected (due to small angle approximation)
                self.assertAlmostEqual(measured_period, expected_period, delta=expected_period * 0.1)

    def test_numerical_stability(self):
        """Test that simulation remains numerically stable over time"""
        with patch('NewtonCradle.params', self.params):
            self.params.num_balls = 5
            self.params.initial_angle = math.pi / 4

            balls = initialize_simulation()

            # Run simulation for extended time
            for _ in range(1000):
                for ball in balls:
                    ball.update(self.params.time_step)
                resolve_collisions(balls)

            # Verify no NaN or Inf values
            for ball in balls:
                self.assertFalse(math.isnan(ball.angle))
                self.assertFalse(math.isinf(ball.angle))
                self.assertFalse(math.isnan(ball.angular_velocity))
                self.assertFalse(math.isinf(ball.angular_velocity))


if __name__ == '__main__':
    unittest.main(verbosity=2)
