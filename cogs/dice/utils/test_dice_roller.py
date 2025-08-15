import pytest
import random
from cogs.dice.utils.dice_roller import DiceRoller

@pytest.fixture(autouse=True)
def set_seed():
    random.seed(12345)

def test_basic_roll():
    dr = DiceRoller()
    result = dr.roll('4d6')
    assert result['notation'] == '4d6'
    assert len(result['groups']) == 1
    group = result['groups'][0]
    assert group['notation'] == '4d6'
    assert len(group['rolls']) == 4
    assert all(1 <= r <= 6 for r in group['rolls'])
    assert group['multiplier'] == 1
    assert group['kept_rolls'] == group['rolls']
    assert group['subtotal'] == sum(group['rolls'])
    assert result['grand_total'] == group['subtotal']

def test_roll_with_modifier():
    dr = DiceRoller()
    result = dr.roll('4d6+10')
    assert len(result['groups']) == 2
    dice_group = result['groups'][0]
    mod_group = result['groups'][1]
    assert dice_group['notation'] == '4d6'
    assert mod_group['notation'] == '+10'
    assert mod_group['subtotal'] == 10
    assert result['grand_total'] == dice_group['subtotal'] + 10

def test_exploding_dice():
    dr = DiceRoller()
    result = dr.roll('2d6!')
    group = result['groups'][0]
    assert group['notation'] == '2d6!'
    # Rolls may be more than 2 if any roll is 6
    assert len(group['rolls']) >= 2
    assert all(1 <= r <= 6 for r in group['rolls'])
    assert group['kept_rolls'] == group['rolls']

def test_keep_highest():
    dr = DiceRoller()
    result = dr.roll('5d6kh2')
    group = result['groups'][0]
    assert group['notation'] == '5d6kh2'
    assert len(group['rolls']) == 5
    assert len(group['kept_rolls']) == 2
    assert group['kept_rolls'] == sorted(group['rolls'], reverse=True)[:2]
    assert group['subtotal'] == sum(group['kept_rolls'])

def test_keep_lowest():
    dr = DiceRoller()
    result = dr.roll('5d6kl2')
    group = result['groups'][0]
    assert group['notation'] == '5d6kl2'
    assert len(group['rolls']) == 5
    assert len(group['kept_rolls']) == 2
    assert group['kept_rolls'] == sorted(group['rolls'])[:2]
    assert group['subtotal'] == sum(group['kept_rolls'])

def test_multiplier():
    dr = DiceRoller()
    result = dr.roll('2d6*2')
    group = result['groups'][0]
    assert group['notation'] == '2d6'
    assert group['multiplier'] == 2
    assert group['subtotal'] == sum(group['rolls']) * 2

def test_multiple_groups():
    dr = DiceRoller()
    result = dr.roll('2d6+1d4')
    assert len(result['groups']) == 2
    g1, g2 = result['groups']
    assert g1['notation'] == '2d6'
    assert g2['notation'] == '1d4'
    assert result['grand_total'] == g1['subtotal'] + g2['subtotal']

def test_invalid_notation():
    dr = DiceRoller()
    with pytest.raises(ValueError):
        dr.roll('badnotation')
