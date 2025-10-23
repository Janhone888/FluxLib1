from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from config import logger


class BaseRepository(ABC):
    """仓储层基类，定义通用的数据访问接口"""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取单个实体"""
        pass

    @abstractmethod
    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有实体，支持过滤条件"""
        pass

    @abstractmethod
    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新实体"""
        pass

    @abstractmethod
    def update(self, id: str, update_data: Dict[str, Any]) -> bool:
        """更新实体"""
        pass

    @abstractmethod
    def delete(self, *args) -> bool:
        """删除实体（支持单主键/复合主键，子类按需实现参数数量）"""
        pass

    @abstractmethod
    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计实体数量"""
        pass