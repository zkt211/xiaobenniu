import yaml
from dataclasses import dataclass
from typing import Optional, Dict
import time
@dataclass
class TestCaseConfig:
    name: str
    api_key: str
    api_secret: str
    api_url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, str]] = None

class TestCaseManager:
    def __init__(self, template_path: str = "config.yaml", generated_test_path: str = None):
        self.template_path = template_path
        self.generated_test_path = generated_test_path
        self.api_configs : Dict[str, TestCaseConfig] = {}
        self.env_config : Dict[str, str] = {}
        self.write_mode = 'w'
        self._load_template_config()

    def _load_template_config(self):
        with open(self.template_path, 'r', encoding='utf-8') as f:
            config_msg = yaml.safe_load(f)
        # 获取api配置信息
        load_apis = config_msg.get('test_cases', {})
        for case_id, case_data in load_apis.items():
            self.api_configs[case_id] = TestCaseConfig(
                name = case_data['name'],
                api_key=case_data['api_key'],
                api_secret=case_data['api_secret'],
                api_url=case_data['api_url'],
                method=case_data['method'],
                headers=case_data.get('headers'),
                params=case_data.get('params'),
                body=case_data.get('body')
            )
    def set_write_mode(self, target: bool = False):
        #"""设置写入模式""""
        self.write_mode = 'a' if target else 'w'    
    def save_config(self):
        test_cases = {}
        for case_id, api in self.api_configs.items():
            test_cases[case_id] = {
                'name': api.name,
                'method': api.method,
                'headers': api.headers,
                'params': api.params,
                'body': api.body
            }
        
        config_msg = {'test_cases': test_cases}
        
        with open(self.generated_test_path, self.write_mode, encoding='utf-8') as f:
            yaml.dump(config_msg, f, allow_unicode=True)
    def add_api_config(self, case_id: str, config: TestCaseConfig, save: bool = True) -> None:
        # 直接添加到 api_configs 字典中
        self.api_configs[case_id] = config
        
        # 如果需要保存到文件
        if save:
            self.save_config()
    def get_api_config(self, api_name: str) -> TestCaseConfig:
        #"""获取API配置"""
        self._load_demo_config()
        if api_name  in self.api_configs:
            print(self.api_configs[api_name].body)
            return self.api_configs[api_name]
        raise ValueError(f"API配置 {api_name} 不存在")
        
        
    def update_env_config(self, env_config: Dict[str, str]):
        #"""更新环境配置"""
        self.env_config.update(env_config)
        self.save_config()
    def get_env_config(self) -> Dict[str, str]:
        #"""获取环境配置"""
        return self.env_config
    