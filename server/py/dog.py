# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
from server.py.game import Game, Player
from typing import Any, List, Optional, ClassVar, Literal
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: str  # position on board (0 to 95)
    is_save: bool = False  # true if marble was moved out of kennel and was not yet moved
    in_kennel: bool = True  # true if marble is in kennel


class PlayerState(BaseModel):
    name: str  # name of player
    colour: Literal["red", "blue", "green", "yellow"]  # colour of player
    list_card: List[Card]  # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card  # card to play
    pos_from: Optional[int] = None # position to move the marble from
    pos_to: Optional[int] = None # position to move the marble to
    card_swap: Optional[Card] = None # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = "setup"  # before the game has started
    RUNNING = "running"  # while the game is running
    FINISHED = "finished"  # when the game is finished


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ["♠", "♥", "♦", "♣"]  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        "2", "3", "4", "5", "6", "7", "8", "9", "10",  # 13 ranks + Joker
        "J", "Q", "K", "A", "JKR"
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit="♠", rank="2"), Card(suit="♥", rank="2"), Card(suit="♦", rank="2"), Card(suit="♣", rank="2"),
        # 3: Move 3 spots forward
        Card(suit="♠", rank="3"), Card(suit="♥", rank="3"), Card(suit="♦", rank="3"), Card(suit="♣", rank="3"),
        # 4: Move 4 spots forward or back
        Card(suit="♠", rank="4"), Card(suit="♥", rank="4"), Card(suit="♦", rank="4"), Card(suit="♣", rank="4"),
        # 5: Move 5 spots forward
        Card(suit="♠", rank="5"), Card(suit="♥", rank="5"), Card(suit="♦", rank="5"), Card(suit="♣", rank="5"),
        # 6: Move 6 spots forward
        Card(suit="♠", rank="6"), Card(suit="♥", rank="6"), Card(suit="♦", rank="6"), Card(suit="♣", rank="6"),
        # 7: Move 7 single steps forward
        Card(suit="♠", rank="7"), Card(suit="♥", rank="7"), Card(suit="♦", rank="7"), Card(suit="♣", rank="7"),
        # 8: Move 8 spots forward
        Card(suit="♠", rank="8"), Card(suit="♥", rank="8"), Card(suit="♦", rank="8"), Card(suit="♣", rank="8"),
        # 9: Move 9 spots forward
        Card(suit="♠", rank="9"), Card(suit="♥", rank="9"), Card(suit="♦", rank="9"), Card(suit="♣", rank="9"),
        # 10: Move 10 spots forward
        Card(suit="♠", rank="10"), Card(suit="♥", rank="10"), Card(suit="♦", rank="10"), Card(suit="♣", rank="10"),
        # Jake: A marble must be exchanged
        Card(suit="♠", rank="J"), Card(suit="♥", rank="J"), Card(suit="♦", rank="J"), Card(suit="♣", rank="J"),
        # Queen: Move 12 spots forward
        Card(suit="♠", rank="Q"), Card(suit="♥", rank="Q"), Card(suit="♦", rank="Q"), Card(suit="♣", rank="Q"),
        # King: Start or move 13 spots forward
        Card(suit="♠", rank="K"), Card(suit="♥", rank="K"), Card(suit="♦", rank="K"), Card(suit="♣", rank="K"),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit="♠", rank="A"), Card(suit="♥", rank="A"), Card(suit="♦", rank="A"), Card(suit="♣", rank="A"),
        # Joker: Use as any other card you want
        Card(suit="", rank="JKR"), Card(suit="", rank="JKR"), Card(suit="", rank="JKR"),
    ] * 2

    cnt_player: int = 4  # number of players (must be 4)
    phase: GamePhase  # current phase of the game
    cnt_round: int  # current round
    bool_card_exchanged: bool  # true if cards was exchanged in round
    idx_player_started: int  # index of player that started the round
    idx_player_active: int  # index of active player in round
    list_player: List[PlayerState]  # list of players
    list_card_draw: List[Card]  # list of cards to draw
    list_card_discard: List[Card]  # list of cards discarded
    card_active: Optional[Card]  # active card (for 7 and JKR with sequence of actions)


class KennelAndStartNumbers(dict[str, Any], Enum):
    blue = {
        "kennel": ["64", "65", "66", "67"],
        "start": 0,
    }
    green = {
        "kennel": ["72", "73", "74", "75"],
        "start": 16,
    }
    red = {
        "kennel": ["80", "81", "82", "83"],
        "start": 32,
    }
    yellow = {
        "kennel": ["88", "89", "90", "91"],
        "start": 48,
    }


class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        random.shuffle(GameState.LIST_CARD)
        self.state = GameState(
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(
                    name="Tick",
                    colour="blue",
                    list_card=GameState.LIST_CARD[:6],
                    list_marble=[Marble(pos="64"), Marble(pos="65"), Marble(pos="66"), Marble(pos="67")],
                ),
                PlayerState(
                    name="Trick",
                    colour="green",
                    list_card=GameState.LIST_CARD[6:12],
                    list_marble=[Marble(pos="72"), Marble(pos="73"), Marble(pos="74"), Marble(pos="75")],
                ),
                PlayerState(
                    name="Track",
                    colour="red",
                    list_card=GameState.LIST_CARD[12:18],
                    list_marble=[Marble(pos="80"), Marble(pos="81"), Marble(pos="82"), Marble(pos="83")],
                ),
                PlayerState(
                    name="Donald",
                    colour="yellow",
                    list_card=GameState.LIST_CARD[18:24],
                    list_marble=[Marble(pos="88"), Marble(pos="89"), Marble(pos="90"), Marble(pos="91")],
                ),
            ],
            list_card_draw=GameState.LIST_CARD[24:],
            list_card_discard=[],
            card_active=None,
        )

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state"""
        self.state = state

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state"""
        if self.state is not None:
            return self.state
        raise ValueError("Game state not set. Set with `set_state` method.")

    def print_state(self) -> None:
        """Print the current game state"""
        pass

    def get_list_action(self) -> List[Action]:
        """Get a list of possible actions for the active player"""
        player = self.state.list_player[self.state.idx_player_active]
        marbles_in_play, marbles_in_kennel = self._get_marbles_in_kennel_and_in_play(
            player
        )
        if len(marbles_in_kennel) == 4:
            return self._if_all_marbles_in_kennel(player, marbles_in_kennel)
        else:
            pass  # TODO: implement for other tests

    def _get_marbles_in_kennel_and_in_play(
        self, player: PlayerState
    ) -> tuple[list[Marble], list[Marble]]:
        marbles_in_play, marbles_in_kennel = [], []
        for marble in player.list_marble:
            if not marble.in_kennel:
                marbles_in_play.append(marble)
            else:
                marbles_in_kennel.append(marble)
        return marbles_in_play, marbles_in_kennel

    def _if_all_marbles_in_kennel(
        self,
        player: PlayerState,
        marbles_in_kennel: list[Marble],
    ) -> list[Action]:
        """Lists all actions that are possible if all marbles of a player are in the kennel."""
        kennels_and_start = KennelAndStartNumbers[player.colour]
        card_ranks = [card.rank for card in player.list_card]
        if not any(item in card_ranks for item in ["JKR", "A", "K"]):
            return []
        else:
            marble_in_kennel_positions = [marble.pos for marble in marbles_in_kennel]
            return [
                Action(
                    card=card,
                    pos_from=min(marble_in_kennel_positions),
                    pos_to=kennels_and_start["start"],
                )
                for card in player.list_card
                if card.rank in ["JKR", "A", "K"]
            ]

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()
