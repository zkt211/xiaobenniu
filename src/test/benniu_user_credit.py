#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import time
import yaml
import json
import random  # 确保这行在这里
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from network.http_client import HttpClient
from ai.ai_service import AIService
from util.rsa_util import RSAEncrypUtil
from .test_suite import TestSuite
from .test_case import TestCase, TestStatus

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.current_time = time.strftime('%Y%m%d%H%M%S')
        #还款测试用例路径
        self.test_cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tests', 'test_cases_user_credit.yaml')

        #进件
        # self.test_cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tests', 'test_cases_user_check.yaml')
        self.ai_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'ai_config.yaml')
        self.rsa_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rsa_config.yaml')
        
        # 加载RSA配置
        with open(self.rsa_config_path, 'r', encoding='utf-8') as f:
            rsa_config = yaml.safe_load(f)
            channel_rsa = rsa_config.get('channel_rsa', {})
            self.channel_private_key = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC2GWk9HKsazGpLFujzqr3eVlvwjVLmfr/3C8C4gLGSGyiFGv0SU0slT8iMvnB5RlGfkHmYqNuSxVOwGRtRHs6Kv5A15duhL8K29lrfoeArF0vSBGx9viC+IvCgdXTsVbLqyK+Wo5mnBZPKRhjU3aJq2fyVr/wxDbkYUWN6iy+YhCptmkzZz7tA9NGoPa62XaMY759QYnzjpbu5UY+qcmTmAmfxizOW8GIeryY4b6//eskOYD3F0qfGfuAezZRqCZAfAK8NsTYCKPhhUtunqfq0QWAhYAPQhSGARkRoYKOBhCMIu0pqWJY+rvW6OGc72SrhVlSr9euYKqXpikXSTA27AgMBAAECggEABsuE80xWEC5vivTEZY9J/XlwfdXwMXyqUiAkpV3cAm00Al+C8QOdqrtC6wmSLdxTYGZmOy2V3/CwEkKlk83X/DJwwaodm3KqS+R+eJjUQhdg82nJ2JlXJHEuVHZ9kfIStpMdhjv9mE9rd+FMvOi2TlFrDPTfrr7p2L/0u9ZkxMadk1rTCJBqSSDe4FAxlxTT2LtvruZY8D/Vk49wlIeNc0VtiRRTM3qXQxRShWb6RwzL6+uQTa3kaJOPdkplhwAmo0BO9c++X1cV1CEfc1DFF7818CaRfWxAcp6Q9xEpLcs+V+gajaaLYmdNmRf8Hef75CUt5GpeYbxDT3U3zpoXVQKBgQDuZXl7cCDBqkvLmUql/65Wm+lSZKMA/ygSb8ejPE+gHOE1IQVwB65DawMkNHaQIg6nwtFQbMndX85rSY9lpcpv54WxB0TUfrWIWmh1T3qc9xlbtpPg3P5LBF9d6UcNOOINNrxBcVOL+MCYxGKnrYlrPOvAuYX/ohtW5R+nysX3xQKBgQDDi7lZ+3VqYP6MZgmaZvpdBZrn0K85Cvw9ecumMRefRo0ywu2vD/yV+CAJlNpvDdSARX0AyxCh8d4KmKWTRarUR7Y4X28iv3Asvw50U3OGF5HiQMRSr+3byK9OK4zrwujwzKm5LaoevnPv8dkuRMMGV2pP8jNU/6znGOD8KEzHfwKBgAKZ0tB48bKLNBZ9jqXu+yzwuIPwmyKopfxFge0S/F9n0UEuIgwN2WXc5gTgGacK6BQGeRgih7VFlU/wVoMqYuIDqZ670JFs7HgXXGpjOpg5zeoFPOnIH3IcExpIMEFBrJ2uSjGAlgPB6//+rIDd0ND9sijBHWgjkZ7KEyVWfgBtAoGAOzNU9SIE5STiS50ksSMWDw2AXUg3lDx4KyBxgCoCrczNOJ39GW/sl3acNGplSxPTztW6x3+y1GSGRYz7K7/+vO/NAfoailmM228oMB2HrwP5vZbAGQx8JXr3X+Idcs76eNRtWcuyYkZkkTMV/kUBCi1y2StJUSVqsjg8/PoybH8CgYBFAcsqHSBkP5R4/rrOJhLZBiaAqAq55PPBC/nwP4haDP0g1aS0TdPUY1I28bWpPwrYxIiFNuslgERcMSLUk9oR3Mbs6JOqImXqvry3n89qmEp645C5jlfjfhIIOggchD3wo7pfOP3JLzpO4kZ8M6Uvfgg7xA/9qjHufrlxPmLvjQ==" # 保持原有的私钥值

            self.platform_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAriU/S6vaJIo51W4flYzfM+bXvsAC3zri+5mfLrj3cOX+zoFuIK9bVD3nQd8gDNcMIpBlZgmnY9YuLZ1/sdIGvnjakGGJuraipbvqhxqLHdbknQWgH+eE6unkxCuP8LA2HZIsy0eb/Sqb1/2t8zQdBY2sO3WC8hc4Wj/TixchYbZDUlgCuDvtxrtbWtHJdjsUwxslQi3qJjVdbd2k8k73CtH+eAP6gY8v9lcc5tW/KkzsZX05/WP1arOxalJuGoCq6mb0ttwthaVFjBxWWeJ2VWh0rGJjMUZrlK3gir8w7Qftlasf7MSmYjl/7LVc7lbTizL5LAdT6xJuK2WeUnZ4DQIDAQAB"
        
        # 加载测试套件
        self.test_suite = TestSuite.from_yaml(self.test_cases_path)
        
    def test_case_execution(self):
        """单次执行测试用例"""
        self.execute_test_suite()
        
    def concurrent_execution(self):
        """并发执行测试用例"""
        import concurrent.futures
        
        repeat_times = 10  # 可以后续改为从配置文件读取
        max_workers = 5
        
        total_results = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0
        }
        
        print(f"\n开始并发执行测试套件: {self.test_suite.name}")
        print(f"重复次数: {repeat_times}, 并发线程数: {max_workers}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.execute_test_suite)
                for _ in range(repeat_times)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    total_results['total_runs'] += 1
                    if result['fail'] == 0:
                        total_results['successful_runs'] += 1
                    else:
                        total_results['failed_runs'] += 1
                except Exception as e:
                    print(f"执行出错: {str(e)}")
                    total_results['total_runs'] += 1
                    total_results['failed_runs'] += 1
        
        # 打印总体执行报告
        print("\n并发执行报告==================================")
        print(f"总执行次数: {total_results['total_runs']}")
        print(f"成功执行次数: {total_results['successful_runs']}")
        print(f"失败执行次数: {total_results['failed_runs']}")
        print(f"成功率: {(total_results['successful_runs'] / total_results['total_runs'] * 100):.2f}%")
        
        # 使用断言确保测试结果符合预期
        self.assertGreater(total_results['successful_runs'] / total_results['total_runs'], 0.8, 
                          "并发测试成功率低于80%")
        
    def execute_test_suite(self, timeout=30):
        """执行测试套件
        
        Args:
            timeout (int): 请求超时时间（秒）
        """
        # 获取测试用例执行顺序
        execution_order = self.test_suite.get_execution_order()
        
        # 创建HTTP客户端，使用传入的超时时间
        client = HttpClient(timeout=timeout)
        
        # 测试结果统计
        test_results = {
            'total': len(execution_order),
            'pass': 0,
            'fail': 0,
            'failed_cases': []
        }
        
        print(f"\n开始执行测试套件: {self.test_suite.name}")
        
        # 按顺序执行测试用例
        for case_id in execution_order:
            case = self.test_suite.cases[case_id]
            print(f"\n执行测试用例: {case.name} ({case_id})")
            
            # 解析变量
            api_path = self.test_suite.resolve_variables(case.api_path)
            print(f"API路径: {api_path}")
            print(f"请求方法: {case.method}")
            
            # 处理请求体中的加密数据
            if isinstance(case.body, dict) and 'data' in case.body:
                # 生成新的随机身份证号
                new_id_number = self.generate_random_id_number()
                
                # 更新userAuthInfo中的身份证号和相关信息
                if 'userAuthInfo' in case.body['data'] and isinstance(case.body['data']['userAuthInfo'], dict):
                    case.body['data']['userAuthInfo']['idNo'] = new_id_number
                    # 从身份证号中提取出生日期
                    birth_date = f"{new_id_number[6:10]}-{new_id_number[10:12]}-{new_id_number[12:14]}"
                    case.body['data']['userAuthInfo']['birthDay'] = birth_date
                    print(f"使用随机生成的身份证号: {new_id_number}")
                    print(f"对应的出生日期: {birth_date}")
                
                # 生成当前时间戳
                current_timestamp = int(time.time() * 1000)
                case.body['timestamp'] = current_timestamp
                
                # 将data对象转换为JSON字符串
                if isinstance(case.body['data'], dict):
                    data_str = json.dumps(case.body['data'], separators=(',', ':'))
                    # 加密数据
                    encrypted_data = RSAEncrypUtil.build_rsa_encrypt_by_public_key(
                        data_str,
                        self.platform_public_key
                    )
                    case.body['data'] = encrypted_data
                    # 生成签名
                    case.body['sign'] = RSAEncrypUtil.build_rsa_sign_by_private_key(
                        encrypted_data,
                        self.channel_private_key
                    )
            
            # print(f"请求消息体: {case}")
            
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
                # 验证响应状态码和格式
                if response.status_code == case.expected_status:
                    try:
                        response_body = json.loads(response.body)
                        # print(f"响应消息体: {response_body}")
                        # 验证响应格式
                        required_keys = ['code', 'data', 'sign']
                        if not all(key in response_body for key in required_keys):
                            print(f"测试失败: 响应格式不符合要求")
                            case.status = TestStatus.FAILED
                            test_results['fail'] += 1
                            test_results['failed_cases'].append({
                                'case_id': case.case_id,
                                'name': case.name,
                                'error': '响应格式不符合要求',
                                'response': response_body
                            })
                            continue
                        
                        # 验证返回码
                        expected_code = case.expected_response.get('code', '000000')
                        if str(response_body['code']) != str(expected_code):
                            print(f"测试失败: 业务返回码错误，预期: {expected_code}，实际: {response_body['code']}")
                            case.status = TestStatus.FAILED
                            test_results['fail'] += 1
                            test_results['failed_cases'].append({
                                'case_id': case.case_id,
                                'name': case.name,
                                'error': f"业务返回码错误: {response_body['code']}, 错误信息: {response_body.get('msg', response_body.get('message', '未知错误'))}"
                            })
                            continue
                        
                        # 在验证签名之前，先处理响应数据
                        response_data = response_body['data']
                        
                        # 添加调试信息
                        # print(f"响应数据: {response_data}")
                        # print(f"签名: {response_body['sign']}")
                        # print(f"平台公钥: {self.platform_public_key[:30]}...")
                        
                        # 验证签名
                        try:
                            verify_sign = RSAEncrypUtil.build_rsa_verify_by_public_key(
                                response_data,
                                self.platform_public_key,
                                response_body['sign']
                            )
                            if not verify_sign:
                                print(f"测试失败: 响应签名验证失败")
                                case.status = TestStatus.FAILED
                                test_results['fail'] += 1
                                test_results['failed_cases'].append({
                                    'case_id': case.case_id,
                                    'name': case.name,
                                    'error': '响应签名验证失败'
                                })
                                continue
                        except Exception as e:
                            print(f"验签失败: {str(e)}")
                            case.status = TestStatus.FAILED
                            test_results['fail'] += 1
                            test_results['failed_cases'].append({
                                'case_id': case.case_id,
                                'name': case.name,
                                'error': f'验签过程出错: {str(e)}'
                            })
                            continue
                    
                        try:
                            # 解密响应数据--还款
                            decrypted_data = RSAEncrypUtil.build_rsa_decrypt_by_private_key(
                                response_body['data'],
                                self.channel_private_key
                            )
                            # 解析解密后的JSON数据
                            decrypted_json = json.loads(decrypted_data)
                            print(f"解密后的action数据: {decrypted_json['success'],decrypted_json['message']}")
                            print(f"预期数据: {case.expected_data['success']}")
                            
                            # 验证解密后的数据结构是否符合预期
                            if case.expected_data['success'] != decrypted_json['success']:
                                print(f"测试失败: 响应数据与预期不符")
                                case.status = TestStatus.FAILED
                                test_results['fail'] += 1
                                test_results['failed_cases'].append({
                                    'case_id': case.case_id,
                                    'name': case.name,
                                    'error': '响应数据与预期不符',
                                    'expected': case.expected_data,
                                    'actual': decrypted_json
                                })
                                continue

                            # # 解析解密后的JSON数据--初筛
                            # decrypted_json = json.loads(decrypted_data)
                            # print(f"解密后的action数据: {decrypted_json['checkLoan']}")
                            # print(f"预期数据: {case.expected_data['checkLoan']}")
                            
                            # # 验证解密后的数据结构是否符合预期
                            # if case.expected_data['checkLoan'] != decrypted_json['checkLoan']:
                            #     print(f"测试失败: 响应数据与预期不符")
                            #     case.status = TestStatus.FAILED
                            #     test_results['fail'] += 1
                            #     test_results['failed_cases'].append({
                            #         'case_id': case.case_id,
                            #         'name': case.name,
                            #         'error': '响应数据与预期不符',
                            #         'expected': case.expected_data,
                            #         'actual': decrypted_json
                            #     })
                            #     continue
                    
                            print(f"测试通过: 状态码 {response.status_code}, 响应数据解密成功且符合预期")
                            case.status = TestStatus.PASSED
                            test_results['pass'] += 1
                        except json.JSONDecodeError as e:
                            print(f"测试失败: 解密后的数据不是有效的JSON格式")
                            case.status = TestStatus.FAILED
                            test_results['fail'] += 1
                            test_results['failed_cases'].append({
                                'case_id': case.case_id,
                                'name': case.name,
                                'error': f'解密后的数据格式错误: {str(e)}'
                            })
                        except Exception as e:
                            print(f"测试失败: 响应数据解密失败")
                            case.status = TestStatus.FAILED
                            test_results['fail'] += 1
                            test_results['failed_cases'].append({
                                'case_id': case.case_id,
                                'name': case.name,
                                'error': f'响应数据解密失败: {str(e)}'
                            })
                    except json.JSONDecodeError as e:
                        print(f"测试失败: 响应不是有效的JSON格式")
                        case.status = TestStatus.FAILED
                        test_results['fail'] += 1
                        test_results['failed_cases'].append({
                            'case_id': case.case_id,
                            'name': case.name,
                            'error': f'响应格式错误: {str(e)}',
                            'response': response.text
                        })
                else:
                    print(f"测试失败: 预期状态码 {case.expected_status}, 实际状态码 {response.status_code}")
                    case.status = TestStatus.FAILED
                    test_results['fail'] += 1
                    test_results['failed_cases'].append({
                        'case_id': case.case_id,
                        'name': case.name,
                        'error': f'HTTP状态码错误: {response.status_code}',
                        'response': response
                    })
            except Exception as e:
                print(f"测试错误: {str(e)}")
                case.status = TestStatus.ERROR
                test_results['fail'] += 1
                test_results['failed_cases'].append({
                    'case_id': case.case_id,
                    'name': case.name,
                    'error': str(e)
                })
            
            # test_results['total'] += 1
        
        client.close()
        
        # 输出测试报告（只打印一次）
        print("\n测试报告==================================")
        print(f"总用例数: {test_results['total']}")
        print(f"通过用例数: {test_results['pass']}")
        print(f"失败用例数: {test_results['fail']}")
        
        if test_results['failed_cases']:
            print("\n失败用例详情:")
            for case in test_results['failed_cases']:
                print(f"用例ID: {case['case_id']}")
                print(f"用例名称: {case['name']}")
                print(f"错误信息: {case['error']}")
                print("------------------------")
        
        # 断言测试结果
        # self.assertEqual(test_results['fail'], 0, f"有 {test_results['fail']} 个测试用例失败")

    def generate_random_id_number(self):
        """生成随机身份证号"""
        # 随机生成地区码(以北京市的区域码为例)
        area_code = "110101"  # 可以扩展为随机地区码
        
        # 随机生成出生日期(1960-2000年之间)
        year = str(random.randint(1960, 2000))
        month = str(random.randint(1, 12)).zfill(2)
        day = str(random.randint(1, 28)).zfill(2)  # 简化处理，统一使用28天
        birth_date = f"{year}{month}{day}"
        
        # 随机生成顺序码
        sequence = str(random.randint(1, 999)).zfill(3)
        
        # 构建前17位
        base = f"{area_code}{birth_date}{sequence}"
        
        # 计算校验码
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_dict = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}
        
        # 计算加权和
        weight_sum = sum(int(base[i]) * weights[i] for i in range(17))
        
        # 计算校验码
        check_code = check_dict[weight_sum % 11]
        
        # 组合最终的身份证号码
        id_number = f"{base}{check_code}"
        return id_number

if __name__ == '__main__':
    unittest.main()
