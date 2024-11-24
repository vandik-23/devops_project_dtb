from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        pass

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        pass

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        pass

    def print_state(self) -> None:
        """Print the current game state."""
        state = self.get_state()

        # Build the masked word with guessed letters
        masked_word = " ".join(
            [letter if letter.upper() in state.guesses else "_" for letter in state.word_to_guess.upper()]
        )

        # Display the word with blanks and guessed letters
        print(f"Word: {masked_word}")

        # Display incorrect guesses
        if state.incorrect_guesses:
            print(f"Incorrect guesses: {', '.join(state.incorrect_guesses)}")
        else:
            print("Incorrect guesses: None")

        # Display the current phase of the game
        print(f"Game Phase: {state.phase.value}")

        # Additional information if the game is finished
        if state.phase == GamePhase.FINISHED:
            if len(state.incorrect_guesses) >= 8:
                print("Game Over! You have lost.")
            else:
                print("Congratulations! You have guessed the word.")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)
