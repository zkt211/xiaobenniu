import lombok.extern.slf4j.Slf4j;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.IOUtils;
import org.springframework.util.Assert;

import javax.crypto.Cipher;
import java.io.ByteArrayOutputStream;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.HashMap;
import java.util.Map;

/**
 * RSA加解密工具类（生成公私密钥对，公私密钥加解密，生成签名，验签）
 *
 * @author air
 * @since 2025/02/21
 */
@Slf4j
public final class RSAEncrypUtil {
    public static final Charset CHARSET = StandardCharsets.UTF_8;

    /**
     * 密钥算法
     */
    public static final String ALGORITHM_RSA = "RSA";

    public static final String ALGORITHM_RSA_SIGN = "SHA256WithRSA";

    /**
     * 密钥长度
     */
    public static final int ALGORITHM_RSA_PRIVATE_KEY_LENGTH = 2048;

    private RSAEncrypUtil() {

    }

    /**
     * 初始化RSA算法生成密钥对
     *
     * @return 经过Base64编码后的公私钥Map, 键名分别为publicKey和privateKey
     */
    public static Map<String, String> initRSAKey() {
        // 为RSA算法创建一个KeyPairGenerator对象
        KeyPairGenerator kpg;
        try {
            kpg = KeyPairGenerator.getInstance(ALGORITHM_RSA);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalArgumentException("No such algorithm-->[" + ALGORITHM_RSA + "]");
        }
        // 初始化KeyPairGenerator对象,
        kpg.initialize(ALGORITHM_RSA_PRIVATE_KEY_LENGTH);
        // 生成密匙对
        KeyPair keyPair = kpg.generateKeyPair();
        // 得到公钥
        Key publicKey = keyPair.getPublic();
        String publicKeyStr = Base64.encodeBase64URLSafeString(publicKey.getEncoded());
        // 得到私钥
        Key privateKey = keyPair.getPrivate();
        String privateKeyStr = Base64.encodeBase64URLSafeString(privateKey.getEncoded());
        Map<String, String> keyPairMap = new HashMap<>();
        keyPairMap.put("publicKey", publicKeyStr);
        keyPairMap.put("privateKey", privateKeyStr);
        return keyPairMap;
    }

