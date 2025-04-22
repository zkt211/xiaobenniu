import unittest
import os
import sys
import time
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from network.http_client import HttpClient
from ai.ai_service import AIService
from test.test_suite import TestSuite
from test.test_case import TestCase, TestStatus

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.current_time = time.strftime('%Y%m%d%H%M%S')
        self.test_cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'test_cases.yaml')
        self.ai_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'ai_config.yaml')
        
        # 加载测试套件
        self.test_suite = TestSuite.from_yaml(self.test_cases_path)
        
    def test_case_execution(self):
        # 执行测试套件中的所有测试用例
        self.execute_test_suite()
        
    def execute_test_suite(self):
        # 获取测试用例执行顺序
        execution_order = self.test_suite.get_execution_order()
        
        # 创建HTTP客户端
        client = HttpClient(timeout=30)
        
        # 测试结果统计
        test_results = {
            'total': 0,
            'pass': 0,
            'fail': 0,
            'failed_cases': []
        }
        
        print(f"开始执行测试套件: {self.test_suite.name}")
        print(f"测试用例执行顺序: {execution_order}")
        
        # 按顺序执行测试用例
        for case_id in execution_order:
            case = self.test_suite.cases[case_id]
            print(f"\n执行测试用例: {case.name} ({case_id})")
            
            # 解析变量
            api_path = self.test_suite.resolve_variables(case.api_path)
            print(f"API路径: {api_path}")
            print(f"请求方法: {case.method}")
            
            # 设置用例状态为运行中
            case.status = TestStatus.RUNNING
            
            # 执行请求
            try:
                if case.method == "GET":
                    response = client.get(
                        url=api_path,
                        headers=case.headers,
                        params=case.params
                    )
                elif case.method == "POST":
                    response = client.post(
                        url=api_path,
                        headers=case.headers,
                        body=case.body
                    )
                # 可以根据需要添加其他HTTP方法
                
                # 验证响应状态码
                if response.status_code == case.expected_status:
                    print(f"测试通过: 状态码 {response.status_code}")
                    case.status = TestStatus.PASSED
                    test_results['pass'] += 1
                else:
                    print(f"测试失败: 预期状态码 {case.expected_status}, 实际状态码 {response.status_code}")
                    case.status = TestStatus.FAILED
                    test_results['fail'] += 1
                    test_results['failed_cases'].append({
                        'case_id': case_id,
                        'name': case.name,
                        'expected_status': case.expected_status,
                        'actual_status': response.status_code,
                        'response': response.body
                    })
            except Exception as e:
                print(f"测试错误: {str(e)}")
                case.status = TestStatus.ERROR
                test_results['fail'] += 1
                test_results['failed_cases'].append({
                    'case_id': case_id,
                    'name': case.name,
                    'error': str(e)
                })
            
            test_results['total'] += 1
        
        client.close()
        
        # 输出测试报告
        print(f"\n测试报告==================================")
        print(f"总用例数: {test_results['total']}")
        print(f"通过用例数: {test_results['pass']}")
        print(f"失败用例数: {test_results['fail']}")
        
        if test_results['failed_cases']:
            print("\n失败用例详情:")
            for case in test_results['failed_cases']:
                print(f"用例ID: {case['case_id']}")
                print(f"用例名称: {case['name']}")
                if 'expected_status' in case:
                    print(f"预期状态码: {case['expected_status']}")
                    print(f"实际状态码: {case['actual_status']}")
                    print(f"响应内容: {case['response']}")
                else:
                    print(f"错误信息: {case['error']}")
                print("------------------------")
        
        # 断言测试结果
        self.assertEqual(test_results['fail'], 0, f"有 {test_results['fail']} 个测试用例失败")

    def test_ai_generated_cases(self):
        # 使用AI生成测试用例
        ai_service = AIService.create(self.ai_config_path)
        
        # KYC API模式定义
        api_schema = {
            "url": "https://api.kyc-service.com/v1/verify/identity",
            "method": "POST",
            "body_schema": {
                "customer_id": "string (客户ID)",
                "id_type": "string (证件类型: passport, id_card, driver_license)",
                "id_number": "string (证件号码)",
                "name": "string (姓名)",
                "birth_date": "string (出生日期, 格式: YYYY-MM-DD)"
            }
        }
        
        # 生成测试用例
        ai_test_cases = ai_service.generate_test_cases(api_schema, num_cases=5)
        
        # 创建测试套件
        test_suite = TestSuite(
            name="AI生成的KYC测试套件",
            description="AI自动生成的KYC身份验证测试用例",
            cases={}
        )
        
        # 添加AI生成的测试用例
        for i, ai_case in enumerate(ai_test_cases, 1):
            case_id = f"ai_case_{i}"
            test_case = TestCase(
                case_id=case_id,
                name=f"AI生成的身份验证测试 {i}",
                description=f"自动生成的KYC身份验证测试用例 {i}",
                api_path=api_schema["url"],
                method=api_schema["method"],
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body=ai_case,
                expected_status=200
            )
            test_suite.cases[case_id] = test_case
            print(f"AI生成测试用例 {case_id}: {ai_case}")
        
        # 保存生成的测试套件
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'tests', f'ai_generated_cases_{self.current_time}.yaml')
        
        # 将测试套件转换为YAML格式并保存
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml_data = {
                'name': test_suite.name,
                'description': test_suite.description,
                'test_cases': {
                    case_id: {
                        'name': case.name,
                        'description': case.description,
                        'api_path': case.api_path,
                        'method': case.method,
                        'headers': case.headers,
                        'body': case.body,
                        'expected_status': case.expected_status
                    }
                    for case_id, case in test_suite.cases.items()
                }
            }
            yaml.dump(yaml_data, f, allow_unicode=True)
        
        print(f"AI生成的测试用例已保存到: {output_path}")

if __name__ == '__main__':
    unittest.main()