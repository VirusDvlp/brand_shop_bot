import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import time
import asyncio

from config import settings, categories

from utils.logger import get_bot_logger

class AsyncSheetCacheManager:

    def __init__(self, spreadsheet_name, categories, service_account_file, cache_dir="data/cache", update_interval=3600):
        self.spreadsheet_name = spreadsheet_name
        self.categories = categories
        self.cache_dir = cache_dir
        self.update_interval = update_interval
        self.cache = {}  # {category: {id: record}}
        self.last_update_time = 0

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
        client = gspread.authorize(creds)
        self.spreadsheet = client.open(spreadsheet_name)

    async def load_sheet(self, category):
        sheet = self.spreadsheet.worksheet(category)
        data = sheet.get_all_records()
        self.cache[category] = {row["id"]: row for row in data}
        self.last_update_time = time.time()

        cache_file = os.path.join(self.cache_dir, f"cache_{category}.json")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    async def load_cache_from_file(self, category):
        cache_file = os.path.join(self.cache_dir, f"cache_{category}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cache[category] = {row["id"]: row for row in data}
            return True
        return False

    async def initialize_cache(self):
        for category in self.categories:
            if not await self.load_cache_from_file(category):
                await self.load_sheet(category)

    async def auto_update_cache(self):
        while True:
            current_time = time.time()
            if current_time - self.last_update_time >= self.update_interval:
                get_bot_logger().info("Автообновление всех категорий...")
                for category in self.categories:
                    try:
                        await self.load_sheet(category)
                    except Exception as e:
                        get_bot_logger().error(f"[Async] Ошибка при обновлении категории '{category}':", e)
            await asyncio.sleep(60)


    async def add_offers(self, records):
        if not records:
            return

        sheet = self.spreadsheet.worksheet("Заказы")
        data = sheet.get_all_records()
        headers = list(data[0].keys()) if data else list(records[0].keys())

        new_rows = [[rec.get(h, "") for h in headers] for rec in records]
        sheet.append_rows(new_rows)


cache_manager = AsyncSheetCacheManager(
    settings.SPREADSHEET_NAME,
    categories,
    "service_account.json"
)
