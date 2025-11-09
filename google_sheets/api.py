import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import time
import asyncio

from config import settings

from utils.logger import get_bot_logger

class AsyncSheetCacheManager:

    
    def __init__(self, spreadsheet_name, service_account_file, cache_dir="sheet_cache", update_interval=3600):
        self.spreadsheet_name = spreadsheet_name
        self.cache_dir = cache_dir
        self.update_interval = update_interval
        self.cache = {}
        self.sheet_titles = {}
        self.last_update_time = 0

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(spreadsheet_name)

    async def refresh_sheets_info(self):
        worksheets = self.spreadsheet.worksheets()
        self.sheet_titles = {
            ws.id: ws.title
            for ws in worksheets
            if ws.title != "Заказы"
        }
        get_bot_logger().info(f"[Async] Найдено листов: {len(worksheets)}")

    async def get_sheet_title(self, sheet_id):
        return self.sheet_titles.get(sheet_id, f"unknown_sheet_{sheet_id}")

    async def get_all_sheets(self):
        return [
            {"id": sid, "title": title}
            for sid, title in self.sheet_titles.items()
        ]

    def _get_worksheet(self, sheet_id):
        return self.spreadsheet.get_worksheet_by_id(sheet_id)

    # Cache

    async def load_sheet(self, sheet_id):
        """Загружает данные конкретного листа по ID"""
        ws = self._get_worksheet(sheet_id)
        data = ws.get_all_records()
        self.cache[sheet_id] = {row["ID"]: row for row in data}

        cache_file = os.path.join(self.cache_dir, f"cache_{sheet_id}.json")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache[sheet_id], f, ensure_ascii=False, indent=2)
        
        get_bot_logger().info(
            f"[Async] Кэш обновлён для листа '{ws.title}' ({len(data)} записей)"
        )

    async def load_cache_from_file(self, sheet_id):
        """Загружает кэш из файла"""
        cache_file = os.path.join(self.cache_dir, f"cache_{sheet_id}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cache[sheet_id] = data
            return True
        return False

    async def initialize_cache(self):
        await self.refresh_sheets_info()
        for sheet_id in self.sheet_titles.keys():
            if not await self.load_cache_from_file(sheet_id):
                await self.load_sheet(sheet_id)
        self.last_update_time = time.time()

    async def auto_update_cache(self):
        while True:
            if time.time() - self.last_update_time >= self.update_interval:
                await self.refresh_sheets_info()
                for sheet_id in self.sheet_titles.keys():
                    try:
                        await self.load_sheet(sheet_id)
                    except Exception as e:
                        print(f"[Async] Ошибка при обновлении листа {sheet_id}: {e}")
                self.last_update_time = time.time()
            await asyncio.sleep(60)

    async def get_record(self, sheet_id, record_id):
        return self.cache.get(sheet_id, {}).get(record_id)

    async def add_offers(self, records):
        if not records:
            return
        ws = self.spreadsheet.worksheet("Заказы")
        data = ws.get_all_records()
        headers = list(data[0].keys()) if data else list(records[0].keys())
        new_rows = [[rec.get(h, "") for h in headers] for rec in records]
        ws.append_rows(new_rows)



cache_manager = AsyncSheetCacheManager(
    settings.SPREADSHEET_NAME,
    "service_account.json"
)
