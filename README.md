# Planet Wars Bot with Behavior Trees

## Introduction

This project implements a reactive bot for the game Planet Wars, a real-time strategy game where the objective is to conquer a galaxy planet by planet. The bot is designed using Behavior Trees, aiming to outperform a series of test bots provided within the project.

## Getting Started

### Prerequisites

- Python (version as specified in your project requirements)
- Java (for running the Planet Wars game interface)

### Installation

Clone this repository to your local machine:

```bash
git clone [repository URL]
cd [local repository]
```

Ensure Python and Java are correctly installed and configured on your system.

### Running the Bot

To run the game and test the bot, navigate to the `/src` folder and execute:

```bash
$ python run.py
```

This command initiates a match between your bot and predefined opponent bots, displaying the match in a new window.

## Project Structure

- `run.py`: Entry point for running matches and testing the bot.
- `behaviour_tree_bot/`: Contains the bot logic and behavior tree implementation.
  - `bt_bot.py`: Main bot strategy implementation file.
  - `behaviors.py`: Action nodes for the behavior tree.
  - `checks.py`: State-based conditional checks for the tree.
  - `bt_nodes.py`: Node classes for constructing the behavior tree.
- `planet_wars.py`: Game state management and utility functions.

## References

 - Behavior Trees for AI: http://gamasutra.com/blogs/ChrisSimpson/20140717/221339/Behavior_trees_for_AI_How_they_work.php
 - Decorators in Behavior Trees: http://aigamedev.com/open/article/decorator/
 - Planet Wars Game Description: http://franz.com/services/conferences_seminars/webinar_1-20-11.gm.pdf