    /**
     * RSA算法公钥加密数据
     *
     * @param data 待加密的明文字符串
     * @param key  RSA公钥字符串
     * @return RSA公钥加密后的经过Base64编码的密文字符串
     */
    public static String buildRSAEncryptByPublicKey(String data, String key) {
        try {
            // 通过X509编码的Key指令获得公钥对象
            X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(Base64.decodeBase64(key));
            KeyFactory keyFactory = KeyFactory.getInstance(ALGORITHM_RSA);
            Key publicKey = keyFactory.generatePublic(x509KeySpec);
            // encrypt
            Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
            cipher.init(Cipher.ENCRYPT_MODE, publicKey);
            return Base64.encodeBase64URLSafeString(
                    rsaSplitCodec(cipher, Cipher.ENCRYPT_MODE, data.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
            throw new RunException("加密字符串[" + data + "]时遇到异常", e);
        }
    }

    /**
     * RSA算法公钥解密数据
     *
     * @param data 待解密的经过Base64编码的密文字符串
     * @param key  RSA公钥字符串
     * @return RSA公钥解密后的明文字符串
     */
    public static String buildRSADecryptByPublicKey(String data, String key) {
        try {
            // 通过X509编码的Key指令获得公钥对象
            X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(Base64.decodeBase64(key));
            KeyFactory keyFactory = KeyFactory.getInstance(ALGORITHM_RSA);
            Key publicKey = keyFactory.generatePublic(x509KeySpec);
            // decrypt
            Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
            cipher.init(Cipher.DECRYPT_MODE, publicKey);
            return new String(rsaSplitCodec(cipher, Cipher.DECRYPT_MODE, Base64.decodeBase64(data)), CHARSET);
        } catch (Exception e) {
            throw new RunException("解密字符串[" + data + "]时遇到异常", e);
        }
    }

    /**
     * RSA算法私钥加密数据
     *
     * @param data 待加密的明文字符串
     * @param key  RSA私钥字符串
     * @return RSA私钥加密后的经过Base64编码的密文字符串
     */
    public static String buildRSAEncryptByPrivateKey(String data, String key) {
        try {
            // 通过PKCS#8编码的Key指令获得私钥对象
            PKCS8EncodedKeySpec pkcs8KeySpec = new PKCS8EncodedKeySpec(Base64.decodeBase64(key));
            KeyFactory keyFactory = KeyFactory.getInstance(ALGORITHM_RSA);
            Key privateKey = keyFactory.generatePrivate(pkcs8KeySpec);
            // encrypt
            Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
            cipher.init(Cipher.ENCRYPT_MODE, privateKey);
            return Base64.encodeBase64URLSafeString(rsaSplitCodec(cipher, Cipher.ENCRYPT_MODE, data.getBytes(CHARSET)));
        } catch (Exception e) {
            throw new RunException("加密字符串[" + data + "]时遇到异常", e);
        }
    }

    /**
     * RSA算法私钥解密数据
     *
     * @param data 待解密的经过Base64编码的密文字符串
     * @param key  RSA私钥字符串
     * @return RSA私钥解密后的明文字符串
     */
    public static String buildRSADecryptByPrivateKey(String data, String key) {
        try {
            // 通过PKCS#8编码的Key指令获得私钥对象
            PKCS8EncodedKeySpec pkcs8KeySpec = new PKCS8EncodedKeySpec(Base64.decodeBase64(key));
            KeyFactory keyFactory = KeyFactory.getInstance(ALGORITHM_RSA);
            Key privateKey = keyFactory.generatePrivate(pkcs8KeySpec);
            // decrypt
            Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
            cipher.init(Cipher.DECRYPT_MODE, privateKey);
            return new String(rsaSplitCodec(cipher, Cipher.DECRYPT_MODE, Base64.decodeBase64(data)), CHARSET);
        } catch (Exception e) {
            throw new RunException("解密字符串[" + data + "]时遇到异常", e);
        }
    }

    /**
     * RSA算法使用私钥对数据生成数字签名
     *
     * @param data 待签名的明文字符串
     * @param key  RSA私钥字符串
     * @return RSA私钥签名后的经过Base64编码的字符串
     */
    public static String buildRSASignByPrivateKey(String data, String key) {
        try {
            // 通过PKCS#8编码的Key指令获得私钥对象
            PKCS8EncodedKeySpec pkcs8KeySpec = new PKCS8EncodedKeySpec(Base64.decodeBase64(key));
            KeyFactory keyFactory = KeyFactory.getInstance(ALGORITHM_RSA);
            PrivateKey privateKey = keyFactory.generatePrivate(pkcs8KeySpec);
            // sign
            Signature signature = Signature.getInstance(ALGORITHM_RSA_SIGN);
            signature.initSign(privateKey);
            signature.update(data.getBytes(CHARSET));
            return Base64.encodeBase64URLSafeString(signature.sign());
        } catch (Exception e) {
            throw new RunException("签名字符串[" + data + "]时遇到异常", e);
        }
    }

    /**
     * RSA算法使用公钥校验数字签名
     *
     * @param data 参与签名的明文字符串
     * @param key  RSA公钥字符串
     * @param sign RSA签名得到的经过Base64编码的字符串
     * @return true--验签通过,false--验签未通过
     */
    public static boolean buildRSAverifyByPublicKey(String data, String key, String sign) {
        try {
            // 通过X509编码的Key指令获得公钥对象
            X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(Base64.decodeBase64(key));
            KeyFactory keyFactory = KeyFactory.getInstance(ALGORITHM_RSA);
            PublicKey publicKey = keyFactory.generatePublic(x509KeySpec);
            // verify
            Signature signature = Signature.getInstance(ALGORITHM_RSA_SIGN);
            signature.initVerify(publicKey);
            signature.update(data.getBytes(CHARSET));
            return signature.verify(Base64.decodeBase64(sign));
        } catch (Exception e) {
            throw new RunException("验签字符串[" + data + "]时遇到异常", e);
        }
    }

    /**
     * RSA算法分段加解密数据
     *
     * @param cipher 初始化了加解密工作模式后的javax.crypto.Cipher对象
     * @param opmode 加解密模式,值为javax.crypto.Cipher.ENCRYPT_MODE/DECRYPT_MODE
     * @return 加密或解密后得到的数据的字节数组
     */
    private static byte[] rsaSplitCodec(Cipher cipher, int opmode, byte[] datas) {
        int maxBlock = 0;
        if (opmode == Cipher.DECRYPT_MODE) {
            maxBlock = ALGORITHM_RSA_PRIVATE_KEY_LENGTH / 8;
        } else {
            maxBlock = ALGORITHM_RSA_PRIVATE_KEY_LENGTH / 8 - 11;
        }
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        int offSet = 0;
        byte[] buff;
        int i = 0;
        try {
            while (datas.length > offSet) {
                if (datas.length - offSet > maxBlock) {
                    buff = cipher.doFinal(datas, offSet, maxBlock);
                } else {
                    buff = cipher.doFinal(datas, offSet, datas.length - offSet);
                }
                out.write(buff, 0, buff.length);
                i++;
                offSet = i * maxBlock;
            }
        } catch (Exception e) {
            throw new RunException("加解密阀值为[" + maxBlock + "]的数据时发生异常", e);
        }
        byte[] resultDatas = out.toByteArray();
        IOUtils.closeQuietly(out);
        return resultDatas;
    }

    public static void main(String[] args) {
        Map<String, String> channelRsaKey = RSAEncrypUtil.initRSAKey();
        Map<String, String> platformRsaKey = RSAEncrypUtil.initRSAKey();
        String channelPrivateKey = channelRsaKey.get("privateKey");
        String channelPublicKey = channelRsaKey.get("publicKey");
        String platformPrivateKey = platformRsaKey.get("privateKey");
        String platformPublicKey = platformRsaKey.get("publicKey");
        String data = "{\"test\":\"test\"}";

        String encryptData = RSAEncrypUtil.buildRSAEncryptByPublicKey(data, platformPublicKey);
        String sign = RSAEncrypUtil.buildRSASignByPrivateKey(encryptData, channelPrivateKey);

        boolean verifySign = RSAEncrypUtil.buildRSAverifyByPublicKey(encryptData, channelPublicKey, sign);
        if (!verifySign) {
            log.info("验签失败");
        }
        String decryptData = RSAEncrypUtil.buildRSADecryptByPrivateKey(encryptData, platformPrivateKey);
        log.info("decryptData:{}", decryptData);
        Assert.isTrue(decryptData.equals(data), "");
    }
}