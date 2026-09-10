# path: f2/utils/string/generator.py

import random

# 使用独立的系统随机源，导入本模块不会改动全局 random 模块的状态
# (Use a dedicated system RNG so importing this module never reseeds the global random module)
_rng = random.SystemRandom()


def gen_random_str(randomlength: int) -> str:
    """
    根据传入长度产生随机字符串 (Generate a random string based on the given length)

    Args:
        randomlength (int): 需要生成的随机字符串的长度 (The length of the random string to be generated)

    Returns:
        str: 生成的随机字符串 (The generated random string)
    """

    base_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
    return "".join(_rng.choice(base_str) for _ in range(randomlength))
