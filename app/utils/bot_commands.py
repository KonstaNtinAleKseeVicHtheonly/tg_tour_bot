from aiogram.types import BotCommand
from aiogram import Bot
from aiogram.types import BotCommandScopeDefault





async def set_public_commands(bot: Bot):
    """Установка команд меню видно всем ю=пользователям"""
    public_commands = [
        BotCommand(command="start", description="Посмотреть меню"),
        BotCommand(command="help", description="📖 О нас"),
        BotCommand(command="payment", description="🎯 Вариант оптлаты"),
        BotCommand(command="mybookings", description="📋 Вариант доставки"),
        BotCommand(command="profile", description="👤 Мой профиль"),
        BotCommand(command="contacts", description="📞 Контакты и поддержка"),
    ]
    await bot.set_my_commands(
        commands=public_commands,
        scope=BotCommandScopeDefault()  # Для всех пользователей
    )
async def delete_public_commands(bot:Bot):
    '''удаляет  общие команды видные юзерам'''
    await bot.delete_my_commands(scope=BotCommandScopeDefault())