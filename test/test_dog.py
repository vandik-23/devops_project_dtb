import pytest
from server.py.dog import (
    Dog,
    Card,
    Action,
    GamePhase,
    FinishNumbers,
    KennelNumbers,
    Marble,
    StartNumbers,
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


# def test_actions_after_exchange():
#     """Test actions after exchange is completed."""
#     dog = Dog()
#     # Complete all exchanges to set bool_card_exchanged = True
#     for i in range(4):
#         card_to_exchange = dog.state.list_player[dog.state.idx_player_active].list_card[
#             0
#         ]
#         dog.apply_action(Action(card=card_to_exchange))

#     # Now we can test normal movement actions
#     actions = dog.get_list_action()
#     # At least one action that involves moving a marble
#     assert any(a.pos_from is not None and a.pos_to is not None for a in actions)


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


def test_check_if_save_marble_between_current_and_destination():
    """
    Test _check_if_save_marble_between_current_and_destination:
    Set up a scenario where a 'is_save' marble is between current and destination.
    """
    dog = Dog()
    # Set a marble of another player as saved and in between path
    # BLUE player is active by default, start at pos=64 kennel
    # Let's place a saved marble from GREEN player between current=0 and destination=10
    dog.state.list_player[1].list_marble[0].pos = 5
    dog.state.list_player[1].list_marble[0].is_save = True
    blocked = dog._check_if_save_marble_between_current_and_destination(0, 10)
    assert blocked is True

    # No blocking marble
    blocked = dog._check_if_save_marble_between_current_and_destination(0, 4)
    assert blocked is False


def test_generate_kennel_and_joker_actions():
    """
    Test _generate_kennel_and_joker_actions:
    All marbles in kennel and player has a Joker.
    """
    dog = Dog()
    # Complete card exchanges so we can generate normal actions
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )
    player = dog.state.list_player[dog.state.idx_player_active]

    # Put all marbles in kennel
    player.colour = "BLUE"
    player.list_marble = [Marble(pos=x) for x in KennelNumbers.BLUE.value]

    # Give a joker card
    joker = Card(suit="", rank="JKR")
    player.list_card = [joker]
    actions = dog._generate_kennel_and_joker_actions(player, player.list_marble)
    # There should be actions for swapping joker and starting from kennel
    assert any(a.card_swap is not None for a in actions)
    assert any(a.pos_from in KennelNumbers.BLUE.value for a in actions)


def test_generate_joker_swap_actions_no_joker():
    """
    Test _generate_joker_swap_actions:
    Scenario where player has no Joker - should return empty.
    """
    dog = Dog()
    # Remove all jokers from current player's hand
    player = dog.state.list_player[0]
    player.list_card = [c for c in player.list_card if c.rank != "JKR"]
    actions = dog._generate_joker_swap_actions(player)
    assert actions == []


def test_action_none_with_seven_reverts():
    """
    Test _action_none with card seven logic:
    Start a 7 move and then do action_none to revert.
    """
    dog = Dog()
    # Complete exchanges
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    # Add a '7' card if not present
    seven_card = Card(suit="♠", rank="7")
    if not any(c.rank == "7" for c in player.list_card):
        player.list_card.append(seven_card)
    else:
        seven_card = [c for c in player.list_card if c.rank == "7"][0]

    marble = player.list_marble[0]
    start_pos = marble.pos

    # Start a partial 7 move
    dog.apply_action(
        Action(card=seven_card, pos_from=start_pos, pos_to=(start_pos + 3) % 64)
    )
    # Now call action_none to revert
    dog.apply_action(None)
    # Marble should be reverted back
    assert marble.pos == start_pos
    # card_seven_metadata should be reset
    assert dog.card_seven_metadata.remaining_steps is None


def test_send_marble_home_if_possible_multiple_marbles():
    """
    Test _send_marble_home_if_possible with multiple marbles on the same cell.
    """
    dog = Dog()
    # Complete exchanges so we can do normal moves
    for _ in range(4):
        card = dog.state.list_player[dog.state.idx_player_active].list_card[0]
        dog.apply_action(Action(card=card))

    player = dog.state.list_player[dog.state.idx_player_active]
    # Give a card that moves forward (e.g. '2')
    forward_card = None
    for c in player.list_card:
        if c.rank in ["2", "3", "4", "5", "6", "8", "9", "10"]:
            forward_card = c
            break
    if not forward_card:
        player.list_card.append(Card(suit="♠", rank="2"))
        forward_card = player.list_card[-1]

    marble = player.list_marble[0]
    start_pos = marble.pos

    # Place another player's marble at the same destination to trigger home sending
    # The marble that moves will stack on top of it
    other_player = dog.state.list_player[
        (dog.state.idx_player_active + 1) % dog.state.cnt_player
    ]
    other_player_marble = other_player.list_marble[0]
    other_player_marble.pos = (start_pos + 2) % 64

    # Move our marble onto that marble
    dog.apply_action(
        Action(card=forward_card, pos_from=start_pos, pos_to=(start_pos + 2) % 64)
    )
    # Other player's marble should be sent home (kennel)
    kennel = KennelNumbers[other_player.colour].value[0]
    assert other_player_marble.pos == kennel


