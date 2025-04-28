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

class SnowflakeGenerator:
    def __init__(self, worker_id=0, datacenter_id=0):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1
        
        # 时间戳、数据中心、机器、序列号的位数
        self.timestamp_bits = 41
        self.datacenter_bits = 5
        self.worker_bits = 5
        self.sequence_bits = 12
        
        # 最大值
        self.max_worker_id = -1 ^ (-1 << self.worker_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)
        
        # 偏移量
        self.worker_shift = self.sequence_bits
        self.datacenter_shift = self.sequence_bits + self.worker_bits
        self.timestamp_shift = self.sequence_bits + self.worker_bits + self.datacenter_bits
        
        # 开始时间戳 (2024-01-01 00:00:00 UTC)
        self.twepoch = 1704067200000

    def get_timestamp(self):
        return int(time.time() * 1000)

    def wait_next_millis(self, last_timestamp):
        timestamp = self.get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self.get_timestamp()
        return timestamp

    def next_id(self):
        timestamp = self.get_timestamp()
        
        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards!")
            
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.max_sequence
            if self.sequence == 0:
                timestamp = self.wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0
            
        self.last_timestamp = timestamp
        
        # 组合ID
        snowflake_id = ((timestamp - self.twepoch) << self.timestamp_shift) | \
                       (self.datacenter_id << self.datacenter_shift) | \
                       (self.worker_id << self.worker_shift) | \
                       self.sequence
                       
        return str(snowflake_id)

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.current_time = time.strftime('%Y%m%d%H%M%S')
        #进件测试用例路径
        self.test_cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tests', 'test_cases_user_credit.yaml')

        self.ai_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'ai_config.yaml')
        self.rsa_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rsa_config.yaml')
        
        # 加载RSA配置
        with open(self.rsa_config_path, 'r', encoding='utf-8') as f:
            rsa_config = yaml.safe_load(f)
            channel_rsa = rsa_config.get('channel_rsa', {})
            self.channel_private_key = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC2GWk9HKsazGpLFujzqr3eVlvwjVLmfr/3C8C4gLGSGyiFGv0SU0slT8iMvnB5RlGfkHmYqNuSxVOwGRtRHs6Kv5A15duhL8K29lrfoeArF0vSBGx9viC+IvCgdXTsVbLqyK+Wo5mnBZPKRhjU3aJq2fyVr/wxDbkYUWN6iy+YhCptmkzZz7tA9NGoPa62XaMY759QYnzjpbu5UY+qcmTmAmfxizOW8GIeryY4b6//eskOYD3F0qfGfuAezZRqCZAfAK8NsTYCKPhhUtunqfq0QWAhYAPQhSGARkRoYKOBhCMIu0pqWJY+rvW6OGc72SrhVlSr9euYKqXpikXSTA27AgMBAAECggEABsuE80xWEC5vivTEZY9J/XlwfdXwMXyqUiAkpV3cAm00Al+C8QOdqrtC6wmSLdxTYGZmOy2V3/CwEkKlk83X/DJwwaodm3KqS+R+eJjUQhdg82nJ2JlXJHEuVHZ9kfIStpMdhjv9mE9rd+FMvOi2TlFrDPTfrr7p2L/0u9ZkxMadk1rTCJBqSSDe4FAxlxTT2LtvruZY8D/Vk49wlIeNc0VtiRRTM3qXQxRShWb6RwzL6+uQTa3kaJOPdkplhwAmo0BO9c++X1cV1CEfc1DFF7818CaRfWxAcp6Q9xEpLcs+V+gajaaLYmdNmRf8Hef75CUt5GpeYbxDT3U3zpoXVQKBgQDuZXl7cCDBqkvLmUql/65Wm+lSZKMA/ygSb8ejPE+gHOE1IQVwB65DawMkNHaQIg6nwtFQbMndX85rSY9lpcpv54WxB0TUfrWIWmh1T3qc9xlbtpPg3P5LBF9d6UcNOOINNrxBcVOL+MCYxGKnrYlrPOvAuYX/ohtW5R+nysX3xQKBgQDDi7lZ+3VqYP6MZgmaZvpdBZrn0K85Cvw9ecumMRefRo0ywu2vD/yV+CAJlNpvDdSARX0AyxCh8d4KmKWTRarUR7Y4X28iv3Asvw50U3OGF5HiQMRSr+3byK9OK4zrwujwzKm5LaoevnPv8dkuRMMGV2pP8jNU/6znGOD8KEzHfwKBgAKZ0tB48bKLNBZ9jqXu+yzwuIPwmyKopfxFge0S/F9n0UEuIgwN2WXc5gTgGacK6BQGeRgih7VFlU/wVoMqYuIDqZ670JFs7HgXXGpjOpg5zeoFPOnIH3IcExpIMEFBrJ2uSjGAlgPB6//+rIDd0ND9sijBHWgjkZ7KEyVWfgBtAoGAOzNU9SIE5STiS50ksSMWDw2AXUg3lDx4KyBxgCoCrczNOJ39GW/sl3acNGplSxPTztW6x3+y1GSGRYz7K7/+vO/NAfoailmM228oMB2HrwP5vZbAGQx8JXr3X+Idcs76eNRtWcuyYkZkkTMV/kUBCi1y2StJUSVqsjg8/PoybH8CgYBFAcsqHSBkP5R4/rrOJhLZBiaAqAq55PPBC/nwP4haDP0g1aS0TdPUY1I28bWpPwrYxIiFNuslgERcMSLUk9oR3Mbs6JOqImXqvry3n89qmEp645C5jlfjfhIIOggchD3wo7pfOP3JLzpO4kZ8M6Uvfgg7xA/9qjHufrlxPmLvjQ==" # 保持原有的私钥值
            self.channel_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAthlpPRyrGsxqSxbo86q93lZb8I1S5n6/9wvAuICxkhsohRr9ElNLJU/IjL5weUZRn5B5mKjbksVTsBkbUR7Oir+QNeXboS/CtvZa36HgKxdL0gRsfb4gviLwoHV07FWy6sivlqOZpwWTykYY1N2iatn8la/8MQ25GFFjeosvmIQqbZpM2c+7QPTRqD2utl2jGO+fUGJ846W7uVGPqnJk5gJn8YszlvBiHq8mOG+v/3rJDmA9xdKnxn7gHs2UagmQHwCvDbE2Aij4YVLbp6n6tEFgIWAD0IUhgEZEaGCjgYQjCLtKaliWPq71ujhnO9kq4VZUq/XrmCql6YpF0kwNuwIDAQAB"
            self.platform_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAriU/S6vaJIo51W4flYzfM+bXvsAC3zri+5mfLrj3cOX+zoFuIK9bVD3nQd8gDNcMIpBlZgmnY9YuLZ1/sdIGvnjakGGJuraipbvqhxqLHdbknQWgH+eE6unkxCuP8LA2HZIsy0eb/Sqb1/2t8zQdBY2sO3WC8hc4Wj/TixchYbZDUlgCuDvtxrtbWtHJdjsUwxslQi3qJjVdbd2k8k73CtH+eAP6gY8v9lcc5tW/KkzsZX05/WP1arOxalJuGoCq6mb0ttwthaVFjBxWWeJ2VWh0rGJjMUZrlK3gir8w7Qftlasf7MSmYjl/7LVc7lbTizL5LAdT6xJuK2WeUnZ4DQIDAQAB"
            self.platform_private_key = ""
        # 加载测试套件
        self.test_suite = TestSuite.from_yaml(self.test_cases_path)
        print(f"加载测试套件: {self.test_suite.name}")
        print(f"用例总数: {len(self.test_suite.cases)}")
        print(f"用例列表: {list(self.test_suite.cases.keys())}")
        # self.id_generator = SnowflakeGenerator(worker_id=1, datacenter_id=1)
        
    # def test_case_execution(self):
    #     """单次执行测试用例"""
    #     self.execute_test_suite()
        
    def test_concurrent_execution(self):
        """并发执行测试用例"""
        import concurrent.futures
        
        repeat_times = 10  # 可以后续改为从配置文件读取
        max_workers = 1
        expected_total_runs = repeat_times * max_workers
        
        total_results = {
            'total_runs': 0,          # 实际执行的总次数
            'successful_runs': 0,     # 完全成功的执行次数（所有用例都通过）
            'failed_runs': 0,         # 有任何用例失败的执行次数
            'total_cases': 0,         # 所有执行中的用例总数
            'passed_cases': 0,        # 所有执行中通过的用例数
            'failed_cases': 0,        # 所有执行中失败的用例数
            'failed_case_details': [] # 失败用例的详细信息
        }
        
        print(f"\n开始并发执行测试套件: {self.test_suite.name}")
        print(f"重复次数: {repeat_times}, 并发线程数: {max_workers}")
        print(f"预期总执行次数: {expected_total_runs}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.execute_test_suite)
                for _ in range(expected_total_runs)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    total_results['total_runs'] += 1
                    total_results['total_cases'] += result['total']
                    total_results['passed_cases'] += result['pass']
                    total_results['failed_cases'] += result['fail']
                    
                    # 如果这次执行所有用例都通过
                    if result['fail'] == 0:
                        total_results['successful_runs'] += 1
                    else:
                        total_results['failed_runs'] += 1
                        # 添加失败用例详情
                        total_results['failed_case_details'].extend(result['failed_cases'])
                        
                except Exception as e:
                    print(f"执行出错: {str(e)}")
                    total_results['total_runs'] += 1
                    total_results['failed_runs'] += 1
        
        # 打印总体执行报告
        print("\n并发执行总报告==================================")
        print(f"预期执行次数: {expected_total_runs}")
        print(f"实际执行次数: {total_results['total_runs']}")
        print(f"完全成功执行次数: {total_results['successful_runs']}")
        print(f"包含失败用例的执行次数: {total_results['failed_runs']}")
        print(f"总体成功率: {(total_results['successful_runs'] / total_results['total_runs'] * 100):.2f}%")
        
        print("\n用例级别统计:")
        print(f"用例总执行次数: {total_results['total_cases']}")
        print(f"用例通过次数: {total_results['passed_cases']}")
        print(f"用例失败次数: {total_results['failed_cases']}")
        print(f"用例通过率: {(total_results['passed_cases'] / total_results['total_cases'] * 100):.2f}%")
        
        if total_results['failed_case_details']:
            print("\n失败用例详情:")
            for case in total_results['failed_case_details']:
                print(f"用例ID: {case['case_id']}")
                print(f"用例名称: {case['name']}")
                print(f"错误信息: {case['error']}")
                print("------------------------")
        
        # 使用断言确保测试结果符合预期
        self.assertGreater(total_results['successful_runs'] / total_results['total_runs'], 0.8, 
                          "并发测试成功率低于80%")
        
    def execute_test_suite(self, timeout=30):
        """执行测试套件"""
        execution_order = self.test_suite.get_execution_order()
        client = HttpClient(timeout=timeout)
        test_results = {
            'total': len(execution_order),
            'pass': 0,
            'fail': 0,
            'failed_cases': []
        }
        
        print(f"\n开始执行测试套件: {self.test_suite.name}")
        
        # 按顺序执行测试用例
        for case_id in execution_order:
            case = None
            try:
                case = self.test_suite.cases[case_id]
                if case is None:
                    print(f"警告: 未找到用例ID {case_id}")
                    continue
                
                case.status = TestStatus.RUNNING
                print(f"\n执行测试用例: {case.name} ({case_id})")
                
                # 生成随机身份证号
                current_id_number = self.generate_random_id_number()
                print(f"\n本次迭代使用的身份证号: {current_id_number}")
                
                # 解析变量
                api_path = self.test_suite.resolve_variables(case.api_path)
                print(f"API路径: {api_path}")
                print(f"请求方法: {case.method}")
                
                # 处理请求体中的加密数据
                if isinstance(case.body, dict) and 'data' in case.body:
                    if 'userAuthInfo' in case.body['data'] and isinstance(case.body['data']['userAuthInfo'], dict):
                        case.body['data']['userAuthInfo']['idNo'] = current_id_number
                        birth_date = f"{current_id_number[6:10]}-{current_id_number[10:12]}-{current_id_number[12:14]}"
                        case.body['data']['userAuthInfo']['birthDay'] = birth_date
                        print(f"对应的出生日期: {birth_date}")
                    
                    if isinstance(case.body['data'], dict):
                        data_str = json.dumps(case.body['data'], separators=(',', ':'))
                        print(f"加密前的消息体: {data_str}")
                        
                        current_timestamp = int(time.time() * 1000)
                        case.body['timestamp'] = current_timestamp
                        
                        encrypted_data = RSAEncrypUtil.build_rsa_encrypt_by_public_key(
                            data_str,
                            self.platform_public_key
                        )
                        case.body['data'] = encrypted_data
                        case.body['sign'] = RSAEncrypUtil.build_rsa_sign_by_private_key(
                            encrypted_data,
                            self.channel_private_key
                        )
                
                # 执行请求
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
                
                # 验证响应
                if response.status_code == case.expected_status:
                    response_body = json.loads(response.body)
                    
                    # 验证响应格式
                    required_keys = ['code', 'data', 'sign']
                    if not all(key in response_body for key in required_keys):
                        raise ValueError("响应格式不符合要求")
                    
                    # 验证返回码
                    expected_code = case.expected_response.get('code', '000000')
                    if str(response_body['code']) != str(expected_code):
                        raise ValueError(f"业务返回码错误: {response_body['code']}")
                    
                    # 验证签名和处理响应数据
                    response_data = response_body['data']
                    verify_sign = RSAEncrypUtil.build_rsa_verify_by_public_key(
                        response_data,
                        self.platform_public_key,
                        response_body['sign']
                    )
                    
                    if not verify_sign:
                        raise ValueError("响应签名验证失败")
                    
                    # 解密响应数据
                    decrypted_data = RSAEncrypUtil.build_rsa_decrypt_by_private_key(
                        response_body['data'],
                        self.channel_private_key
                    )
                    decrypted_json = json.loads(decrypted_data)
                    
                    if case.expected_data['success'] != decrypted_json['success']:
                        raise ValueError("响应数据与预期不符")
                    
                    print(f"测试通过: {case.name}")
                    case.status = TestStatus.PASSED
                    test_results['pass'] += 1
                else:
                    raise ValueError(f"HTTP状态码错误: {response.status_code}")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"测试失败: {error_msg}")
                if case:
                    case.status = TestStatus.FAILED
                test_results['fail'] += 1
                test_results['failed_cases'].append({
                    'case_id': case_id,
                    'name': case.name if case else 'Unknown',
                    'error': error_msg
                })
        
        client.close()
        
        # 打印测试报告
        print("\n测试报告==================================")
        print(f"总用例数: {test_results['total']}")
        print(f"通过用例数: {test_results['pass']}")
        print(f"失败用例数: {test_results['fail']}")
        
        if test_results['failed_cases']:
            print("\n失败用例详情:")
            for failed_case in test_results['failed_cases']:
                print(f"用例ID: {failed_case['case_id']}")
                print(f"用例名称: {failed_case['name']}")
                print(f"错误信息: {failed_case['error']}")
                print("------------------------")
        
        return test_results

    def generate_random_id_number(self):
        """生成随机身份证号"""
        # 使用更多的地区码选项
        area_codes = [
            '110101', '110102', '110105', '110106', '110107', '110108', '110109', '110111',  # 北京
            '310101', '310104', '310105', '310106', '310107', '310109', '310110', '310112',  # 上海
            '440103', '440104', '440105', '440106', '440111', '440112', '440113', '440114',  # 广州
            '510104', '510105', '510106', '510107', '510108', '510112', '510113', '510114',  # 成都
        ]
        area_code = random.choice(area_codes)
        
        # 扩大出生日期范围(1960-2005年之间)
        year = str(random.randint(1960, 2005))
        month = str(random.randint(1, 12)).zfill(2)
        # 根据月份确定天数
        days_in_month = {
            '01': 31, '02': 29 if int(year) % 4 == 0 else 28,
            '03': 31, '04': 30, '05': 31, '06': 30,
            '07': 31, '08': 31, '09': 30, '10': 31,
            '11': 30, '12': 31
        }
        day = str(random.randint(1, days_in_month[month])).zfill(2)
        birth_date = f"{year}{month}{day}"
        
        # 扩大顺序码范围（3位数，包括000-999）
        sequence = str(random.randint(0, 999)).zfill(3)
        
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
