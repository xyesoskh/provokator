# meta developer: @lomkapd
# meta name: Provokator
# meta desc: Автоотправка случайного текста из файла шаблонов

from .. import loader, utils
import random
import asyncio
import os

@loader.tds
class Provokator(loader.Module):
    """Автоотправка случайного текста из файла"""

    strings = {
        "name": "Provokator",
        "started": "▶️ Запущено с интервалом {} сек.",
        "stopped": "⏹ Остановлено.",
        "nofile": "❌ Файл templates.txt не найден!",
        "empty": "❌ Файл шаблонов пустой!",
    }

    def __init__(self):
        self.running = False
        self.task = None
        self.templates = []

    async def client_ready(self, client, db):
        path = os.path.join(os.path.dirname(__file__), "templates.txt")

        if not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            self.templates = [line.strip() for line in f if line.strip()]

    @loader.command()
    async def provstart(self, message):
        """Запуск автоотправки. Использование: .provstart <секунды>"""
        args = utils.get_args_raw(message)

        if not args.isdigit():
            await utils.answer(message, "❌ Укажи интервал в секундах. Пример: .provstart 10")
            return

        if not self.templates:
            await utils.answer(message, self.strings["empty"])
            return

        interval = int(args)

        if self.running:
            await utils.answer(message, "⚠️ Уже запущено.")
            return

        self.running = True

        async def loop():
            while self.running:
                text = random.choice(self.templates)
                await message.client.send_message(message.chat_id, text)
                await asyncio.sleep(interval)

        self.task = asyncio.create_task(loop())
        await utils.answer(message, self.strings["started"].format(interval))

    @loader.command()
    async def provstop(self, message):
        """Остановить автоотправку"""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
        await utils.answer(message, self.strings["stopped"])
