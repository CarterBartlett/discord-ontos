import random
import re

class DiceRoller:
    def roll(self, notation: str):
        """
        Rolls dice based on advanced dice notation.
        Supports:
        - 4d6
        - 4d6*2
        - 4d6kh1
        - 4d6kl1
        - 4d6!
        - d20
        - 1d8+4
        - 2d20+1d4
        - 4dF (fudge dice)
        """
        expr = notation.replace(' ', '')
        # Split into dice groups and modifiers, but keep multipliers attached
        group_regex = r'([+-]?\d*d\d+!?k?[hl]?\d*(?:\*\d+)?|[+-]?\d*dF(?:!|k[hl]?\d*)?(?:\*\d+)?|[+-]\d+)'  # Support fudge dice and modifiers
        groups = re.findall(group_regex, expr)
        results = []
        grand_total = 0
        for group in groups:
            # Remove leading '+' from dice groups
            if group.startswith('+') and 'd' in group:
                group = group[1:]
            # Parse multiplier
            mult_match = re.search(r'(.*)\*(\d+)$', group)
            if mult_match:
                dice_part = mult_match.group(1)
                multiplier = int(mult_match.group(2))
            else:
                dice_part = group
                multiplier = 1
            # Fudge dice support
            fudge_match = re.fullmatch(r'([+-]?)(\d*)dF((!|k[hl]?\d*)?)', dice_part)
            if fudge_match:
                sign = -1 if fudge_match.group(1) == '-' else 1
                num_dice = int(fudge_match.group(2)) if fudge_match.group(2) else 1
                fudge_opts = fudge_match.group(3)
                # Fudge dice: each die is -1, 0, or +1
                rolls = [random.choice([-1, 0, 1]) for _ in range(num_dice)]
                kept_rolls = rolls
                removed_rolls = []
                # Support keep highest/lowest for fudge dice
                keep_type = None
                keep_num = None
                if fudge_opts:
                    keep_match = re.match(r'k(h|l)?(\d+)', fudge_opts)
                    if keep_match:
                        keep_type = 'kh' if keep_match.group(1) == 'h' or keep_match.group(1) is None else 'kl'
                        keep_num = int(keep_match.group(2))
                if keep_type and keep_num:
                    if keep_type == 'kh':
                        sorted_rolls = sorted(rolls, reverse=True)
                        kept_rolls = sorted_rolls[:keep_num]
                        removed_rolls = sorted_rolls[keep_num:]
                    elif keep_type == 'kl':
                        sorted_rolls = sorted(rolls)
                        kept_rolls = sorted_rolls[:keep_num]
                        removed_rolls = sorted_rolls[keep_num:]
                subtotal = sum(kept_rolls) * multiplier * sign
                results.append({
                    'notation': dice_part,
                    'rolls': rolls,
                    'kept_rolls': kept_rolls,
                    'removed_rolls': removed_rolls,
                    'multiplier': multiplier,
                    'subtotal': subtotal
                })
                grand_total += subtotal
            else:
                # Parse regular dice
                dice_match = re.fullmatch(r'([+-]?)(\d*)d(\d+)(!?)((kh|kl|k)(\d+))?', dice_part)
                if dice_match:
                    sign = -1 if dice_match.group(1) == '-' else 1
                    num_dice = int(dice_match.group(2)) if dice_match.group(2) else 1
                    num_sides = int(dice_match.group(3))
                    explode = bool(dice_match.group(4))
                    keep_type = dice_match.group(6)
                    keep_num = int(dice_match.group(7)) if dice_match.group(7) else None
                    rolls = []
                    for _ in range(num_dice):
                        roll = random.randint(1, num_sides)
                        if explode:
                            temp = [roll]
                            while roll == num_sides:
                                roll = random.randint(1, num_sides)
                                temp.append(roll)
                            rolls.extend(temp)
                        else:
                            rolls.append(roll)
                    kept_rolls = rolls
                    removed_rolls = []
                    if keep_type and keep_num:
                        if keep_type in ['kh', 'k']:
                            sorted_rolls = sorted(rolls, reverse=True)
                            kept_rolls = sorted_rolls[:keep_num]
                            removed_rolls = sorted_rolls[keep_num:]
                        elif keep_type == 'kl':
                            sorted_rolls = sorted(rolls)
                            kept_rolls = sorted_rolls[:keep_num]
                            removed_rolls = sorted_rolls[keep_num:]
                    subtotal = sum(kept_rolls) * multiplier * sign
                    results.append({
                        'notation': dice_part,
                        'rolls': rolls,
                        'kept_rolls': kept_rolls,
                        'removed_rolls': removed_rolls,
                        'multiplier': multiplier,
                        'subtotal': subtotal
                    })
                    grand_total += subtotal
            # Modifier only (e.g., +4)
            mod_match = re.fullmatch(r'([+-]\d+)', group)
            if mod_match:
                mod = int(mod_match.group(1))
                results.append({
                    'notation': group,
                    'rolls': [],
                    'kept_rolls': [],
                    'removed_rolls': [],
                    'multiplier': 1,
                    'subtotal': mod
                })
                grand_total += mod
            elif not (fudge_match or dice_match):
                # If not a dice group or modifier, raise error
                raise ValueError(f"Invalid dice group: {group}")
        if not results:
            raise ValueError(f"Invalid dice notation: {notation}")
        return {
            'notation': notation,
            'groups': results,
            'grand_total': grand_total
        }
