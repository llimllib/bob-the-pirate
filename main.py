#!/usr/bin/env python3
"""Bob the Pirate - A Megaman-style platformer."""

import argparse

from game.game import Game


def main():
    """Entry point for the game."""
    parser = argparse.ArgumentParser(description="Bob the Pirate - A Megaman-style platformer")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug output (player state, animation info)"
    )
    args = parser.parse_args()

    game = Game(debug=args.verbose)
    game.run()


if __name__ == "__main__":
    main()
