from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class TestStatus(Enum):
    """测试用例状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"

@dataclass
class TestCase:
    """测试用例数据类
    
    属性:
        case_id: 用例ID
        name: 用例名称
        description: 用例描述
        api_path: API路径
        method: HTTP方法
        headers: 请求头
        params: 查询参数
        body: 请求体
        expected_status: 预期状态码
        expected_response: 预期响应
        timeout: 超时时间
        dependencies: 依赖的用例ID列表
        status: 用例执行状态
    """
    case_id: str
    name: str
    description: str
    api_path: str
    method: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    expected_response: Optional[Dict[str, Any]] = None
    expected_data: Optional[Dict[str, Any]] = None
    timeout: int = 30
    dependencies: List[str] = None
    status: TestStatus = TestStatus.PENDING
    
    def __post_init__(self):
        """初始化后的验证和处理"""
        if self.dependencies is None:
            self.dependencies = []
        if self.method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            raise ValueError(f"不支持的HTTP方法: {self.method}")