    def clear_cache_handler(self):
        """Clear cached data and notify user."""
        if hasattr(self, 'plugin_instance') and self.plugin_instance:
            self.plugin_instance.data_cache.clear()
            self.results.append("✓ Cache cleared - next preview will re-process data")
            logger.info("Cache cleared by user")
        else:
            self.results.append("⚠ Cache not available")
