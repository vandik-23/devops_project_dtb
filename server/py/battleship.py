from typing import List, Optional
from enum import Enum
import random

from pydantic import BaseModel

from server.py.game import Game, Player


class ActionType(str, Enum):
    SET_SHIP = 'set_ship'
    SHOOT = 'shoot'


class BattleshipAction(BaseModel):
    action_type: ActionType
    ship_name: Optional[str]
    location: List[str]


class Ship(BaseModel):
    name: str
    length: int
    location: Optional[List[str]]


class PlayerState(BaseModel):
    name: str
    ships: List[Ship]
    shots: List[str]
    successful_shots: List[str]


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started (including setting ships)
    RUNNING = 'running'        # while the game is running (shooting)
    FINISHED = 'finished'      # when the game is finished


class BattleshipGameState(BaseModel):
    idx_player_active: int
    phase: GamePhase
    winner: Optional[int]
    players: List[PlayerState]


class Battleship(Game):

    def __init__(self):
        """ Game initialization (set_state call not necessary) """
        self.state = BattleshipGameState(
            idx_player_active=0,
            phase=GamePhase.SETUP,
            winner=None,
            players=[],
        )

    def print_state(self) -> None:
        """ Set the game to a given state """
        if self.state is None:
            raise ValueError("Game state not set yet. Use set_state() to set the game state.")
        print(self.state.model_dict())

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state """
        if self.state is None:
            raise ValueError("Game state not set yet. Use set_state() to set the game state.")
        return self.state

    def set_state(self, state: BattleshipGameState) -> None:
        """ Print the current game state """
        self.state = state

    def get_list_action(self) -> List[BattleshipAction]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: BattleshipAction) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Battleship()
    player_1 = PlayerState(
        name="Player 1",
        ships=[
            Ship(name="Carrier", length=5, location=["H5", "H6", "H7", "H8", "H9"]),
            Ship(name="Battleship", length=4, location=["G1", "H1", "I1", "J1"]),
            Ship(name="Cruiser", length=3, location=["D9", "E9", "F9"]),
            Ship(name="Submarine", length=3, location=["D1", "D2", "D3"]),
            Ship(name="Destroyer", length=2, location=["A1", "B1"]),
        ],
        shots=[],
        successful_shots=[],
    )
    player_2 = PlayerState(
        name="Player 2",
        ships=[
            Ship(name="Carrier", length=5, location=["A5", "A6", "A7", "A8", "A9"]),
            Ship(name="Battleship", length=4, location=["A1", "B1", "C1", "D1"]),
            Ship(name="Cruiser", length=3, location=["H10", "I10", "J10"]),
            Ship(name="Submarine", length=3, location=["G2", "G3", "G4"]),
            Ship(name="Destroyer", length=2, location=["J5", "J6"]),
        ],
        shots=[],
        successful_shots=[],
    )
    players = [player_1, player_2]
    game_state = BattleshipGameState(
        idx_player_active=0,
        phase=GamePhase.SETUP,
        winner=None,
        players=players,
    )
    game.set_state(game_state)
    game.print_state()
    game.get_list_action()
