import pytest
from server.py.dog import (
    Dog,
    Card,
    Action,
    GamePhase,
    FinishNumbers,
)


def test_init():
    """Test initialization of the Dog class."""
    dog = Dog()
    state = dog.get_state()
    assert state.phase == GamePhase.RUNNING
    assert len(state.list_player) == 4
    assert len(state.list_player[0].list_card) == 6
    assert len(state.list_card_draw) > 0
    assert not state.bool_card_exchanged


def test_set_and_get_state():
    """Test setting and getting the state."""
    dog = Dog()
    original_state = dog.get_state()
    new_state = original_state.model_copy()
    new_state.cnt_round = 10
    dog.set_state(new_state)
    state = dog.get_state()
    assert state.cnt_round == 10


def test_print_state(capfd):
    """Test that print_state prints the state without error."""
    dog = Dog()
    dog.print_state()
    out, err = capfd.readouterr()
    assert "phase" in out
    assert err == ""


def test_unique_actions():
    """Test that _unique_actions returns unique actions."""
    dog = Dog()
    actions = [
        Action(card=dog.state.list_player[0].list_card[0]),
        Action(card=dog.state.list_player[0].list_card[0]),
    ]
    unique = dog._unique_actions(actions)
    assert len(unique) == 1


def test_get_list_action_before_exchange():
    """Test action list before card exchange is done."""
    dog = Dog()
    # Before card exchange is done, should only return exchange actions
    actions = dog.get_list_action()
    assert len(actions) > 0
    for action in actions:
        assert action.pos_from is None
        assert action.pos_to is None


def test_exchange_cards():
    """Test card exchange logic."""
    dog = Dog()
    player = dog.state.list_player[0]
    card_to_exchange = player.list_card[0]
    dog.apply_action(Action(card=card_to_exchange))
    # After first exchange, idx_player_active should move to next player
    assert dog.state.idx_player_active == 1


def test_actions_after_exchange():
    """Test actions after exchange is completed."""
    dog = Dog()
    # Complete all exchanges to set bool_card_exchanged = True
    for i in range(4):
        card_to_exchange = dog.state.list_player[dog.state.idx_player_active].list_card[
            0
        ]
        dog.apply_action(Action(card=card_to_exchange))

    # Now we can test normal movement actions
    actions = dog.get_list_action()
    # At least one action that involves moving a marble
    assert any(a.pos_from is not None and a.pos_to is not None for a in actions)


def test_apply_action_joker():
    """Test applying a Joker action."""
    dog = Dog()
    # Force a Joker card into player's hand for testing
    player = dog.state.list_player[0]
    joker = Card(suit="", rank="JKR")
    num_jokers_before_adding = len([card for card in player.list_card if card.rank == "JKR"])
    player.list_card.append(joker)

    # Perform a joker action to swap it for an A♠ card
    action = Action(card=joker, card_swap=Card(suit="♠", rank="A"))
    dog.apply_action(action)

    # card_active should now be A♠
    assert dog.state.card_active is None
    assert len([card for card in player.list_card if card.rank == "JKR"]) == num_jokers_before_adding


def test_apply_action_seven():
    """Test applying a 7 card action (partial movement)."""
    dog = Dog()
    # Complete exchanges
    for i in range(4):
        card_to_exchange = dog.state.list_player[dog.state.idx_player_active].list_card[
            0
        ]
        dog.apply_action(Action(card=card_to_exchange))

    player = dog.state.list_player[dog.state.idx_player_active]
    # Ensure player has a '7' card
    seven_card = None
    for c in player.list_card:
        if c.rank == "7":
            seven_card = c
            break
    if seven_card is None:
        # If not found, just pick a known card from player's hand for demonstration:
        player.list_card.append(Card(suit="♠", rank="7"))
        seven_card = player.list_card[-1]

    marble = player.list_marble[0]
    start_pos = marble.pos

    # Apply a partial move with 7
    dog.apply_action(
        Action(card=seven_card, pos_from=start_pos, pos_to=(start_pos + 3) % 64)
    )
    # Check that card_active is still '7' (because steps remain)
    assert dog.state.card_active.rank == "7"
    # Apply remaining steps
    dog.apply_action(
        Action(
            card=seven_card, pos_from=(start_pos + 3) % 64, pos_to=(start_pos + 7) % 64
        )
    )
    # Now the '7' action should be completed and card_active should be None
    assert dog.state.card_active is None


def test_action_none():
    """Test applying None action (skip move)."""
    dog = Dog()
    dog.apply_action(None)
    # If no cards were drawn, player should now have no cards and next player active
    assert dog.state.idx_player_active == 1


def test_finish_game():
    """Test finishing the game when marbles are in finish positions."""
    dog = Dog()
    # Put BLUE marbles into finish position
    finish_positions = FinishNumbers["BLUE"].value
    for i, marble in enumerate(dog.state.list_player[0].list_marble):
        marble.pos = finish_positions[i]

    # Trigger finish logic
    dog._finish_game()
    assert dog.state.list_player[0].finished is True
    # If partner is also finished, phase would be finished. Let's force that:
    finish_positions_red = FinishNumbers["RED"].value
    for i, marble in enumerate(dog.state.list_player[2].list_marble):
        marble.pos = finish_positions_red[i]

    dog._finish_game()
    assert dog.state.phase == GamePhase.FINISHED


def test_error_no_card_in_hand():
    """Test error when action card not in player's hand."""
    dog = Dog()
    # Complete exchanges first
    for _ in range(4):
        card_to_exchange = dog.state.list_player[dog.state.idx_player_active].list_card[
            0
        ]
        dog.apply_action(Action(card=card_to_exchange))

    # Try to apply action with a card player does not have
    player = dog.state.list_player[dog.state.idx_player_active]
    fake_card = Card(suit="♠", rank="Z")  # Non-existent rank
    with pytest.raises(ValueError):
        dog.apply_action(Action(card=fake_card, pos_from=0, pos_to=10))


def test_error_no_marble_at_position():
    """Test error when no marble at given pos_from."""
    dog = Dog()
    # Complete exchanges
    for _ in range(4):
        card_to_exchange = dog.state.list_player[dog.state.idx_player_active].list_card[
            0
        ]
        dog.apply_action(Action(card=card_to_exchange))

    player = dog.state.list_player[dog.state.idx_player_active]
    # Use a known card
    test_card = player.list_card[0]
    with pytest.raises(ValueError):
        # Use a position not occupied by the player's marble
        dog.apply_action(Action(card=test_card, pos_from=999, pos_to=0))


def test_get_player_view():
    """Test the masked player view."""
    dog = Dog()
    player_view = dog.get_player_view(0)
    # Player 0 sees their own cards
    assert len(player_view.list_player[0].list_card) == 6
    # Other players' cards are masked
    assert len(player_view.list_player[1].list_card) == 0
    assert len(player_view.list_player[2].list_card) == 0
    assert len(player_view.list_player[3].list_card) == 0
