import base64
from typing import Dict, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key, load_der_public_key

CHARSET = 'utf-8'
ALGORITHM_RSA = 'RSA'
ALGORITHM_RSA_PRIVATE_KEY_LENGTH = 2048
ALGORITHM_RSA_SIGN = "SHA256withRSA"

class RSAEncrypUtil:

    @staticmethod
    def build_rsa_encrypt_by_public_key(data: str, key: str) -> str:
        """
        RSA算法公钥加密数据
        :param data: 待加密的明文字符串
        :param key: RSA公钥字符串(Base64编码)
        :return: RSA公钥加密后的经过Base64编码的密文字符串
        """
        try:
            # 直接解码Base64公钥
            public_key_bytes = base64.b64decode(key)
            public_key = serialization.load_der_public_key(public_key_bytes)

            # 加密数据
            data_bytes = data.encode(CHARSET)
            encrypted = public_key.encrypt(
                data_bytes,
                padding.PKCS1v15()
            )
            return base64.b64encode(encrypted).decode(CHARSET)
        except Exception as e:
            raise RuntimeError(f'加密字符串[{data}]时遇到异常') from e

    @staticmethod
    def build_rsa_decrypt_by_public_key(data: str, key: str) -> str:
        """
        RSA算法公钥解密数据
        :param data: 待解密的经过Base64编码的密文字符串
        :param key: RSA公钥字符串
        :return: RSA公钥解密后的明文字符串
        """
        try:
            # 解码Base64编码的公钥
            public_key_bytes = base64.b64decode(key.encode(CHARSET))
            public_key = load_pem_public_key(public_key_bytes)

            # 解密数据
            encrypted_data = base64.b64decode(data.encode(CHARSET))
            decrypted = RSAEncrypUtil._rsa_split_codec(public_key, encrypted_data, False)
            return decrypted.decode(CHARSET)
        except Exception as e:
            raise RuntimeError(f'解密字符串[{data}]时遇到异常') from e

    @staticmethod
    def build_rsa_encrypt_by_private_key(data: str, key: str) -> str:
        """
        RSA算法私钥加密数据
        :param data: 待加密的明文字符串
        :param key: RSA私钥字符串
        :return: RSA私钥加密后的经过Base64编码的密文字符串
        """
        try:
            # 解码Base64编码的私钥
            private_key_bytes = base64.b64decode(key.encode(CHARSET))
            private_key = load_pem_private_key(private_key_bytes, password=None)

            # 加密数据
            data_bytes = data.encode(CHARSET)
            encrypted = RSAEncrypUtil._rsa_split_codec(private_key, data_bytes, True)
            return base64.b64encode(encrypted).decode(CHARSET)
        except Exception as e:
            raise RuntimeError(f'加密字符串[{data}]时遇到异常') from e

    
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    import base64
    @staticmethod
    def build_rsa_decrypt_by_private_key(encrypted_data: str, private_key: str) -> str:
        """
        使用RSA私钥解密数据
        :param encrypted_data: Base64编码的加密数据
        :param private_key: Base64编码的RSA私钥(纯字符串格式)
        :return: 解密后的字符串
        """
        try:
            # 处理URL-safe的Base64编码的加密数据
            encrypted_data = encrypted_data.replace('-', '+').replace('_', '/')
            missing_padding = len(encrypted_data) % 4
            if missing_padding:
                encrypted_data += '=' * (4 - missing_padding)
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # 解码Base64格式的私钥
            private_key_bytes = base64.b64decode(private_key)
            
            # 使用DER格式加载私钥
            private_key_obj = serialization.load_der_private_key(
                private_key_bytes,
                password=None
            )
            
            # 使用PKCS1v15填充方案进行解密
            decrypted_data = private_key_obj.decrypt(
                encrypted_bytes,
                padding.PKCS1v15()
            )
            
            return decrypted_data.decode(CHARSET)
        except Exception as e:
            print(f"解密失败详细信息: {str(e)}")
            print(f"加密数据长度: {len(encrypted_bytes)}")
            print(f"私钥长度: {len(private_key_bytes)}")
            raise RuntimeError(f"解密失败: {str(e)}")
    # def build_rsa_decrypt_by_private_key(data: str, key: str) -> str:
    #     """
    #     RSA算法私钥解密数据
    #     :param data: 待解密的经过Base64编码的密文字符串
    #     :param key: RSA私钥字符串(PEM格式)
    #     :return: RSA私钥解密后的明文字符串
    #     """
    #     try:
    #         # 直接加载PEM格式的私钥
    #         private_key = load_pem_private_key(key.encode(CHARSET), password=None)

    #         # 解密数据
    #         encrypted_data = base64.b64decode(data.encode(CHARSET))
    #         decrypted = RSAEncrypUtil._rsa_split_codec(private_key, encrypted_data, False)
    #         return decrypted.decode(CHARSET)
    #     except Exception as e:
    #         raise RuntimeError(f'解密字符串[{data}]时遇到异常') from e

   
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    import base64

    ALGORITHM_RSA_SIGN = "SHA256withRSA"
    CHARSET = "UTF-8"
    @staticmethod
    def build_rsa_sign_by_private_key(data: str, key: str) -> str:
        """
        RSA算法使用私钥对数据生成数字签名
        :param data: 待签名的明文字符串
        :param key: RSA私钥字符串(Base64编码)
        :return: RSA私钥签名后的经过Base64编码的字符串
        """
        try:
            # 直接解码Base64私钥
            private_key_bytes = base64.b64decode(key)
            private_key = serialization.load_der_private_key(private_key_bytes, password=None)
            
            # 生成签名
            signature = private_key.sign(
                data.encode(CHARSET),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # 进行Base64编码
            return base64.b64encode(signature).decode(CHARSET)
            
        except Exception as e:
            raise RuntimeError(f'签名字符串[{data}]时遇到异常') from e
            
    @staticmethod
    def build_rsa_verify_by_public_key(data: str, key: str, sign: str) -> bool:
        """
        RSA算法使用公钥验证签名
        :param data: 原始数据
        :param key: RSA公钥字符串(Base64编码)
        :param sign: 签名字符串(Base64编码)
        :return: 验证结果，True表示验证通过，False表示验证失败
        """
        try:
            # 解码Base64公钥
            public_key_bytes = base64.b64decode(key)
            public_key = serialization.load_der_public_key(public_key_bytes)
            
            # 处理URL-safe的Base64编码的签名
            sign = sign.replace('-', '+').replace('_', '/')
            missing_padding = len(sign) % 4
            if missing_padding:
                sign += '=' * (4 - missing_padding)
            
            # 解码签名
            signature = base64.b64decode(sign)
            
            # 验证签名
            try:
                public_key.verify(
                    signature,
                    data.encode(CHARSET),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True
            except InvalidSignature:
                return False
        except Exception as e:
            print(f"验证签名失败: {str(e)}")
            return False

        # 使用示例：
        # private_key_pem = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCQczHYWPaUWuln..."  # PKCS#8格式私钥
        # signed_data = build_rsa_sign_by_private_key("待签名数据", private_key_pem)
        # print(signed_data)
   

    
    import base64
    import logging
    from io import BytesIO
    
    # 导入所需的模块
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
    from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5
    from Crypto.Hash import SHA256

    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 常量定义
    CHARSET = 'utf-8'
    ALGORITHM_RSA = 'RSA'
    ALGORITHM_RSA_PRIVATE_KEY_LENGTH = 2048
    ALGORITHM_RSA_SIGN = "SHA256withRSA"

    class RSAEncrypUtil:
        """
        RSA加解密工具类（生成公私密钥对，公私密钥加解密，生成签名，验签）
        """
        
        # 字符集
        CHARSET = 'utf-8'
        
        # 密钥算法
        ALGORITHM_RSA = "RSA"
        
        # 签名算法
        ALGORITHM_RSA_SIGN = "SHA256"
        
        # 密钥长度
        ALGORITHM_RSA_PRIVATE_KEY_LENGTH = 2048
        
        @staticmethod
        def init_rsa_key():
            """
            初始化RSA算法生成密钥对
            
            Returns:
                dict: 经过Base64编码后的公私钥Map, 键名分别为publicKey和privateKey
            """
            # 生成RSA密钥对
            key = RSA.generate(ALGORITHM_RSA_PRIVATE_KEY_LENGTH)
            
            # 获取私钥
            private_key = key.export_key()
            private_key_str = base64.urlsafe_b64encode(private_key).decode(CHARSET)
            
            # 获取公钥
            public_key = key.publickey().export_key()
            public_key_str = base64.urlsafe_b64encode(public_key).decode(CHARSET)
            
            # 返回密钥对
            key_pair_map = {
                "publicKey": public_key_str,
                "privateKey": private_key_str
            }
            return key_pair_map
        
        @staticmethod
        def _get_public_key(key):
            """
            从Base64编码的字符串中获取公钥
            
            Args:
                key: Base64编码的公钥字符串
                
            Returns:
                公钥对象
            """
            key_bytes = base64.b64decode(key)
            return RSA.import_key(key_bytes)
        
        @staticmethod
        def _get_private_key(key):
            """
            从Base64编码的字符串中获取私钥
            
            Args:
                key: Base64编码的私钥字符串
                
            Returns:
                私钥对象
            """
            key_bytes = base64.b64decode(key)
            return RSA.import_key(key_bytes)
        
        @staticmethod
        def build_rsa_encrypt_by_public_key(data, key):
            """
            RSA算法公钥加密数据
            
            Args:
                data: 待加密的明文字符串
                key: RSA公钥字符串
                
            Returns:
                RSA公钥加密后的经过Base64编码的密文字符串
            """
            try:
                # 获取公钥
                public_key = RSAEncrypUtil._get_public_key(key)
                
                # 将字符串转换为字节
                data_bytes = data.encode(CHARSET)
                
                # 分段加密
                cipher = Cipher_PKCS1_v1_5.new(public_key)
                block_size = RSAEncrypUtil.ALGORITHM_RSA_PRIVATE_KEY_LENGTH // 8 - 11
                
                output = BytesIO()
                for i in range(0, len(data_bytes), block_size):
                    block = data_bytes[i:i + block_size]
                    encrypted_block = cipher.encrypt(block)
                    output.write(encrypted_block)
                
                encrypted_data = output.getvalue()
                return base64.urlsafe_b64encode(encrypted_data).decode(CHARSET)
            except Exception as e:
                raise RuntimeError(f"加密字符串[{data}]时遇到异常: {str(e)}")
        
        @staticmethod
        def build_rsa_decrypt_by_private_key(data, key):
            """
            RSA算法私钥解密数据
            
            Args:
                data: 待解密的经过Base64编码的密文字符串
                key: RSA私钥字符串
                
            Returns:
                RSA私钥解密后的明文字符串
            """
            try:
                # 获取私钥
                private_key = RSAEncrypUtil._get_private_key(key)
                
                # 解码Base64
                data_bytes = base64.urlsafe_b64decode(data)
                
                # 分段解密
                cipher = Cipher_PKCS1_v1_5.new(private_key)
                block_size = RSAEncrypUtil.ALGORITHM_RSA_PRIVATE_KEY_LENGTH // 8
                
                output = BytesIO()
                for i in range(0, len(data_bytes), block_size):
                    block = data_bytes[i:i + block_size]
                    decrypted_block = cipher.decrypt(block, b'ERROR')
                    output.write(decrypted_block)
                
                decrypted_data = output.getvalue()
                return decrypted_data.decode(CHARSET)
            except Exception as e:
                logger.error(f"解密失败详细信息: {str(e)}")
                logger.error(f"加密数据长度: {len(data_bytes)}")
                raise RuntimeError(f"解密失败: {str(e)}")
        
        @staticmethod
        def build_rsa_sign_by_private_key(data, key):
            """
            RSA算法使用私钥对数据生成数字签名
            
            Args:
                data: 待签名的明文字符串
                key: RSA私钥字符串(Base64编码)
                
            Returns:
                RSA私钥签名后的经过Base64编码的字符串
            """
            try:
                # 获取私钥
                private_key = RSAEncrypUtil._get_private_key(key)
                
                # 计算哈希
                h = SHA256.new(data.encode(CHARSET))
                
                # 签名
                signer = Signature_PKCS1_v1_5.new(private_key)
                signature = signer.sign(h)
                
                # 返回Base64编码的签名
                return base64.b64encode(signature).decode(CHARSET)
            except Exception as e:
                raise RuntimeError(f"签名字符串[{data}]时遇到异常: {str(e)}")
        
        @staticmethod
        def build_rsa_verify_by_public_key(data, key, sign):
            """
            RSA算法使用公钥验证签名
            
            Args:
                data: 原始数据
                key: RSA公钥字符串(Base64编码)
                sign: 签名字符串(Base64编码)
                
            Returns:
                验证结果，True表示验证通过，False表示验证失败
            """
            try:
                # 获取公钥
                public_key = RSAEncrypUtil._get_public_key(key)
                
                # 计算哈希
                h = SHA256.new(data.encode(CHARSET))
                
                # 解码签名
                signature = base64.b64decode(sign)
                
                # 验证签名
                verifier = Signature_PKCS1_v1_5.new(public_key)
                return verifier.verify(h, signature)
            except Exception as e:
                logger.error(f"验证签名失败: {str(e)}")
                return False


    if __name__ == '__main__':
        # 测试代码
        # channel_rsa_key = RSAEncrypUtil.init_rsa_key()
        # platform_rsa_key = RSAEncrypUtil.init_rsa_key()
        # channel_private_key = channel_rsa_key['privateKey']
        # channel_public_key = channel_rsa_key['publicKey']
        # platform_private_key = platform_rsa_key['privateKey']
        # platform_public_key = platform_rsa_key['publicKey']
        channel_private_key = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCQczHYWPaUWuln7z97UawePimBjpa+XOG8t8e0Y33a8CybfsfImvQjw1kxIcRp9Q04tdyBS+8rzMRDj7POH89ewvLC/FDaV7ZnNUtYW3MYUOWYOi7AaVdM7SszQpWg2Cdw9v2q/Nfwlv6a6pLPYxZRuecgwdl1u8X7WeWZ7UX2wz3oVR3Exm5EtNwFysWS2vc8MrbW9AGyHaj5L5Wdy80Cwy3wZY/6dSqIS0MYPLhLPQOH7w/dELyoEfwNz6IUCCk1rbYjFJwI1gK72iGRdcs5P+0DHXzian9Nwalw8gT4TqasfGMyAOlCyNEJoI6VkY8Z8rt6dVsBoNt1Z+AGa6GBAgMBAAECggEAIUUO8XQIEwJfaOtfVTFp8atClw725FBzQ6qWihMyPRd9RrEsJaWe3o/TPrA202q4CVxFtdf99bobaC40bSDBe+Nt04AWxTtXjSzmtiqV9z9GqkmYVAPPMi4b+Zn36YxvhSK2KUhEGitE5/xoJPD/BoLJW6+aPPYrMumxKsNODnfv+AtD5k4vvkQH+fxn1VIQBBr5AuhzLVoDNdKe4X6wn2wXOMggIqwADmhbc/dJ0beCg91UuYsV1TTFzOh3rqv4XM2l57AXTFhZttY1r+7YckpFuK4siUWK0EjB5hyx9mGyyWvhpuiS14U4yCcCZMTb5vSlMMjMjtM6ml8Pzd7v+wKBgQDByBViJODsOVtsWWGYeqz9Yl5vrenDzZaerFDROFBWAKTe9oEgLx+hQhQHnNwCEKqNoZYPW+vAW9Nw/l3BjIP0886jYdsEtohPyZDIYoIwDgb4ySv7KbOhW59F+Lv1LGzi+u26+YJqY2n3dBl2vth8tK9lDgaIr5ANQNl5HE/KNwKBgQC+1EpZyD4SQ1ISUV9eMqFUuiyElz7d3G84GDZ6208291HhgK7e2cGTLAF9Mh2hgyVlgHSnR+8J2AImMFEgSZXGH8PXOoWLv1xxzx8ijavvnAbp8xHwTxiA0ol3nJAd+TijZD45UvBrP5l1PCcq58WRft8emfy1yJfMY46/KFa2BwKBgHD38e9bTHyqG3AY01qO+dZlyGQW4Ray/cHW9u5hhAP/MB6DWlem4SujWAXwHhpeGO+kadTeY5uqbKOMxp+VCUB9+dMpswMWXnUVLwCC3R6irtHOhYNQllXVEg86qGiP05Kncnv0BWF8P0RxPH8LVy2sMCwbdxesMbBoQ9/k72cVAoGACSbXNf0TdP7DhdtfLn5RHGYdUnKKcktrDg6jNjskTmeIBr+MI2XgEbXPkHiB0Ugf2AFUFt2tShSQ7dHtYhYFV84YL09ALlaMEW00egy/TSt3bWrZ1mOEslDmhNT+WGGmZLefAFLI8uvG6UdsPXOGFxc1jhsmcnVfSk8P/nzpw6sCgYAiZtvYbvS8YZloZfYLJHTd98lFvVQ47uB7IJJt3JFarDI7Cr1NV+B4lQrgn5TLe086m0+I2+9rarwJGFbfAR1k9r2bAoOX7cq0Cqj/jyzrb1SbOy45yGDco42i57xtjLdmQroSLbdqn7oJM5PXt/OfJETE2dbgooy17dtvKBCrHw=="
        channel_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkHMx2Fj2lFrpZ+8/e1GsHj4pgY6WvlzhvLfHtGN92vAsm37HyJr0I8NZMSHEafUNOLXcgUvvK8zEQ4+zzh/PXsLywvxQ2le2ZzVLWFtzGFDlmDouwGlXTO0rM0KVoNgncPb9qvzX8Jb+muqSz2MWUbnnIMHZdbvF+1nlme1F9sM96FUdxMZuRLTcBcrFktr3PDK21vQBsh2o+S+VncvNAsMt8GWP+nUqiEtDGDy4Sz0Dh+8P3RC8qBH8Dc+iFAgpNa22IxScCNYCu9ohkXXLOT/tAx184mp/TcGpcPIE+E6mrHxjMgDpQsjRCaCOlZGPGfK7enVbAaDbdWfgBmuhgQIDAQAB"
        # 平台密钥对
        platform_private_key = "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCuJT9Lq9okijnVbh+VjN8z5te+wALfOuL7mZ8uuPdw5f7OgW4gr1tUPedB3yAM1wwikGVmCadj1i4tnX+x0ga+eNqQYYm6tqKlu+qHGosd1uSdBaAf54Tq6eTEK4/wsDYdkizLR5v9KpvX/a3zNB0Fjaw7dYLyFzhaP9OLFyFhtkNSWAK4O+3Gu1ta0cl2OxTDGyVCLeomNV1t3aTyTvcK0f54A/qBjy/2Vxzm1b8qTOxlfTn9Y/Vqs7FqUm4agKrqZvS23C2FpUWMHFZZ4nZVaHSsYmMxRmuUreCKvzDtB+2Vqx/sxKZiOX/stVzuVtOLMvksB1PrEm4rZZ5SdngNAgMBAAECggEAIusbDvxNiGgjApXLRXxywQB3oCr2KHaxTsvV7FNwYjXr6tJvF6SxxmmHNmEcFxcDuuaDPnuPEei/Z6weD7TSX1zyTmMQb9zxLhRJCYAcBwaw3n9jRSJyN3xgv6kQeq2KnFFUJAqez5u8lgmq2IpJi3SF5YJBmHNpfEcyDsC7k9DYbtpymqKdryBlLhUNS/nTf+LqTQecaTGWDQfatYIuQF+fzOLwGYDagQzaKsuH520rZu74+skZQxmMl6TlLX+lUW2eiS0kTlzUNopqcJsKhkAaRz7fi1C5zsCARa5MiPjapzA1DWY4x/QUPjxa5uv9i9u+x270Gz/T0x1XtquhoQKBgQDVdVGmuU+2bzv/Uhx7U5Ha+/vNZaNR78UTMlFbXgSL3M9JnLK/F5uDwv+tBJSXotPI4pXW2foq93Qb4UbeegjYNvJpM0u7YQ69wWPCEfAuGbFZovtGHn5wkt5N37hZWgDO/g+EE9LhhjTkMxtrYNvPP9wEFOHhv3km1smx+GKR5QKBgQDQ2i7U/aH3wsInaBAyPPBDgSN4M3emg/kerjcQJGTW8BoyetU8VyJUXM9Hro7Kx+o6thK79P0L//ue8N6VNdAdVNFVcEjJCbOauGCLfqPFaZ6qhu98GRt0SVvL+kiqCrsmnhkF2e6+9Apy4vyhts1Gpkp1J7XZJJs5rOnKziiLCQKBgQCaZrM6Iv8K2mkOpSle97MgMHcSOnupcAMggJwit94YAQ+bkpIk8YGXDHz+fLqy+J+yxltWPvPbEoVVCV3G3YT6SLyN5gHYtzr/fRyYq3sNDZ6gVOjm7nXNHh9ZOwNQ9m5xS4qTofc/FGG700/5GuXEgs+10BkXvvV2Z5Ube6xpFQKBgQC1JxqJ+jlb2x1m6tdpi/vmwYOPhizZTQ1vNDNkl/yzhm1irbJ5dSa8wAe2qE0IzKB5LmZPi69VkkKhWVHnYFbUqjYsgolPf0+++wAa3syUtgk+5m2hWXG7ysmJwtz2SPqOA4G21pJEJQ9PGV2BszqYdjKNLdWItDzDqRzcoTb/aQKBgQDNpwzuPMIKIC77I6nY2QIKPT+Q4Kkyr4D9bw47jjE1L4RtlO0GHBjJl30C5ACK7sQygMOQepwYJz7qmH0j75tR+gfjz4t5HJWDyW3AdpB4a3LPwCv2vMKLRi4IYHwzDaL6V1q6tx2snlnNkEM3Cj5UoaSUQ/+NZ/euE2oxaAOBgw=="
        platform_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAriU/S6vaJIo51W4flYzfM+bXvsAC3zri+5mfLrj3cOX+zoFuIK9bVD3nQd8gDNcMIpBlZgmnY9YuLZ1/sdIGvnjakGGJuraipbvqhxqLHdbknQWgH+eE6unkxCuP8LA2HZIsy0eb/Sqb1/2t8zQdBY2sO3WC8hc4Wj/TixchYbZDUlgCuDvtxrtbWtHJdjsUwxslQi3qJjVdbd2k8k73CtH+eAP6gY8v9lcc5tW/KkzsZX05/WP1arOxalJuGoCq6mb0ttwthaVFjBxWWeJ2VWh0rGJjMUZrlK3gir8w7Qftlasf7MSmYjl/7LVc7lbTizL5LAdT6xJuK2WeUnZ4DQIDAQAB"
        test_data = '{"test":"test"}'
    
        # 加密和签名
        encrypt_data = RSAEncrypUtil.build_rsa_encrypt_by_public_key(test_data, platform_public_key)
        sign = RSAEncrypUtil.build_rsa_sign_by_private_key(encrypt_data, channel_private_key)
    
        # 验签和解密
        verify_sign = RSAEncrypUtil.build_rsa_verify_by_public_key(encrypt_data, channel_public_key, sign)
        if not verify_sign:
            print('验签失败')
        else:
            print('验签成功')
        decrypt_data = RSAEncrypUtil.build_rsa_decrypt_by_private_key(encrypt_data, platform_private_key)
        print(f'decrypt_data: {decrypt_data}')
        assert decrypt_data == test_data, '解密数据与原始数据不匹配'
