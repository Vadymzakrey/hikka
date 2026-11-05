import asyncio
import logging
from datetime import datetime
import pytz
from telethon.tl.functions.account import UpdateProfileRequest
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class KyivTimeNickMod(loader.Module):
    """Автоматически меняет время в никнейме (поддерживает Киевское время)"""
    strings = {
        "name": "KyivTimeNick", 
        "started": "⏳ Авто-время по Киеву запущено!", 
        "stopped": "🛑 Авто-время остановлено."
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "FORMAT", "fl | {time}", "Формат никнейма. Использовать {time} для времени.",
            "TIMEZONE", "Europe/Kyiv", "Твой часовой пояс."
        )
        self.active = False

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def timenick(self, message):
        """Запустить или остановить циклическую смену времени в нике"""
        if self.active:
            self.active = False
            await utils.answer(message, self.strings["stopped"])
        else:
            self.active = True
            await utils.answer(message, self.strings["started"])
            self.bot.loop.create_task(self.time_loop())

    async def time_loop(self):
        while self.active:
            try:
                tz = pytz.timezone(self.config["TIMEZONE"])
                current_time = datetime.now(tz).strftime("%H:%M")
                new_name = self.config["FORMAT"].format(time=current_time)
                
                # Меняем First Name (Имя) в Telegram
                await self.client(UpdateProfileRequest(first_name=new_name))
            except Exception as e:
                logger.error(f"Ошибка обновления ника: {e}")
            
            # Задержка 60 секунд (безопасно для API Telegram)
            await asyncio.sleep(60)
          