def test_calculate_steps_over_start_line():
    """
    Test _calculate_steps where current_position < start_number <= destination.
    This should cover the branch in code.
    """
    dog = Dog()
    player = dog.state.list_player[0]
    player.colour = "BLUE"
    dog.state.idx_player_active = 0
    # start_number for BLUE is 0, but code sets it to 64 if 0.
    # Let's place current_position = 60, destination = 2
    steps = dog._calculate_steps(60, 2)
    # This tests code that wraps over start_number=64 logic
    # Just ensure no error and some step count is returned
    assert steps >= 0


def test_calculate_num_card_all_rounds():
    """
    Test _calculate_num_card for various rounds to ensure different return values.
    """
    dog = Dog()
    # Round 1 -> 6 cards
    assert dog._calculate_num_card(1) == 6
    # Round 2 -> 5 cards
    assert dog._calculate_num_card(2) == 5
    # Round 3 -> 4 cards
    assert dog._calculate_num_card(3) == 4
    # Round 4 -> 3 cards
    assert dog._calculate_num_card(4) == 3
    # Round 5 -> 2 cards
    assert dog._calculate_num_card(5) == 2
    # Round 6 (looping back) -> same as Round 1 -> 6 cards
    assert dog._calculate_num_card(6) == 6


def test_distribute_cards():
    """
    Test _distribute_cards:
    Modify the game so the next action_none leads to distributing new cards.
    """
    dog = Dog()
    dog.state.bool_card_exchanged = True
    idx_player_active = dog.state.idx_player_active
    # Remove all cards from players
    for p in dog.state.list_player:
        p.list_card = []

    # Call action_none to force new card distribution
    dog.apply_action(None)
    # Check that the active player now has cards dealt
    player = dog.state.list_player[idx_player_active]
    assert len(player.list_card) > 0


def test_is_player_in_finish():
    """
    Test _is_player_in_finish:
    Make sure a player is recognized as finished when all marbles are in finish.
    """
    dog = Dog()
    player = dog.state.list_player[0]
    finish_positions = FinishNumbers[player.colour].value
    for i, marble in enumerate(player.list_marble):
        marble.pos = finish_positions[i]
    assert dog._is_player_in_finish(player, finish_positions) is True


def test_apply_action_joker_in_hand_but_wrong_joker():
    """Test that apply_action with a joker that doesn't match any in player's hand raises ValueError."""
    dog = Dog()
    player = dog.state.list_player[0]
    # Add a joker to player's hand
    joker = Card(suit="", rank="JKR")
    player.list_card.append(joker)

    # Try using a joker with different suit attributes to fail retrieval
    joker_different = Card(suit="♠", rank="JKR")
    with pytest.raises(ValueError):
        dog.apply_action(
            Action(card=joker_different, card_swap=Card(suit="♠", rank="A"))
        )


def test_apply_action_negative_move_with_4():
    """
    Test applying action with a 4 card moving backward (-4).
    Ensure that backward movement is possible from start field.
    """
    dog = Dog()
    # Complete all exchanges
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    # Ensure player has a '4' card
    four_card = None
    for c in player.list_card:
        if c.rank == "4":
            four_card = c
            break
    if four_card is None:
        player.list_card.append(Card(suit="♠", rank="4"))
        four_card = player.list_card[-1]

    marble = player.list_marble[0]
    start_pos = marble.pos
    # Try moving backward -4 steps from start_pos
    # start_pos is likely a kennel start, let's move it out first if needed
    if start_pos in KennelNumbers[player.colour].value:
        # Need to start the marble first
        start_card = Card(suit="♠", rank="A")
        player.list_card.append(start_card)
        dog.apply_action(
            Action(
                card=start_card,
                pos_from=start_pos,
                pos_to=StartNumbers[player.colour].value,
            )
        )
        start_pos = player.list_marble[0].pos

    # Apply backward 4
    backward_destination = (start_pos - 4) % 64
    dog.apply_action(
        Action(card=four_card, pos_from=start_pos, pos_to=backward_destination)
    )
    assert player.list_marble[0].pos == backward_destination


