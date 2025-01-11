# paginator.py

import discord

class CryptoPaginator(discord.ui.View):
    def __init__(self, cryptos, per_page=15):
        # Adjust per_page to be a multiple of 3 since we want 3 columns
        super().__init__(timeout=None) # No timeout for the buttons
        self.cryptos = cryptos
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(cryptos) + per_page - 1) // per_page

        # Disable previous button initially if we're on the first page
        self.previous_page.disabled = True

        # Disable next button if only one page
        if self.total_pages == 1:
            self.next_page.disabled = True

    # Function to create the embed for the current page
    def create_embed(self):
        embed = discord.Embed(title="Available Cryptocurrencies", color=0x00A300)
        start_index = self.current_page * self.per_page
        end_index = start_index + self.per_page
        cryptos_on_page = self.cryptos[start_index:end_index]

        # Adding fields in three columns
        for i, crypto in enumerate(cryptos_on_page):
            # Add fields in 3 columns by checking the position
            embed.add_field(
                name=f"{crypto['name']} ({crypto['symbol'].upper()})", 
                value=f"ID: {crypto['id']}", 
                inline=True # Inline True to make them side by side
            )
        
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        return embed

    # Next button interaction
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        
        # Enable the previous button since we're no longer on the first page
        self.previous_page.disabled = False
        
        # Disable next button if we reach the last page
        if self.current_page == self.total_pages - 1:
            button.disabled = True

        # Update the message with the new embed
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    # Previous button interaction
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        
        # Enable the next button since we're no longer on the last page
        self.next_page.disabled = False
        
        # Disable previous button if we're back on the first page
        if self.current_page == 0:
            button.disabled = True

        # Update the message with the new embed
        await interaction.response.edit_message(embed=self.create_embed(), view=self)