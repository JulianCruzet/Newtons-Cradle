# Newton's Cradle Simulation

This is a Newton's Cradle simulation developed as a course project for **Simulations and Modelling**. The simulation is implemented in Python using Pygame and is designed to model the dynamics of a Newton's cradle with a focus on energy conservation and realistic collision behavior.

## Overview

The simulation models a Newton's Cradle, where the two end balls swing while the intermediate balls remain nearly stationary. Key features include:

- **Accurate Pendulum Dynamics:**  
  Each ball is modeled as a pendulum attached to its own pivot, updating its motion according to the pendulum equation.
  
- **Iterative Collision Resolution:**  
  An iterative algorithm resolves collisions between adjacent balls to simulate the propagation of energy through the cradle.
  
- **Energy Conservation:**  
  When damping is set to 1.0 and equal masses are used, the simulation nearly perfectly conserves energy, so that the leftmost ball rises to the same height as the initially raised rightmost ball.
  
- **Interactive User Interface:**  
  The simulation includes sliders and buttons to adjust parameters in real time, including the number of balls, ball radius, gravity, rod length, ball mass, damping, and the initial angle.

## Features

- **Real-Time Simulation:** Visualizes the energy transfer and collision cascade through the balls.
- **Adjustable Parameters:**  
  Use UI sliders to control:
  - **Number of Balls:** Total balls in the cradle.
  - **Ball Radius:** The size of each ball.
  - **Gravity:** Gravitational constant for the simulation.
  - **Rod Length:** The length of the pendulum rods.
  - **Ball Mass:** Mass of each ball.
  - **Damping:** Damping factor (set to 1.0 for ideal, lossless energy transfer).
  - **Initial Angle (rad):** Starting angle for the raised (rightmost) ball.
- **User Controls:**  
  - **Start/Pause Button:** Start or pause the simulation.
  - **Reset Button:** Reset the simulation with the current parameters.

## Requirements

- **Python 3.x**
- **Pygame**  
  Install via pip:
  ```bash
  pip install pygame
  ```

## How to Run

1. Clone or download the project repository.
2. Make sure you have Python and Pygame installed.
3. Run the simulation by pressing the 'run' button or by executing:
   ```bash
   python NewtonCradle.py
   ```

## Project Structure

- **NewtonCradle.py**: Main simulation code.
- **README.md**: This README file.

## Usage Instructions

Upon running the simulation, you will see a Newton's cradle with the rightmost ball raised. Use the following controls:

- **Start/Pause Button:**  
  Toggle the simulation on or off.
  
- **Reset Button:**  
  Reset the simulation with any updated parameters from the sliders.
  
- **Sliders:**  
  Adjust the simulation parameters in real time:
  - **Number of Balls:** Set how many balls are in the cradle.
  - **Ball Radius:** Define the size of the balls.
  - **Gravity:** Adjust the gravitational constant.
  - **Rod Length:** Set the length of each pendulum rod.
  - **Ball Mass:** Adjust the mass of each ball.
  - **Damping:** Control the damping factor (set to 1.0 for lossless energy transfer).
  - **Initial Angle (rad):** Change the starting angle of the rightmost ball.

## Credits

Developed by:
- Julian Cruzet ( 100870375 )
- Jonathan McKesey ( )
