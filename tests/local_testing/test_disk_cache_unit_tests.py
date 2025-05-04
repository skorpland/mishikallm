from cache_unit_tests import LLMCachingUnitTests
from mishikallm.caching import MishikaLLMCacheType


class TestDiskCacheUnitTests(LLMCachingUnitTests):
    def get_cache_type(self) -> MishikaLLMCacheType:
        return MishikaLLMCacheType.DISK


# if __name__ == "__main__":
#     pytest.main([__file__, "-v", "-s"])
