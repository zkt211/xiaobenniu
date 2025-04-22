import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
from .test_case import TestCase, TestStatus

@dataclass
class TestSuite:
    """测试套件数据类
    
    属性:
        name: 套件名称
        description: 套件描述
        cases: 测试用例字典
        variables: 变量字典
    """
    name: str
    description: str
    cases: Dict[str, TestCase]
    variables: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'TestSuite':
        """从YAML文件加载测试套件"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                cases = {}
                for case_id, case_data in data['test_cases'].items():
                    case_data['case_id'] = case_id
                    # 移除setup字段，因为TestCase类不需要这个字段
                    if 'setup' in case_data:
                        del case_data['setup']
                    cases[case_id] = TestCase(**case_data)
                
                return cls(
                    name=data.get('name', 'Default Suite'),
                    description=data.get('description', ''),
                    cases=cases,
                    variables=data.get('variables', {})
                )
        except Exception as e:
            raise ValueError(f"加载测试套件失败: {str(e)}")
    
    def get_execution_order(self) -> List[str]:
        """根据依赖关系确定执行顺序"""
        executed = set()
        order = []
        
        def add_case(case_id: str):
            if case_id in executed:
                return
            if case_id not in self.cases:
                raise ValueError(f"依赖的测试用例不存在: {case_id}")
                
            case = self.cases[case_id]
            for dep in case.dependencies:
                if dep not in executed:
                    add_case(dep)
            order.append(case_id)
            executed.add(case_id)
        
        for case_id in self.cases:
            add_case(case_id)
        
        return order
    
    def resolve_variables(self, text: str) -> str:
        """解析变量引用"""
        if not isinstance(text, str):
            return text

        # 处理变量替换
        for var_name, var_value in self.variables.items():
            placeholder = f"${{{var_name}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(var_value))
        return text

    def _encrypt_data(self, data: str) -> str:
        """对数据进行RSA加密"""
        try:
            from util.rsa_util import RSAEncrypUtil
            encrypted_data = RSAEncrypUtil.build_rsa_encrypt_by_public_key(
                data,
                self.variables.get('platform_public_key', '')
            )
            return encrypted_data
        except Exception as e:
            raise ValueError(f"RSA加密失败: {str(e)}")

    def _sign_data(self, data: dict) -> str:
        """对数据进行RSA签名"""
        try:
            from util.rsa_util import RSAEncrypUtil
            import json
            # 将数据转换为待签名的字符串
            data_str = json.dumps(data, separators=(',', ':'))
            # 使用渠道私钥进行签名
            sign = RSAEncrypUtil.build_rsa_sign_by_private_key(
                data_str,
                self.variables.get('channel_private_key', '')
            )
            return sign
        except Exception as e:
            raise ValueError(f"RSA签名失败: {str(e)}")
    
    def resolve_case_variables(self, case_id: str) -> None:
        """解析测试用例中的所有变量"""
        case = self.cases[case_id]
        
        # 解析API路径中的变量
        case.api_path = self.resolve_variables(case.api_path)
        
        # 解析请求体中的变量
        if case.body:
            self._resolve_dict_variables(case.body)
            # 对data字段进行加密
            if 'data' in case.body and isinstance(case.body['data'], dict):
                # 先将data字段转换为JSON字符串
                data_str = json.dumps(case.body['data'], separators=(',', ':'))
                # 对data字段进行加密
                case.body['data'] = self._encrypt_data(data_str)
                # 生成签名
                case.body['sign'] = self._sign_data(case.body)
            
        # 解析请求参数中的变量
        if case.params:
            self._resolve_dict_variables(case.params)
            
        # 解析请求头中的变量
        if case.headers:
            self._resolve_dict_variables(case.headers)
    
    def _resolve_dict_variables(self, data: Dict) -> None:
        """递归解析字典中的变量"""
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = self.resolve_variables(value)
            elif isinstance(value, dict):
                self._resolve_dict_variables(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        value[i] = self.resolve_variables(item)
                    elif isinstance(item, dict):
                        self._resolve_dict_variables(item)
    
    def _verify_response_data(self, actual_data: Dict[str, Any], expected_data: Dict[str, Any]) -> bool:
        """验证响应数据是否符合预期"""
        if not expected_data:
            return True
            
        try:
            for key, expected_value in expected_data.items():
                if key not in actual_data:
                    print(f"响应数据缺少字段: {key}")
                    return False
                
                actual_value = actual_data[key]
                if expected_value is None:
                    if actual_value is not None:
                        print(f"字段 {key} 预期为 None，实际为: {actual_value}")
                        return False
                elif actual_value != expected_value:
                    print(f"字段 {key} 值不匹配，预期: {expected_value}，实际: {actual_value}")
                    return False
            
            return True
        except Exception as e:
            print(f"验证响应数据时发生错误: {str(e)}")
            return False
    
    def validate_response(self, case: TestCase, response_data: Dict[str, Any]) -> bool:
        """验证响应数据"""
        # 验证业务状态码
        if case.expected_response:
            expected_code = case.expected_response.get('code')
            actual_code = response_data.get('code')
            if expected_code and str(actual_code) != str(expected_code):
                print(f"业务状态码不匹配，预期: {expected_code}，实际: {actual_code}")
                return False
        
        # 验证业务数据
        if case.expected_data:
            decrypted_data = response_data.get('data', {})
            if isinstance(decrypted_data, str):
                try:
                    decrypted_data = json.loads(decrypted_data)
                except json.JSONDecodeError:
                    print("解密后的数据不是有效的JSON格式")
                    return False
            
            if not self._verify_response_data(decrypted_data, case.expected_data):
                return False
        
        return True
