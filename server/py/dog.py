import random
from enum import Enum
from typing import ClassVar, List, Literal, Optional

from pydantic import BaseModel

from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

    def __lt__(self, card: "Card") -> bool:
        return self.suit < card.suit or self.rank < card.rank


class Marble(BaseModel):
    pos: int # position on board (0 to 95)
    is_save: bool = False  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str  # name of player
    colour: Literal["RED", "BLUE", "GREEN", "YELLOW"]  # colour of player
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


class KennelNumbers(Enum):
    BLUE = (64, 65, 66, 67)
    GREEN = (72, 73, 74, 75)
    RED = (80, 81, 82, 83)
    YELLOW = (88, 89, 90, 91)


class StartNumbers(int, Enum):
    BLUE = 0
    GREEN = 16
    RED = 32
    YELLOW = 48


class FinishNumbers(Enum):
    BLUE = (68 ,69 ,70 ,71)
    GREEN = (76, 77, 78, 79)
    RED = (84, 85, 86, 87)
    YELLOW = (92, 93, 94, 95)


MOVES = {
    "2": [2],
    "3": [3],
    "4": [4, -4],
    "5": [5],
    "6": [6],
    "7": [1, 2, 3, 4, 5, 6, 7],
    "8": [8],
    "9": [9],
    "10": [10],
    "J": [],
    "Q": [12],
    "K": [13],
    "A": [1, 11],
    "JKR": [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
}

class Dog(Game):
    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        random.shuffle(GameState.LIST_CARD)
        self.state = GameState(
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(
                    name="Tick",
                    colour="BLUE",
                    list_card=GameState.LIST_CARD[:6],
                    list_marble=[Marble(pos=64), Marble(pos=65), Marble(pos=66), Marble(pos=67)],
                ),
                PlayerState(
                    name="Trick",
                    colour="GREEN",
                    list_card=GameState.LIST_CARD[6:12],
                    list_marble=[Marble(pos=72), Marble(pos=73), Marble(pos=74), Marble(pos=75)],
                ),
                PlayerState(
                    name="Track",
                    colour="RED",
                    list_card=GameState.LIST_CARD[12:18],
                    list_marble=[Marble(pos=80), Marble(pos=81), Marble(pos=82), Marble(pos=83)],
                ),
                PlayerState(
                    name="Donald",
                    colour="YELLOW",
                    list_card=GameState.LIST_CARD[18:24],
                    list_marble=[Marble(pos=88), Marble(pos=89), Marble(pos=90), Marble(pos=91)],
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
        print(self.state)

    def get_list_action(self) -> List[Action]:
        """Get a list of possible actions for the active player"""
        player = self.state.list_player[self.state.idx_player_active]

        # Checks if card exchange is completed
        if not self.state.bool_card_exchanged:
            return self._generate_card_exchange_actions(player) # calls helper method for the exchange

        marbles_in_play, marbles_in_kennel = self._get_marbles_in_kennel_and_in_play(player)

        other_marbles_in_play = []
        for idx_other_player, other_player in enumerate(self.state.list_player):
            if idx_other_player != self.state.idx_player_active:
                other_marbles_in_play.extend(self._get_marbles_in_kennel_and_in_play(other_player)[0])

        if len(marbles_in_kennel) == 4:
            return self._generate_kennel_and_joker_actions(player, marbles_in_kennel)

        # Special case: If the player has a JOKER card, generate JOKER-specific actions
        joker_actions = self._generate_joker_swap_actions(player)
        if joker_actions:
            return joker_actions

        # Special case: If the player has a JAKE card, generate JAKE-specific actions
        jake_actions = self._generate_jake_swap_actions(player, marbles_in_play, other_marbles_in_play)
        if jake_actions == []:
           jake_actions.append(Action(card=card, pos_from=StartNumbers[player.colour].value, pos_to=StartNumbers[player.colour].value)+1)
        actions = []
        for marble in marbles_in_play:
            for card in player.list_card:
                for move in MOVES[card.rank]:
                    current_position = marble.pos
                    destination = (current_position + move) % 64
                    if self._check_if_save_marble_between_current_and_destination(current_position, destination):
                        continue # action not possible
                    actions.append(Action(card=card, pos_from=current_position, pos_to=destination))
        return actions + jake_actions

    def _generate_jake_swap_actions(self, player: PlayerState, marbles_in_play: list[Marble], other_marbels_in_play: list[Marble] ) -> List[Action]:
        actions = []
        jake_cards = [card for card in player.list_card if card.rank =="J"]

        if jake_cards:
            positions_jake_from = []
            positions_jake_to = []
            for marble in marbles_in_play:
                if  marble.pos not in FinishNumbers[player.colour].value:
                    positions_jake_from.append(marble.pos)
            for marble in other_marbels_in_play:
                if marble.is_save == False and \
                    (marble.pos not in FinishNumbers['BLUE'].value \
                    or marble.pos not in FinishNumbers['RED'].value \
                    or marble.pos not in FinishNumbers['GREEN'].value \
                    or marble.pos not in FinishNumbers['YELLOW'].value \
                    or marble.pos not in StartNumbers['BLUE'].value \
                    or marble.pos not in StartNumbers['RED'].value \
                    or marble.pos not in StartNumbers['GREEN'].value \
                    or marble.pos not in StartNumbers['YELLOW'].value):
                    positions_jake_to.append(marble.pos)

            for jake_card in jake_cards:
                for position_jake_from in positions_jake_from:
                    for position_jake_to in positions_jake_to:
                        actions.append(
                            Action(
                            card=jake_card,
                            pos_from=position_jake_from,
                            pos_to=position_jake_to,
                            card_swap= None,
                            )
                        )
                        actions.append(
                            Action(
                            card=jake_card,
                            pos_from=position_jake_to,
                            pos_to=position_jake_from,
                            card_swap= None,
                            )
                        )
        return actions

    def _generate_card_exchange_actions(self, player: PlayerState) -> List[Action]:
        """returns list of possible Actions for the card exchange"""
        unique_cards = {card.rank + card.suit: card for card in player.list_card}.values()
        return [Action(card=card) for card in unique_cards]

    def _check_if_save_marble_between_current_and_destination(self, current_position: int, destination: int) -> bool:
        for player in self.state.list_player:
            for marble in player.list_marble:
                if current_position < destination:
                    if marble.pos > current_position and marble.pos <= destination and marble.is_save:
                        return True
                else: # if move is over start (0) position
                    if marble.pos < current_position and marble.pos <= destination and marble.is_save:
                        return True
        return False

    def _get_marbles_in_kennel_and_in_play(self, player: PlayerState) -> tuple[list[Marble], list[Marble]]:
        kennel_positions = KennelNumbers[player.colour].value
        marbles_in_play, marbles_in_kennel = [], []
        for marble in player.list_marble:
            if marble.pos not in kennel_positions:
                marbles_in_play.append(marble)
            else:
                marbles_in_kennel.append(marble)
        return marbles_in_play, marbles_in_kennel

    def _generate_kennel_and_joker_actions(self, player: PlayerState, marbles_in_kennel: list[Marble]) -> list[Action]:
        """
        Generate possible actions when all marbles are in the kennel and/or
        when the player has a JOKER card.
        """
        actions = []
        start_position = StartNumbers[player.colour].value

        joker_cards = [card for card in player.list_card if card.rank == "JKR"]
        if joker_cards:
            swap_cards = [
                Card(suit=suit, rank=rank)
                for suit in GameState.LIST_SUIT
                for rank in ["A", "K"]
            ]
            for joker_card in joker_cards:
                # Tauschaktionen mit JOKER generieren
                for swap_card in swap_cards:
                    actions.append(
                        Action(
                            card=joker_card,
                            pos_from=None,
                            pos_to=None,
                            card_swap=swap_card,
                        )
                    )

        card_ranks = [card.rank for card in player.list_card]
        if any(rank in ["JKR", "A", "K"] for rank in card_ranks):
            marble_in_kennel_positions = [marble.pos for marble in marbles_in_kennel]
            for card in player.list_card:
                if card.rank in ["JKR", "A", "K"]:
                    actions.append(
                        Action(
                            card=card,
                            pos_from=min(marble_in_kennel_positions),
                            pos_to=start_position,
                        )
                    )

        return actions

    def _generate_joker_swap_actions(self, player: PlayerState) -> list[Action]:
        """generate all possible swap actions for JOKER"""

        actions = []
        joker_cards = [card for card in player.list_card if card.rank =="JKR"]

        if joker_cards:

            for joker_card in joker_cards:
                for suit in GameState.LIST_SUIT:
                    for rank in GameState.LIST_RANK[:-1]:
                        swap_card = Card(suit=suit, rank=rank)
                        actions.append(
                            Action(
                                card=joker_card,
                                pos_from=None,
                                pos_to=None,
                                card_swap=swap_card,
                            )
                        )
        return actions

    def _calculate_num_card(self, cnt_round: int) -> int:
        """Calculate the number of cards to deal based on the round number."""
        effective_round = (cnt_round - 1) % 5 + 1
        return max(6 - (effective_round - 1), 1)

    def _distribute_cards(self, num_cards: int) -> None:
        """Distribute a specific number of cards to each player."""
        player = self.state.list_player[self.state.idx_player_active]
        player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards)]

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        player = self.state.list_player[self.state.idx_player_active]

        if not self.state.bool_card_exchanged:
            self._exchange_cards(player, action)
            return None

        if action is None:
            return self._action_none(player)

        current_position = action.pos_from
        destination = action.pos_to
        marble_idx = self._get_marble_idx_from_position(player, current_position)
        if marble_idx < 0:
            raise ValueError("You don't have a marble at your specified position.")
        if destination is not None:
            player.list_marble[marble_idx].pos = destination
        if destination == StartNumbers[player.colour].value and current_position in KennelNumbers[player.colour].value:
            player.list_marble[marble_idx].is_save = True
        card_idx = self._get_card_idx_in_hand(player, action)
        if card_idx < 0:
            raise ValueError("You don't have a this card in Hand.")
        player.list_card.pop(card_idx)
        self._send_marble_home_if_possible(action, marble_idx, current_position, destination)

        return None

    def _action_none(self, player: PlayerState) -> None:
        if player.list_card: # Player has cards, but no action possible
            player.list_card = []
            return
        # Player has no cards (beginning of round)
        if all(not player.list_card for player in self.state.list_player): # all players have no cards
            self.state.cnt_round += 1
        num_cards = self._calculate_num_card(self.state.cnt_round)
        self._distribute_cards(num_cards)
        if all(player.list_card for player in self.state.list_player):
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        return


    def _exchange_cards(self, player: PlayerState, action: Action) -> None:
        idx_partner = (self.state.idx_player_active + 2) % self.state.cnt_player # identify partner-player
        partner = self.state.list_player[idx_partner]

        # Exchange the card
        if action is not None:
            player.list_card.remove(action.card)
            partner.list_card.append(action.card)

        # Move to next player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.bool_card_exchanged = True

    def _get_marble_idx_from_position(self, player: PlayerState, position: int | None) -> int:
        for i, marble in enumerate(player.list_marble):
            if marble.pos == position:
                return i
        return -1

    def _get_card_idx_in_hand(self, player: PlayerState, action: Action) -> int:
        for i, card in enumerate(player.list_card):
            if card.suit == action.card.suit and card.rank == action.card.rank:
                return i
        return -1

    def _send_marble_home_if_possible(
            self, action: Action, marble_idx: int, current_position: int | None, destination: int | None
        ) -> None:
        for i, player in enumerate(self.state.list_player):
            kennel_positions = KennelNumbers[player.colour].value
            for j, marble in enumerate(player.list_marble):
                if i == self.state.idx_player_active and j == marble_idx:
                    continue # skip the marble that was moved
                if action.card.rank == 7 and (current_position is not None and destination is not None):
                    if marble.pos > current_position and marble.pos < destination:
                        marble.pos = kennel_positions[0] # find smarter way to allocate marbles to kennel

                if marble.pos == destination:
                    marble.pos = kennel_positions[0]

    def _swap_marble():
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        player_view_state = self.state.model_copy()
        for i, player in enumerate(player_view_state.list_player):
            if i != idx_player:
                player.list_card = []
        return player_view_state



class RandomPlayer(Player):

    def random_public_method_to_satisfy_pylint(self) -> None:
        """ Random public method to satisfy pylint """
        return None

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()
