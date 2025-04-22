import unittest
import os
import sys
import time
import yaml
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from network.http_client import HttpClient
from ai.ai_service import AIService
from util.rsa_util import RSAEncrypUtil
from .test_suite import TestSuite
from .test_case import TestCase, TestStatus

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.current_time = time.strftime('%Y%m%d%H%M%S')
        self.test_cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tests', 'test_cases.yaml')
        self.ai_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'ai_config.yaml')
        self.rsa_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rsa_config.yaml')
        
        # 加载RSA配置
        with open(self.rsa_config_path, 'r', encoding='utf-8') as f:
            rsa_config = yaml.safe_load(f)
            channel_rsa = rsa_config.get('channel_rsa', {})
            # self.channel_private_key = channel_rsa.get('private_key', '')
            # self.channel_public_key = channel_rsa.get('public_key', '')
            self.channel_private_key = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCQczHYWPaUWuln7z97UawePimBjpa+XOG8t8e0Y33a8CybfsfImvQjw1kxIcRp9Q04tdyBS+8rzMRDj7POH89ewvLC/FDaV7ZnNUtYW3MYUOWYOi7AaVdM7SszQpWg2Cdw9v2q/Nfwlv6a6pLPYxZRuecgwdl1u8X7WeWZ7UX2wz3oVR3Exm5EtNwFysWS2vc8MrbW9AGyHaj5L5Wdy80Cwy3wZY/6dSqIS0MYPLhLPQOH7w/dELyoEfwNz6IUCCk1rbYjFJwI1gK72iGRdcs5P+0DHXzian9Nwalw8gT4TqasfGMyAOlCyNEJoI6VkY8Z8rt6dVsBoNt1Z+AGa6GBAgMBAAECggEAIUUO8XQIEwJfaOtfVTFp8atClw725FBzQ6qWihMyPRd9RrEsJaWe3o/TPrA202q4CVxFtdf99bobaC40bSDBe+Nt04AWxTtXjSzmtiqV9z9GqkmYVAPPMi4b+Zn36YxvhSK2KUhEGitE5/xoJPD/BoLJW6+aPPYrMumxKsNODnfv+AtD5k4vvkQH+fxn1VIQBBr5AuhzLVoDNdKe4X6wn2wXOMggIqwADmhbc/dJ0beCg91UuYsV1TTFzOh3rqv4XM2l57AXTFhZttY1r+7YckpFuK4siUWK0EjB5hyx9mGyyWvhpuiS14U4yCcCZMTb5vSlMMjMjtM6ml8Pzd7v+wKBgQDByBViJODsOVtsWWGYeqz9Yl5vrenDzZaerFDROFBWAKTe9oEgLx+hQhQHnNwCEKqNoZYPW+vAW9Nw/l3BjIP0886jYdsEtohPyZDIYoIwDgb4ySv7KbOhW59F+Lv1LGzi+u26+YJqY2n3dBl2vth8tK9lDgaIr5ANQNl5HE/KNwKBgQC+1EpZyD4SQ1ISUV9eMqFUuiyElz7d3G84GDZ6208291HhgK7e2cGTLAF9Mh2hgyVlgHSnR+8J2AImMFEgSZXGH8PXOoWLv1xxzx8ijavvnAbp8xHwTxiA0ol3nJAd+TijZD45UvBrP5l1PCcq58WRft8emfy1yJfMY46/KFa2BwKBgHD38e9bTHyqG3AY01qO+dZlyGQW4Ray/cHW9u5hhAP/MB6DWlem4SujWAXwHhpeGO+kadTeY5uqbKOMxp+VCUB9+dMpswMWXnUVLwCC3R6irtHOhYNQllXVEg86qGiP05Kncnv0BWF8P0RxPH8LVy2sMCwbdxesMbBoQ9/k72cVAoGACSbXNf0TdP7DhdtfLn5RHGYdUnKKcktrDg6jNjskTmeIBr+MI2XgEbXPkHiB0Ugf2AFUFt2tShSQ7dHtYhYFV84YL09ALlaMEW00egy/TSt3bWrZ1mOEslDmhNT+WGGmZLefAFLI8uvG6UdsPXOGFxc1jhsmcnVfSk8P/nzpw6sCgYAiZtvYbvS8YZloZfYLJHTd98lFvVQ47uB7IJJt3JFarDI7Cr1NV+B4lQrgn5TLe086m0+I2+9rarwJGFbfAR1k9r2bAoOX7cq0Cqj/jyzrb1SbOy45yGDco42i57xtjLdmQroSLbdqn7oJM5PXt/OfJETE2dbgooy17dtvKBCrHw=="
            self.channel_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkHMx2Fj2lFrpZ+8/e1GsHj4pgY6WvlzhvLfHtGN92vAsm37HyJr0I8NZMSHEafUNOLXcgUvvK8zEQ4+zzh/PXsLywvxQ2le2ZzVLWFtzGFDlmDouwGlXTO0rM0KVoNgncPb9qvzX8Jb+muqSz2MWUbnnIMHZdbvF+1nlme1F9sM96FUdxMZuRLTcBcrFktr3PDK21vQBsh2o+S+VncvNAsMt8GWP+nUqiEtDGDy4Sz0Dh+8P3RC8qBH8Dc+iFAgpNa22IxScCNYCu9ohkXXLOT/tAx184mp/TcGpcPIE+E6mrHxjMgDpQsjRCaCOlZGPGfK7enVbAaDbdWfgBmuhgQIDAQAB"
            # 平台密钥对
            self.platform_private_key = "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCuJT9Lq9okijnVbh+VjN8z5te+wALfOuL7mZ8uuPdw5f7OgW4gr1tUPedB3yAM1wwikGVmCadj1i4tnX+x0ga+eNqQYYm6tqKlu+qHGosd1uSdBaAf54Tq6eTEK4/wsDYdkizLR5v9KpvX/a3zNB0Fjaw7dYLyFzhaP9OLFyFhtkNSWAK4O+3Gu1ta0cl2OxTDGyVCLeomNV1t3aTyTvcK0f54A/qBjy/2Vxzm1b8qTOxlfTn9Y/Vqs7FqUm4agKrqZvS23C2FpUWMHFZZ4nZVaHSsYmMxRmuUreCKvzDtB+2Vqx/sxKZiOX/stVzuVtOLMvksB1PrEm4rZZ5SdngNAgMBAAECggEAIusbDvxNiGgjApXLRXxywQB3oCr2KHaxTsvV7FNwYjXr6tJvF6SxxmmHNmEcFxcDuuaDPnuPEei/Z6weD7TSX1zyTmMQb9zxLhRJCYAcBwaw3n9jRSJyN3xgv6kQeq2KnFFUJAqez5u8lgmq2IpJi3SF5YJBmHNpfEcyDsC7k9DYbtpymqKdryBlLhUNS/nTf+LqTQecaTGWDQfatYIuQF+fzOLwGYDagQzaKsuH520rZu74+skZQxmMl6TlLX+lUW2eiS0kTlzUNopqcJsKhkAaRz7fi1C5zsCARa5MiPjapzA1DWY4x/QUPjxa5uv9i9u+x270Gz/T0x1XtquhoQKBgQDVdVGmuU+2bzv/Uhx7U5Ha+/vNZaNR78UTMlFbXgSL3M9JnLK/F5uDwv+tBJSXotPI4pXW2foq93Qb4UbeegjYNvJpM0u7YQ69wWPCEfAuGbFZovtGHn5wkt5N37hZWgDO/g+EE9LhhjTkMxtrYNvPP9wEFOHhv3km1smx+GKR5QKBgQDQ2i7U/aH3wsInaBAyPPBDgSN4M3emg/kerjcQJGTW8BoyetU8VyJUXM9Hro7Kx+o6thK79P0L//ue8N6VNdAdVNFVcEjJCbOauGCLfqPFaZ6qhu98GRt0SVvL+kiqCrsmnhkF2e6+9Apy4vyhts1Gpkp1J7XZJJs5rOnKziiLCQKBgQCaZrM6Iv8K2mkOpSle97MgMHcSOnupcAMggJwit94YAQ+bkpIk8YGXDHz+fLqy+J+yxltWPvPbEoVVCV3G3YT6SLyN5gHYtzr/fRyYq3sNDZ6gVOjm7nXNHh9ZOwNQ9m5xS4qTofc/FGG700/5GuXEgs+10BkXvvV2Z5Ube6xpFQKBgQC1JxqJ+jlb2x1m6tdpi/vmwYOPhizZTQ1vNDNkl/yzhm1irbJ5dSa8wAe2qE0IzKB5LmZPi69VkkKhWVHnYFbUqjYsgolPf0+++wAa3syUtgk+5m2hWXG7ysmJwtz2SPqOA4G21pJEJQ9PGV2BszqYdjKNLdWItDzDqRzcoTb/aQKBgQDNpwzuPMIKIC77I6nY2QIKPT+Q4Kkyr4D9bw47jjE1L4RtlO0GHBjJl30C5ACK7sQygMOQepwYJz7qmH0j75tR+gfjz4t5HJWDyW3AdpB4a3LPwCv2vMKLRi4IYHwzDaL6V1q6tx2snlnNkEM3Cj5UoaSUQ/+NZ/euE2oxaAOBgw=="
            self.platform_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAriU/S6vaJIo51W4flYzfM+bXvsAC3zri+5mfLrj3cOX+zoFuIK9bVD3nQd8gDNcMIpBlZgmnY9YuLZ1/sdIGvnjakGGJuraipbvqhxqLHdbknQWgH+eE6unkxCuP8LA2HZIsy0eb/Sqb1/2t8zQdBY2sO3WC8hc4Wj/TixchYbZDUlgCuDvtxrtbWtHJdjsUwxslQi3qJjVdbd2k8k73CtH+eAP6gY8v9lcc5tW/KkzsZX05/WP1arOxalJuGoCq6mb0ttwthaVFjBxWWeJ2VWh0rGJjMUZrlK3gir8w7Qftlasf7MSmYjl/7LVc7lbTizL5LAdT6xJuK2WeUnZ4DQIDAQAB"
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
                # 获取当前时间戳
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
            
            print(f"请求消息体: {case}")
            
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
                        print(f"响应消息体: {response_body}")
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
                        print(f"响应数据: {response_data}")
                        print(f"签名: {response_body['sign']}")
                        print(f"平台公钥: {self.platform_public_key[:30]}...")
                        
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
                            # 解密响应数据
                            decrypted_data = RSAEncrypUtil.build_rsa_decrypt_by_private_key(
                                response_body['data'],
                                self.channel_private_key
                            )
                            # 解析解密后的JSON数据
                            decrypted_json = json.loads(decrypted_data)
                            print(f"解密后的action数据: {decrypted_json['checkLoan']}")
                            print(f"预期数据: {case.expected_data['checkLoan']}")
                            
                            # 验证解密后的数据结构是否符合预期
                            if case.expected_data['checkLoan'] != decrypted_json['checkLoan']:
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
            
            test_results['total'] += 1
        
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


if __name__ == '__main__':
    unittest.main()
