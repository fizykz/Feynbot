"""Collection of constants, references, and collections used throughout the
bot for configuration."""


events_list: list[str] = [
    # Make sure to have set correct intents.
    # Connection & Debug
    "on_connect",
    "on_disconnect",
    "on_shard_connect",
    "on_shard_disconnect",
    "on_ready",
    "on_resumed",
    "on_shard_ready",
    "on_shard_resumed",
    "on_error",
    "on_socket_event_type",
    # Automod
    "on_automod_rule_create",
    "on_automod_rule_update",
    "on_automod_rule_delete",
    "on_automod_action",
    # Guilds
    "on_guild_available",
    "on_guild_unavailable",
    "on_guild_join",
    "on_guild_remove",
    "on_guild_update",
    "on_guild_emojis_update",
    "on_guild_stickers_update",
    "on_audit_log_entry_create",  # Object-unreliable
    "on_invite_create",  # (Rarely) Object-unreliable
    "on_invite_delete",  # (Rarely) Object-unreliable
    # Channels
    "on_guild_channel_create",
    "on_guild_channel_delete",
    "on_guild_channel_update",
    "on_guild_channel_pins_update",
    "on_private_channel_update",
    "on_private_channel_pins_update",
    "on_typing",
    # Voice
    "on_voice_state_update",
    # Members
    "on_member_join",
    "on_member_remove",
    "on_member_update",
    "on_user_update",
    "on_member_ban",
    "on_member_unban",
    "on_presence_update",
    # Commands
    "on_app_command_completion",
    "on_interaction",  # Low Level
    # Messages
    "on_message",
    "on_message_edit",
    "on_message_delete",
    "on_bulk_message_delete",
    # Reactions
    "on_reaction_add",
    "on_reaction_remove",
    "on_reaction_clear",
    "on_reaction_clear_emoji",
    # Roles
    "on_guild_role_create",
    "on_guild_role_delete",
    "on_guild_role_update",
    # Events
    "on_scheduled_event_create",
    "on_scheduled_event_delete",
    "on_scheduled_event_update",
    "on_scheduled_event_user_add",
    "on_scheduled_event_user_remove",
    # Stages
    "on_stage_instance_create",
    "on_stage_instance_delete",
    "on_stage_instance_update",
    # Threads
    "on_thread_create",
    "on_thread_join",
    "on_thread_update",
    "on_thread_remove",  # May not fire if not in thread.
    "on_thread_delete",
    "on_thread_member_join",
    "on_thread_member_remove",
    # Integrations
    "on_integration_create",
    "on_integration_update",
    "on_guild_integrations_update",
    "on_webhooks_update",
]
