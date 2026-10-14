from __future__ import annotations

import asyncio
import re
from urllib.parse import urlparse

import discord
from discord.ext import commands

from utils.cv2_compat import embed_to_view


class EmbedBuilderView(discord.ui.View):
    def __init__(self, ctx: commands.Context, embed: discord.Embed) -> None:
        super().__init__(timeout=180)
        self.ctx = ctx
        self.embed = embed
        self.message: discord.Message | None = None

        self.editor = discord.ui.Select(
            placeholder="Choose an embed part to edit",
            options=[
                discord.SelectOption(label="Title", value="title"),
                discord.SelectOption(label="Description", value="description"),
                discord.SelectOption(label="Add field", value="field"),
                discord.SelectOption(label="Color", value="color"),
                discord.SelectOption(label="Thumbnail URL", value="thumbnail"),
                discord.SelectOption(label="Image URL", value="image"),
                discord.SelectOption(label="Footer", value="footer"),
                discord.SelectOption(label="Author", value="author"),
            ],
        )
        self.editor.callback = self.edit_embed
        self.add_item(self.editor)

        send_button = discord.ui.Button(
            label="Send embed", style=discord.ButtonStyle.success
        )
        send_button.callback = self.send_embed
        self.add_item(send_button)

        cancel_button = discord.ui.Button(
            label="Cancel", style=discord.ButtonStyle.secondary
        )
        cancel_button.callback = self.cancel
        self.add_item(cancel_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "Only the owner who opened this embed builder can use it.",
            ephemeral=True,
        )
        return False

    async def _read_input(
        self, interaction: discord.Interaction, prompt: str
    ) -> discord.Message | None:
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.ctx.send(prompt)
        try:
            return await self.ctx.bot.wait_for(
                "message",
                timeout=60,
                check=lambda message: (
                    message.author.id == self.ctx.author.id
                    and message.channel.id == self.ctx.channel.id
                ),
            )
        except asyncio.TimeoutError:
            await interaction.followup.send("Timed out waiting for your reply.", ephemeral=True)
            return None

    async def edit_embed(self, interaction: discord.Interaction) -> None:
        selected = self.editor.values[0]
        prompts = {
            "title": "Send the embed title (up to 256 characters).",
            "description": "Send the embed description (up to 2000 characters).",
            "field": "Send the field name (up to 256 characters).",
            "color": "Send a 6-digit hex color, for example `#5865F2`.",
            "thumbnail": "Send a thumbnail image URL starting with http:// or https://.",
            "image": "Send an image URL starting with http:// or https://.",
            "footer": "Send the footer text.",
            "author": "Send the author text.",
        }
        response = await self._read_input(interaction, prompts[selected])
        if response is None:
            return

        value = response.content.strip()
        if selected == "field":
            field_value = await self._read_input(
                interaction, "Send the field value (up to 1024 characters)."
            )
            if field_value is None:
                return
            if not value or len(value) > 256 or not field_value.content.strip() or len(field_value.content) > 1024:
                await interaction.followup.send(
                    "Field name and value must fit Discord's limits.", ephemeral=True
                )
                return
            if len(self.embed.fields) >= 25:
                await interaction.followup.send(
                    "An embed can have at most 25 fields.", ephemeral=True
                )
                return
            self.embed.add_field(name=value, value=field_value.content.strip(), inline=False)
        elif selected == "title":
            if not value or len(value) > 256:
                await interaction.followup.send("Title must be 1-256 characters.", ephemeral=True)
                return
            self.embed.title = value
        elif selected == "description":
            if not value or len(value) > 4000:
                await interaction.followup.send("Description must be 1-4000 characters.", ephemeral=True)
                return
            self.embed.description = value
        elif selected == "color":
            if not re.fullmatch(r"#?[0-9a-fA-F]{6}", value):
                await interaction.followup.send("Use a valid 6-digit hex color.", ephemeral=True)
                return
            self.embed.color = discord.Color(int(value.removeprefix("#"), 16))
        elif selected in {"thumbnail", "image"}:
            parsed = urlparse(value)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                await interaction.followup.send("That is not a valid HTTP(S) URL.", ephemeral=True)
                return
            if selected == "thumbnail":
                self.embed.set_thumbnail(url=value)
            else:
                self.embed.set_image(url=value)
        elif selected == "footer":
            if not value or len(value) > 2048:
                await interaction.followup.send("Footer must be 1-2048 characters.", ephemeral=True)
                return
            self.embed.set_footer(text=value)
        elif selected == "author":
            if not value or len(value) > 256:
                await interaction.followup.send("Author must be 1-256 characters.", ephemeral=True)
                return
            self.embed.set_author(name=value)

        if self.message is not None:
            await self.message.edit(view=embed_to_view(self.embed, view=self))
        await interaction.followup.send("Embed updated.", ephemeral=True)

    async def send_embed(self, interaction: discord.Interaction) -> None:
        target = await self._read_input(
            interaction, "Mention the channel where you want to send this embed."
        )
        if target is None:
            return
        if not target.channel_mentions:
            await interaction.followup.send("Please mention a valid channel.", ephemeral=True)
            return

        channel = target.channel_mentions[0]
        if channel.guild.id != self.ctx.guild.id:
            await interaction.followup.send(
                "Choose a channel from this server.", ephemeral=True
            )
            return

        try:
            await channel.send(view=embed_to_view(self.embed))
        except (discord.Forbidden, discord.HTTPException):
            await interaction.followup.send(
                "I could not send the embed there. Check my channel permissions.",
                ephemeral=True,
            )
            return

        self.stop()
        await interaction.followup.send("Embed sent.", ephemeral=True)
        if self.message is not None:
            await self.message.delete()

    async def cancel(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.stop()
        if self.message is not None:
            await self.message.delete()

    async def on_timeout(self) -> None:
        if self.message is not None:
            try:
                await self.message.edit(view=embed_to_view(self.embed))
            except discord.HTTPException:
                pass


class EmbedBuilder(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="embed", aliases=["embedbuilder"])
    @commands.guild_only()
    @commands.is_owner()
    async def embed(self, ctx: commands.Context) -> None:
        embed = discord.Embed(title="New Embed", color=discord.Color.dark_theme())
        view = EmbedBuilderView(ctx, embed)
        view.message = await ctx.send(view=embed_to_view(embed, view=view))