#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة مساعدة للتعامل مع بادئات الأوامر
تُستخدم هذه الوحدة لاختيار البادئة المناسبة للأوامر المختلفة
"""

def get_prefix_for_command(command_name, config):
    """
    الحصول على البادئة المناسبة حسب نوع الأمر
    
    Args:
        command_name (str): اسم الأمر
        config (dict): قاموس التكوين
        
    Returns:
        str: البادئة المناسبة للأمر
    """
    prefix_config = config.get('prefix', {})
    commands_config = config.get('commands', {})
    
    if not prefix_config or not commands_config:
        return prefix_config.get('DEFAULT_PREFIX', '!')
    
    voice_commands = commands_config.get('voiceChannelCommands', [])
    game_commands = commands_config.get('gameCommands', [])
    
    if command_name in voice_commands:
        return prefix_config.get('VOICE_PREFIX', '-')
    elif command_name in game_commands:
        return prefix_config.get('GAMES_PREFIX', '!')
    else:
        return prefix_config.get('DEFAULT_PREFIX', '!')

def has_valid_prefix(message, config):
    """
    تحديد ما إذا كانت الرسالة تبدأ ببادئة صالحة
    
    Args:
        message (discord.Message): كائن رسالة Discord
        config (dict): قاموس التكوين
        
    Returns:
        bool: True إذا كانت الرسالة تبدأ ببادئة صالحة
    """
    prefix_config = config.get('prefix', {})
    
    default_prefix = prefix_config.get('DEFAULT_PREFIX', '!')
    voice_prefix = prefix_config.get('VOICE_PREFIX', '-')
    games_prefix = prefix_config.get('GAMES_PREFIX', '!')
    
    return (message.content.startswith(default_prefix) or 
            message.content.startswith(voice_prefix) or 
            message.content.startswith(games_prefix))

def get_used_prefix(message, config):
    """
    الحصول على البادئة المستخدمة في الرسالة
    
    Args:
        message (discord.Message): كائن رسالة Discord
        config (dict): قاموس التكوين
        
    Returns:
        str: البادئة المستخدمة في الرسالة، أو None إذا لم تبدأ الرسالة ببادئة صالحة
    """
    prefix_config = config.get('prefix', {})
    
    default_prefix = prefix_config.get('DEFAULT_PREFIX', '!')
    voice_prefix = prefix_config.get('VOICE_PREFIX', '-')
    games_prefix = prefix_config.get('GAMES_PREFIX', '!')
    
    if message.content.startswith(voice_prefix):
        return voice_prefix
    elif message.content.startswith(games_prefix):
        return games_prefix
    elif message.content.startswith(default_prefix):
        return default_prefix
    
    return None 