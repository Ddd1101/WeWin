from typing import Dict, Optional
from ..platform_adapters.base import BasePlatformAdapter
from ..platform_adapters.ali_1688 import Ali1688Adapter
from ..industry_adapters.base import BaseIndustryAdapter
from ..industry_adapters.crystal_bracelet import CrystalBraceletAdapter


class AdapterFactory:
    """适配器工厂，用于创建平台和行业适配器"""

    PLATFORM_ALI_1688 = "ali_1688"
    INDUSTRY_CRYSTAL_BRACELET = "crystal_bracelet"

    @classmethod
    def create_platform_adapter(cls, platform: str, store_config: Dict) -> Optional[BasePlatformAdapter]:
        """
        创建平台适配器
        :param platform: 平台名称
        :param store_config: 店铺配置
        :return: 平台适配器实例
        """
        if platform == cls.PLATFORM_ALI_1688:
            return Ali1688Adapter(store_config)
        return None

    @classmethod
    def create_industry_adapter(cls, industry: str) -> Optional[BaseIndustryAdapter]:
        """
        创建行业适配器
        :param industry: 行业名称
        :return: 行业适配器实例
        """
        if industry == cls.INDUSTRY_CRYSTAL_BRACELET:
            return CrystalBraceletAdapter()
        return None
