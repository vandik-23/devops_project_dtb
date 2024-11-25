from typing import List, Optional
import random
from enum import Enum

from pydantic import BaseModel

from server.py.game import Game, Player


class GuessLetterAction(BaseModel):
    letter: str


class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished


class HangmanGameState(BaseModel):
    word_to_guess: str
    phase: GamePhase
    guesses: List[str]
    incorrect_guesses: List[str]


class Hangman(Game):

    def __init__(self, word_to_guess:str ="") -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.state = None

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        if self.state is None:
            raise Exception("Game state not set yet. Set the game state using `set_state` method.")
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        for letter in state.guesses:
            if letter not in state.word_to_guess.upper():
                state.incorrect_guesses.append(letter.upper())
        
        self.state = state

    def print_state(self) -> None:
        """Print the current game state."""
        masked_state = self.get_player_view()
        
        if masked_state is not None:
            print(masked_state.model_dump())
        else:
            print("No state set yet. Use the `set_state()` method to set a state.")


    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """

        # all_letters contains all possible letters for the player
        all_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # from current game state all guessed letters
        guessed_letters = set(letter.upper() for letter in self.state.guesses)

        # Computes all unguessed letters
        unguessed_letters = all_letters - guessed_letters

        # Creates a GuessLetterAction for each unguessed letter
        return [GuessLetterAction(letter) for letter in sorted(unguessed_letters)]


    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """        
        if self.state.phase != GamePhase.RUNNING:
            self.state.phase = GamePhase.RUNNING
        
        self.state.guesses.append(action.letter.upper()) # add letter to guesses
        if all(letter in self.state.guesses for letter in self.state.word_to_guess.upper()):
            self.state.phase = GamePhase.FINISHED
        
        if action.letter.upper() not in self.state.word_to_guess.upper():
            self.state.incorrect_guesses.append(action.letter.upper()) # add letter to incorrect guesses
            if len(self.state.incorrect_guesses) >= 8:
                self.state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""

        masked_word = "".join([char if char.upper() in self.state.guesses else "_" for char in self.state.word_to_guess])
        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses)



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
