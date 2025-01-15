import discord
from discord import ButtonStyle, Interaction
from discord.ui import Button, View
from mcstatus import JavaServer
from redbot.core import commands, app_commands

class confirm(View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Mark as resolved", style=ButtonStyle.danger, custom_id="ReportClose")
    async def confirm(self, interaction: discord.Interaction, button: discord.Button) -> None:
        try:
            if interaction.user.get_role(726137282104524871):
                newTags = interaction.channel.applied_tags
                resolved_tag_id = 1055496168509034497
                resolved_tag = interaction.guild.get_tag(resolved_tag_id)  # Fetch the tag object

                if resolved_tag not in newTags:
                    newTags.append(resolved_tag)

                await interaction.channel.edit(applied_tags=newTags)
                await interaction.response.edit_message(content="This thread has been marked as resolved", components=[]) 
                await interaction.channel.set_locked(True)
                await interaction.channel.set_archived(True)
            else:
                await interaction.response.send_message(content="You do not have permission to close this thread", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
        finally:
            self.value = True
            self.stop() 


class ticket(commands.Cog):
    """Custom Thread ticket system"""

    def __init__(self, bot):
        self.bot = bot
        self.ip = "mc.8bitcommunity.com"
        self.ports = {
            25565: "Proxy",
            25500: "Hub",
            25510: "Survival",
            25530: "Plotworld"
        }
        self.server_chat_id = 581520306984845324 

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        """Send a message and a button when a thread is created in the specified category."""

        tech_role_id = 726137282104524871  
        tech_support_category_id = 1054839141118001203  
        ping_tag_id = 1054839593947643984  #Tag for server crash to ping the server

        if thread.parent_id == tech_support_category_id:
            view = confirm()
            #await thread.send(f"<@&{tech_role_id}>")
            await thread.send("To close this click the button (tech only)", view=view)
            await view.wait()

            if view.value is None:
                print('Timeout')
            elif view.value:
                print('Confirmed')
            else:
                print('Cancelled')

            if ping_tag_id in thread.applied_tags:
                await thread.send("Thanks for creating a crash report, a tech staff will check on this as soon as possible")
                embed = Embed(title="Server Status", description="Crash Report", color=0x0099ff)
                for port, name in self.ports.items():
                    try:
                        server = JavaServer.lookup(f"{self.ip}:{port}")
                        status = await server.async_status()
                        embed.add_field(name=f"{name} Status", value="Online", inline=True)
                        embed.add_field(name=f"{name} Players", value=f"{status.players.online}/{status.players.max}", inline=True)
                        embed.add_field(name=f"{name} Ping", value=f"{status.latency} ms", inline=True)
                    except Exception as e:
                        embed.add_field(name=f"{name} Status", value="Offline", inline=True)
                        print(f"Error getting status for {name}: {e}")
                try:
                    channel = await self.bot.fetch_channel(self.server_chat_id)
                    topic = channel.topic
                    topic_array = topic.split("|")
                    if len(topic_array) == 4:
                        online_for = topic_array[2]
                        embed.add_field(name="Online For", value=online_for, inline=True)
                    else:
                        embed.add_field(name="Online For", value="Cant get data (Offline?)", inline=True)
                except Exception as e:
                    print(f"Error getting server chat topic: {e}")
                    embed.add_field(name="Online For", value="Cant get data (Offline?)", inline=True)
                embed.timestamp = thread.created_at
                await thread.send(embed=embed)
            else:
                await thread.send("Thanks for creating a bug report, a tech staff will check on this as soon as possible")