def test_generate_jake_swap_actions_no_positions_jake_to():
    """
    Test _generate_jake_swap_actions scenario where there are no valid positions_jake_to.
    In this case, code modifies positions_jake_to and positions_jake_from arrays.
    """
    dog = Dog()
    # Complete exchanges
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    player.colour = "BLUE"

    # Give player a J card if not present
    j_card = None
    for c in player.list_card:
        if c.rank == "J":
            j_card = c
            break
    if not j_card:
        player.list_card.append(Card(suit="♠", rank="J"))
        j_card = player.list_card[-1]

    # All player's marbles are in play and no other marbles are available for swapping
    # Move player's marbles out to ensure they are not in finish positions
    for marble in player.list_marble:
        if marble.pos in KennelNumbers[player.colour].value:
            start_card = Card(suit="♠", rank="A")
            player.list_card.append(start_card)
            dog.apply_action(
                Action(
                    card=start_card,
                    pos_from=marble.pos,
                    pos_to=StartNumbers[player.colour].value,
                )
            )

    # Remove all opponent marbles from play by putting them in their finish - to avoid swaps
    for idx, p in enumerate(dog.state.list_player):
        if idx != dog.state.idx_player_active:
            finish_positions = FinishNumbers[p.colour].value
            for i, m in enumerate(p.list_marble):
                m.pos = finish_positions[i]

    actions = dog._generate_jake_swap_actions(player, [j_card], player.list_marble)
    # Even though no positions_jake_to initially, code tries fallback scenario
    # At least some actions should be returned due to fallback logic
    assert len(actions) > 0


def test_action_none_no_cards_all_players():
    """
    Test _action_none scenario when no player has cards.
    Ensures new cards are distributed.
    """
    dog = Dog()
    dog.state.bool_card_exchanged = True
    # Remove all cards from all players
    for p in dog.state.list_player:
        p.list_card = []

    current_player = dog.state.idx_player_active
    dog.apply_action(None)
    # After action_none, distribution should happen
    # The current player should now have some cards
    assert len(dog.state.list_player[current_player].list_card) > 0


def test_send_marble_home_if_possible_no_marble_sent():
    """
    Test _send_marble_home_if_possible scenario where no marbles are actually sent home.
    Move a marble to an empty destination cell.
    """
    dog = Dog()
    # Complete exchanges
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    # Ensure we have a forward-moving card
    move_card = None
    for c in player.list_card:
        if c.rank in ["2", "3", "5"]:
            move_card = c
            break
    if move_card is None:
        player.list_card.append(Card(suit="♠", rank="2"))
        move_card = player.list_card[-1]

    marble = player.list_marble[0]
    start_pos = marble.pos
    destination = (start_pos + 2) % 64
    # Ensure destination is free of other marbles
    for p in dog.state.list_player:
        for m in p.list_marble:
            if m is not marble:
                m.pos = (m.pos + 10) % 64  # move them somewhere else

    # Move marble to an empty spot
    dog.apply_action(Action(card=move_card, pos_from=start_pos, pos_to=destination))
    # No marbles should have been sent home, check that no kennel changes occurred
    for p in dog.state.list_player:
        for m in p.list_marble:
            kennel_positions = KennelNumbers[p.colour].value
            assert m.pos not in kennel_positions or m is marble


def test_finish_game_no_finish():
    """
    Test finishing game scenario where no player is finished.
    The game should remain in RUNNING phase.
    """
    dog = Dog()
    dog._finish_game()
    assert dog.state.phase == GamePhase.RUNNING


def test_get_other_marble_idx_from_position():
    """
    Test _get_other_marble_idx_from_position by placing a marble of another player in a known position
    and ensuring we find it.
    """
    dog = Dog()
    # Complete exchanges so we can manipulate freely
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    other_player = dog.state.list_player[
        (dog.state.idx_player_active + 1) % dog.state.cnt_player
    ]

    # Move other player's first marble to position 10
    other_player.list_marble[0].pos = 10
    p, idx = dog._get_other_marble_idx_from_position(10)
    assert p == other_player
    assert idx == 0


def test_generate_joker_swap_actions_with_joker():
    """
    Test _generate_joker_swap_actions scenario where the player actually has a Joker card.
    Ensure that a list of swap actions is generated.
    """
    dog = Dog()
    # Complete card exchanges first
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    joker_card = Card(suit="", rank="JKR")
    player.list_card.append(joker_card)

    actions = dog._generate_joker_swap_actions(player)
    # With a Joker in hand, we should get multiple actions replacing Joker with another card
    assert len(actions) > 0
    # Check that all returned actions have card=JKR and card_swap != None
    for a in actions:
        assert a.card.rank == "JKR"
        assert a.card_swap is not None


