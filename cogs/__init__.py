from __future__ import annotations
from core import Rem
from utils import console
import logging

from .commands.owner import Owner
from .events.owner_protection import OwnerProtection
from .events.react import React

from .antinuke.anti_member_update import AntiMemberUpdate
from .antinuke.antiban import AntiBan
from .antinuke.antibotadd import AntiBotAdd
from .antinuke.antichcr import AntiChannelCreate
from .antinuke.antichdl import AntiChannelDelete
from .antinuke.antichup import AntiChannelUpdate
from .antinuke.antieveryone import AntiEveryone
from .antinuke.antiguild import AntiGuildUpdate
from .antinuke.antiIntegration import AntiIntegration
from .antinuke.antikick import AntiKick
from .antinuke.antiprune import AntiPrune
from .antinuke.antirlcr import AntiRoleCreate
from .antinuke.antirldl import AntiRoleDelete
from .antinuke.antirlup import AntiRoleUpdate
from .antinuke.antiwebhook import AntiWebhookUpdate
from .antinuke.antiwebhookcr import AntiWebhookCreate
from .antinuke.antiwebhookdl import AntiWebhookDelete

from .automod.antispam import AntiSpam
from .automod.anticaps import AntiCaps
from .automod.antilink import AntiLink
from .automod.anti_invites import AntiInvite
from .automod.anti_mass_mention import AntiMassMention
from .automod.anti_emoji_spam import AntiEmojiSpam
from .automod.protected_users import ProtectedUsers

from .moderation.ban import Ban
from .moderation.unban import Unban
from .moderation.timeout import Mute
from .moderation.unmute import Unmute
from .moderation.kick import Kick
from .moderation.warn import Warn
from .moderation.role import Role
from .moderation.message import Message
from .moderation.moderation import Moderation
from .moderation.snipe import Snipe


log = logging.getLogger(__name__)


# Only keep the operational owner-control, moderation, and anti-abuse features
# that are required for the current deployment.
COGS_TO_LOAD = [
    Owner,
    OwnerProtection,
    React,
    Message,
    Moderation,
    Ban,
    Unban,
    Mute,
    Unmute,
    Kick,
    Warn,
    Role,
    Snipe,
    AntiSpam,
    AntiCaps,
    AntiInvite,
    AntiLink,
    AntiMassMention,
    AntiEmojiSpam,
    ProtectedUsers,
    AntiEveryone,
    AntiMemberUpdate,
    AntiBan,
    AntiBotAdd,
    AntiChannelCreate,
    AntiChannelDelete,
    AntiChannelUpdate,
    AntiGuildUpdate,
    AntiIntegration,
    AntiKick,
    AntiPrune,
    AntiRoleCreate,
    AntiRoleDelete,
    AntiRoleUpdate,
    AntiWebhookUpdate,
    AntiWebhookCreate,
    AntiWebhookDelete,
]


async def setup(bot: Rem):
    loaded_names: set[str] = set()
    timer = console.LoadTimer("COGS")
    total = len(COGS_TO_LOAD)
    console.section(f"Loading cogs ({total})")
    loaded_count = 0

    for cog_cls in COGS_TO_LOAD:
        cog = cog_cls(bot)
        name = cog.qualified_name
        if name in loaded_names or bot.get_cog(name):
            log.warning("Skipping duplicate cog: %s", name)
            console.warn(f"Skipped duplicate cog: {name}")
            continue

        await bot.add_cog(cog)
        loaded_names.add(name)
        loaded_count += 1
        console.cog_progress(name, index=loaded_count, total=total)
        log.debug("Loaded cog: %s", name)

    timer.finish(f"Loaded {loaded_count} cog(s)")
