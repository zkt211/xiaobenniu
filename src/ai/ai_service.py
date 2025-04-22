import httpx
import openai
from typing import List, Dict, Any

from .ai_config import AIServiceConfig, AIConfigManager  # 添加 AIConfigManager 的导入
import json
import re

class AIService:
    def __init__(self, config: AIServiceConfig):
        self.config = config
        http_client = httpx.Client(
            timeout=config.timeout,
            proxy=config.proxy if hasattr(config, 'proxy') else None
        )
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            http_client=http_client
        )

    @classmethod
    def create(cls, config_path: str):
        # 导入环境变量加载器
        from utils.env_loader import load_env
        
        # 确保环境变量已加载
        load_env()
        
        config_manager = AIConfigManager(config_path)
        # 直接使用 openai 作为键名
        config = config_manager.get_service_config("openai")
        if not config:
            raise ValueError("未找到OpenAI服务配置")
        return cls(config)

    def generate_test_cases(self, api_schema: Dict[str, Any], num_cases: int = None) -> List[Dict[str, Any]]:
        try:
            schema_str = """
            请为以下KYC(Know Your Customer)API生成完整的测试用例集，确保覆盖所有必要的测试场景：

            API 参数说明：
            - name: 客户姓名，字符串类型，2-30个字符
            - idNumber: 身份证号码，字符串类型，18位
            - phoneNumber: 手机号码，字符串类型，11位数字
            - faceImage: 人脸图像，base64编码字符串
            - idCardImage: 身份证图像，base64编码字符串

            测试场景要求：
            1. 正常场景：有效的姓名、身份证号、手机号和图像数据
            2. 边界值测试：姓名长度边界、刚满18岁客户、临近过期证件
            3. 异常场景：无效身份证号、手机号格式错误、姓名包含特殊字符
            4. 组合场景：多个字段同时异常的情况
            5. 欺诈场景：疑似欺诈的数据组合

            请按照以下 JSON 格式返回测试用例：
            [
                {{"name": "张三", "idNumber": "110101200001011234", "phoneNumber": "13800138000", "faceImage": "base64...(省略)", "idCardImage": "base64...(省略)"}},
                {{"name": "李四", "idNumber": "310101199001011234", "phoneNumber": "13900139000", "faceImage": "base64...(省略)", "idCardImage": "base64...(省略)"}}
            ]

            注意：
            1. 必须返回可解析的标准JSON
            2. 为简化测试，faceImage和idCardImage字段可使用简短的占位符如"base64_face_image_data"
            3. 身份证号需符合中国身份证规则，包括地区码、出生日期和校验位
            4. 不要使用任何JavaScript语法
            5. 不要包含注释或说明文字
            6. 请确保生成足够的测试用例以覆盖所有测试场景
            """
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个金融行业KYC测试专家。请只返回标准JSON格式的测试数据，不要包含任何其他内容。"},
                    {"role": "user", "content": schema_str}
                ]
            )
            
            result = self._parse_ai_response(response.choices[0].message.content)
            if not result:
                print("AI 返回结果解析失败")
                return []
            return result
            
        except Exception as e:
            print(f"生成测试用例失败：{str(e)}")
            return []

    def _parse_ai_response(self, content: str) -> List[Dict[str, Any]]:
        try:
            # 预处理 AI 返回的内容
            content = content.replace('```json', '').replace('```', '').strip()
            content = content.replace('.repeat(', ' * ')  # 替换 JavaScript 的 repeat 为 Python 的乘法
            
            # 处理特殊的 JavaScript 函数调用
            import re
            repeat_pattern = r'"([^"]*)" \* (\d+)'
            content = re.sub(repeat_pattern, lambda m: f'"{m.group(1) * int(m.group(2))}"', content)
            
            # 尝试解析 JSON
            import json
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                # 如果解析失败，尝试提取 JSON 数组部分
                array_match = re.search(r'\[([\s\S]*)\]', content)
                if array_match:
                    array_content = f"[{array_match.group(1)}]"
                    # 清理可能的多余逗号
                    array_content = re.sub(r',(\s*[}\]])', r'\1', array_content)
                    return json.loads(array_content)
                raise e
                
        except Exception as e:
            print(f"JSON 解析失败：{str(e)}\n原始内容：\n{content}")