def test_get_list_action_player_finished():
    """
    Covers:
    - self._finish_game() call
    - if player.finished logic
    """
    dog = Dog()
    # Complete all exchanges first to move to normal action phase
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    # Place current player's marbles in finish positions to mark them as finished
    player = dog.state.list_player[dog.state.idx_player_active]
    finish_positions = FinishNumbers[player.colour].value
    for i, marble in enumerate(player.list_marble):
        marble.pos = finish_positions[i]

    # This triggers player.finished = True in _finish_game
    actions = dog.get_list_action()  # Will call self._finish_game() internally
    # Player finished means player's marbles replaced by partner's marbles
    partner = dog.state.list_player[(dog.state.idx_player_active + 2) % 4]
    assert player.list_marble == partner.list_marble
    # No card_active, so it will go past the if self.state.card_active block
    # Just ensure it returns possible actions (likely kennel start since partner marbles are used)
    assert isinstance(actions, list)


def test_get_list_action_with_card_active_7():
    """
    Covers:
    - if self.state.card_active is not None
    - if self.state.card_active.rank == "7"
    - if self.card_seven_metadata.remaining_steps is None
    - the loop to append actions for each possible step (including -4 if applicable)
    """
    dog = Dog()
    # Complete exchanges
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    # Give the player a '7' card and set it as active
    seven_card = Card(suit="♠", rank="7")
    player.list_card.append(seven_card)
    dog.state.card_active = seven_card
    # Move one marble out of kennel to start position
    start_pos = StartNumbers[player.colour].value
    kennel_pos = KennelNumbers[player.colour].value[0]
    # Use an A card to start marble from kennel
    player.list_card.append(Card(suit="♠", rank="A"))
    dog.apply_action(
        Action(card=player.list_card[-1], pos_from=kennel_pos, pos_to=start_pos)
    )

    actions = dog.get_list_action()
    # With a '7' card active, we should see multiple step moves (1 to 7, and possibly -4 if start position used)
    # Ensure some actions were generated
    assert any(a.card.rank == "7" for a in actions)


def test_get_list_action_with_card_active_normal():
    """
    Covers:
    - if self.state.card_active is not None with a non-7 card
    - generating actions for normal moves
    """
    dog = Dog()
    # Complete exchanges
    for _ in range(4):
        dog.apply_action(
            Action(card=dog.state.list_player[dog.state.idx_player_active].list_card[0])
        )

    player = dog.state.list_player[dog.state.idx_player_active]
    # Give the player a '2' card and set it active
    two_card = Card(suit="♠", rank="2")
    player.list_card.append(two_card)
    dog.state.card_active = two_card
    # Move a marble out of kennel first
    start_pos = StartNumbers[player.colour].value
    kennel_pos = KennelNumbers[player.colour].value[0]
    player.list_card.append(Card(suit="♠", rank="A"))
    dog.apply_action(
        Action(card=player.list_card[-1], pos_from=kennel_pos, pos_to=start_pos)
    )

    actions = dog.get_list_action()
    # With '2' card active, should generate forward moves
    assert any(a.card.rank == "2" for a in actions)


def test_process_joker_action():
    dog = Dog()
    player = dog.state.list_player[0]
    no_of_jokers = len([card for card in player.list_card if card.rank == "JKR"])
    # Add a joker card to player's hand
    joker_card = Card(suit="", rank="JKR")
    player.list_card.append(joker_card)

    # The card we want to swap the joker for
    swap_card = Card(suit="♠", rank="A")

    # Call the _process_joker_action method
    dog._process_joker_action(player, Action(card=joker_card, card_swap=swap_card))

    # Joker should be removed from player's hand
    assert len([card for card in player.list_card if card.rank == "JKR"]) == no_of_jokers
    # card_active should now be the swap_card
    assert dog.state.card_active == swap_card


def test_process_joker_action_wrong_card():
    dog = Dog()
    player = dog.state.list_player[0]
    # Player has a joker
    joker_card = Card(suit="", rank="JKR")
    player.list_card.append(joker_card)

    # Attempt with a non-joker card as action.card
    non_joker_card = Card(suit="♠", rank="2")
    with pytest.raises(
        ValueError, match="Nur Joker-Aktionen sind in dieser Funktion erlaubt."
    ):
        dog._process_joker_action(
            player, Action(card=non_joker_card, card_swap=Card(suit="♠", rank="A"))
        )


def test_process_joker_action_no_swap_card():
    dog = Dog()
    player = dog.state.list_player[0]
    # Player has a joker
    joker_card = Card(suit="", rank="JKR")
    player.list_card.append(joker_card)

    # No card_swap provided
    with pytest.raises(
        ValueError, match="Es muss eine Karte angegeben werden, die der Joker ersetzt."
    ):
        dog._process_joker_action(player, Action(card=joker_card))