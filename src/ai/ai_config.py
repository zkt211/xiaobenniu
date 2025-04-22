import yaml
from dataclasses import dataclass, asdict
from typing import Optional, Dict
from utils.env_loader import get_env

@dataclass(frozen=True)  # 使用不可变数据类，确保配置安全性
class AIServiceConfig:
    """AI服务配置数据类
    
    属性:
        api_key: API密钥
        api_base: API基础URL
        model: 模型名称
        timeout: 超时时间（秒）
        proxy: 代理服务器地址
    """
    api_key: str
    api_base: str
    model: str
    timeout: int = 30
    proxy: Optional[str] = None

    def __post_init__(self):
        """初始化后的验证"""
        if self.timeout <= 0:
            raise ValueError("timeout必须大于0")
        if self.model.strip() == "":
            raise ValueError("model不能为空")

    def to_dict(self) -> Dict[str, any]:
        """转换为字典格式"""
        return asdict(self)

@dataclass
class AIConfig:
    """AI配置管理数据类
    
    属性:
        ai_services: 服务配置字典
    """
    ai_services: Dict[str, AIServiceConfig]



class AIConfigManager:
    """AI配置管理器
    
    负责加载和管理AI服务的配置信息
    """
    def __init__(self, config_path: str):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = AIConfig.from_yaml(config_path)
    
    def get_service_config(self, service_name: str) -> Optional[AIServiceConfig]:
        """获取指定服务的配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            AIServiceConfig: 服务配置对象，如果不存在则返回None
        """
        return self.config.get_service_config(service_name)