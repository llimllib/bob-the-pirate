#!/usr/bin/env python3
"""Bob the Pirate - A Megaman-style platformer."""

from game.game import Game


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
