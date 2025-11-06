from .api import cache_manager



class CachedDataReader:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager

    def get_record(self, category, record_id):
        return self.cache_manager.cache.get(category, {}).get(record_id)

    def get_all_records(self, category):
        return list(self.cache_manager.cache.get(category, {}).values())


cached_data_reader = CachedDataReader(
    cache_manager
)
