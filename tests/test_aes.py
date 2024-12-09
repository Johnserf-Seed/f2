import pytest
from f2.utils.utils import AESEncryptionUtils


# 测试用例参数
TEST_KEY_AES128 = b"6267274627536375"  # 16 字节
TEST_KEY_AES192 = b"626727462753637592910384"  # 24 字节
TEST_KEY_AES256 = b"62672746275363759291038426391283"  # 32 字节
TEST_IV_CBC = b"9865356457433664"  # 16 字节
TEST_IV_GCM = b"986535645743"  # 12 字节
TEST_TEXT = b"Hello, World!"  # 明文数据


@pytest.fixture
def aes128_gcm_encryption():
    return AESEncryptionUtils(
        key=TEST_KEY_AES128, algorithm="AES128", mode="GCM", iv=TEST_IV_GCM
    )


@pytest.fixture
def aes128_cbc_encryption():
    return AESEncryptionUtils(
        key=TEST_KEY_AES128, algorithm="AES128", mode="CBC", iv=TEST_IV_CBC
    )


@pytest.fixture
def aes128_ecb_encryption():
    return AESEncryptionUtils(key=TEST_KEY_AES128, algorithm="AES128", mode="ECB")


@pytest.fixture
def aes192_gcm_encryption():
    return AESEncryptionUtils(
        key=TEST_KEY_AES192, algorithm="AES192", mode="GCM", iv=TEST_IV_GCM
    )


@pytest.fixture
def aes192_cbc_encryption():
    return AESEncryptionUtils(
        key=TEST_KEY_AES192, algorithm="AES192", mode="CBC", iv=TEST_IV_CBC
    )


@pytest.fixture
def aes192_ecb_encryption():
    return AESEncryptionUtils(key=TEST_KEY_AES192, algorithm="AES192", mode="ECB")


@pytest.fixture
def aes256_gcm_encryption():
    return AESEncryptionUtils(
        key=TEST_KEY_AES256, algorithm="AES256", mode="GCM", iv=TEST_IV_GCM
    )


@pytest.fixture
def aes256_cbc_encryption():
    return AESEncryptionUtils(
        key=TEST_KEY_AES256, algorithm="AES256", mode="CBC", iv=TEST_IV_CBC
    )


@pytest.fixture
def aes256_ecb_encryption():
    return AESEncryptionUtils(key=TEST_KEY_AES256, algorithm="AES256", mode="ECB")


# 测试 AES128 GCM 加密和解密
def test_aes128_gcm_encrypt_decrypt(aes128_gcm_encryption):
    encrypted = aes128_gcm_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes128_gcm_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES128 GCM 解密失败，明文不匹配"


# 测试 AES128 CBC 加密和解密
def test_aes128_cbc_encrypt_decrypt(aes128_cbc_encryption):
    encrypted = aes128_cbc_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes128_cbc_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES128 CBC 解密失败，明文不匹配"


# 测试 AES128 ECB 加密和解密
def test_aes128_ecb_encrypt_decrypt(aes128_ecb_encryption):
    encrypted = aes128_ecb_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes128_ecb_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES128 ECB 解密失败，明文不匹配"


# 测试 AES192 GCM 加密和解密
def test_aes192_gcm_encrypt_decrypt(aes192_gcm_encryption):
    encrypted = aes192_gcm_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes192_gcm_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES192 GCM 解密失败，明文不匹配"


# 测试 AES192 CBC 加密和解密
def test_aes192_cbc_encrypt_decrypt(aes192_cbc_encryption):
    encrypted = aes192_cbc_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes192_cbc_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES192 CBC 解密失败，明文不匹配"


# 测试 AES192 ECB 加密和解密
def test_aes192_ecb_encrypt_decrypt(aes192_ecb_encryption):
    encrypted = aes192_ecb_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes192_ecb_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES192 ECB 解密失败，明文不匹配"


# 测试 AES256 GCM 加密和解密
def test_aes256_gcm_encrypt_decrypt(aes256_gcm_encryption):
    encrypted = aes256_gcm_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes256_gcm_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES256 GCM 解密失败，明文不匹配"


# 测试 AES256 CBC 加密和解密
def test_aes256_cbc_encrypt_decrypt(aes256_cbc_encryption):
    encrypted = aes256_cbc_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes256_cbc_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES256 CBC 解密失败，明文不匹配"


# 测试 AES256 ECB 加密和解密
def test_aes256_ecb_encrypt_decrypt(aes256_ecb_encryption):
    encrypted = aes256_ecb_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes256_ecb_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "AES256 ECB 解密失败，明文不匹配"


# 测试不正确的密钥长度
def test_invalid_key_length():
    with pytest.raises(
        ValueError, match="AES128 算法密钥长度不正确：8 字节，期望长度为 16 字节。"
    ):
        AESEncryptionUtils(key=b"shortkey", algorithm="AES128", mode="GCM")


# 测试不支持的加密模式
def test_invalid_mode():
    with pytest.raises(ValueError, match="模式必须为 'GCM', 'CBC' 或 'ECB'。"):
        AESEncryptionUtils(key=TEST_KEY_AES128, algorithm="AES128", mode="INVALID_MODE")


# 测试 GCM 解密时，认证标签无效
def test_gcm_invalid_tag(aes128_gcm_encryption):
    # 创建一个伪造的密文，其中认证标签无效
    fake_encrypted = aes128_gcm_encryption.aes_encrypt(TEST_TEXT)
    fake_encrypted = fake_encrypted[:12] + b"invalidtag" + fake_encrypted[28:]

    with pytest.raises(ValueError, match="GCM 模式解密失败：认证标签无效"):
        aes128_gcm_encryption.aes_decrypt(fake_encrypted)


# 测试 CBC 模式时 IV 的影响
def test_cbc_iv(aes192_cbc_encryption):
    encrypted1 = aes192_cbc_encryption.aes_encrypt(TEST_TEXT)
    aes192_cbc_encryption.iv = b"1111111111111111"  # 修改 IV
    encrypted2 = aes192_cbc_encryption.aes_encrypt(TEST_TEXT)

    # 检查不同 IV 产生不同的密文
    assert (
        encrypted1 != encrypted2
    ), "CBC 模式加密相同的明文，但使用不同的 IV 应该产生不同的密文"


# 测试 ECB 模式加密
def test_ecb_no_iv(aes256_ecb_encryption):
    # ECB 模式不需要 IV
    encrypted = aes256_ecb_encryption.aes_encrypt(TEST_TEXT)
    decrypted = aes256_ecb_encryption.aes_decrypt(encrypted)

    assert decrypted == TEST_TEXT, "ECB 模式解密失败，明文不匹配"
