#!/usr/bin/env python3
"""Bob the Pirate - A Megaman-style platformer.

This entry point supports both native and web (WASM) deployment.
For web builds using pygbag, the game runs with an async loop.
For native builds, it uses the standard synchronous game loop.
"""

import sys

# Detect if running in web/WASM environment
# pygbag sets sys.platform to 'emscripten'
IS_WEB = sys.platform == "emscripten"

if IS_WEB:
    # Web/WASM mode - use async loop for browser compatibility
    import asyncio

    import pygame

    from game.game import Game
    from game.settings import FPS

    async def main_async():
        """Async entry point for web deployment."""
        game = Game(debug=False)

        while game.running:
            game.clock.tick(FPS)
            game.handle_events()
            game.update()
            game.draw()

            # Yield control to the browser - required for WASM
            await asyncio.sleep(0)

        pygame.quit()

    # pygbag expects this pattern
    asyncio.run(main_async())

else:
    # Native mode - standard synchronous execution with CLI args
    import argparse

    from game.game import Game

    def main():
        """Entry point for native game."""
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
