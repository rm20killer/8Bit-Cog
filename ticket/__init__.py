from .ticket import ticket


async def setup(bot):
    await bot.add_cog(ticket(bot))