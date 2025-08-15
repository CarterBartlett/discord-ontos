from discord.ext import commands
from discord import app_commands
from cogs.dice.utils.dice_roller import DiceRoller

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='roll', description='Roll a dice!')
    @app_commands.describe(
        notation='Dice notation (e.g., 2d6, 1d20)',
        whisper='Send result privately (default: False)'
    )
    async def roll(self, interaction, notation: str, whisper: bool = False):
        roller = DiceRoller()
        try:
            result = roller.roll(notation)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=whisper)
            return

        breakdowns = []
        for group in result['groups']:
            # Markdown formatting: strikethrough unused rolls
            if group['rolls']:
                rolls = group['rolls'][:]
                kept = group['kept_rolls'][:]
                roll_display = []
                for r in rolls:
                    if r in kept:
                        roll_display.append(f"**{r}**")
                        kept.remove(r)  # Remove one instance to handle duplicates
                    else:
                        roll_display.append(f"~~{r}~~")
                rolls_str = ', '.join(roll_display)
                breakdowns.append(f"**{group['notation']}**: [{rolls_str}]  \nSubtotal: **{group['subtotal']}**")
            else:
                breakdowns.append(f"**{group['notation']}**  \nSubtotal: **{group['subtotal']}**")

        msg = '\n'.join(breakdowns)
        msg += f"\n\n**Total:** __{result['grand_total']}__"
        await interaction.response.send_message(msg, ephemeral=whisper)

async def setup(bot):
    await bot.add_cog(Dice(bot=bot))