from discord.ext import commands
from discord import app_commands
import dice

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='roll', description='Roll a dice!')
    @app_commands.describe(notation='Dice notation (e.g., 2d6, 1d20)')
    async def roll(self, interaction, notation: str):
        try:
            result = dice.roll(notation)
        except dice.DiceBaseException as e:
            await interaction.response.send_message(e.pretty_print())
            return

        if len(result) == 0:
            await interaction.response.send_message('Invalid dice notation. Please use a valid format like "2d6" or "1d20".')
            return
        elif len(result) == 1:
            await interaction.response.send_message(f'You rolled {result[0]}!')
        else:
            await interaction.response.send_message(f'You rolled {", ".join(map(str, result))} for a total of {sum(result)}!')

async def setup(bot):
    await bot.add_cog(Dice(bot=bot))