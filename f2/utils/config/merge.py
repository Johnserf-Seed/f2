# path: f2/utils/config/merge.py

from typing import Any, Dict, Iterable, Optional

import click

from f2.exceptions.conf_exceptions import ConfError
from f2.i18n.translator import _

# 与 click.BOOL 接受的写法一致
_TRUE_WORDS = frozenset({"1", "true", "t", "yes", "y", "on"})
_FALSE_WORDS = frozenset({"0", "false", "f", "no", "n", "off"})


def merge_config(
    main_conf: dict,
    custom_conf: dict,
    **kwargs,
) -> dict:
    """
    合并配置参数，使 CLI 参数优先级高于自定义配置，自定义配置优先级高于主配置，最终生成完整配置参数字典。

    Args:
        main_conf (dict): 主配置参数字典
        custom_conf (dict): 自定义配置参数字典
        **kwargs: CLI 参数和其他额外的配置参数

    Returns:
        dict: 合并后的配置参数字典

    Raises:
        ValueError: 当主配置或自定义配置为空时抛出错误。
    """
    if not main_conf:
        raise ValueError(_("主配置参数不能为空，请检查配置文件是否正确加载"))

    if not custom_conf:
        raise ValueError(_("自定义配置参数不能为空或空字典，请提供有效的自定义配置"))

    # 合并主配置和自定义配置
    merged_conf = {}
    for key, value in main_conf.items():
        merged_conf[key] = value  # 将主配置复制到合并后的配置中

    for key, value in custom_conf.items():
        if value not in [None, ""]:  # 只有值不为 None 和 空字符串，才进行合并
            merged_conf[key] = value  # 自定义配置参数会覆盖主配置中的同名参数

    # 合并 CLI 参数与合并后的配置，确保 CLI 参数的优先级最高
    for key, value in kwargs.items():
        if value not in [None, ""]:  # 如果值不为 None 和 空字符串，则进行合并
            merged_conf[key] = value  # CLI 参数会覆盖自定义配置和主配置中的同名参数

    return merged_conf


def parse_bool(value: Any) -> Any:
    """
    把配置中表示开关的字符串转换为布尔值 (Convert switch-like strings in config files to booleans)

    ruamel.yaml 按 YAML 1.2 解析，yes/no/on/off 会被读成字符串，而非空字符串在 Python 中都为真，
    写成 no 的开关反而会被打开。无法识别的值原样返回（例如 verify 也可以是 CA 证书路径）。

    Args:
        value (Any): 配置值 (Config value)

    Returns:
        Any: 能识别时返回布尔值，否则原样返回 (A bool when recognized, otherwise the value unchanged)
    """
    if isinstance(value, str):
        word = value.strip().lower()
        if word in _TRUE_WORDS:
            return True
        if word in _FALSE_WORDS:
            return False
    return value


def coerce_bool_options(
    params: Iterable[click.Parameter], conf: Dict[str, Any]
) -> Dict[str, Any]:
    """
    把命令行布尔选项对应的配置值转换为布尔值 (Convert config values of boolean CLI options to booleans)

    命令行传入的值已由 click 转换，这里处理来自配置文件的字符串（如 yes/no）。

    Args:
        params (Iterable[click.Parameter]): 命令的参数定义 (Parameters of the command)
        conf (Dict[str, Any]): 合并后的配置 (Merged configuration)

    Returns:
        Dict[str, Any]: 转换后的配置 (The configuration with booleans converted)

    Raises:
        ConfError: 配置值无法识别为开关时 (When a value cannot be read as a switch)
    """
    for param in params:
        name = param.name
        if not name or not isinstance(param.type, click.types.BoolParamType):
            continue
        value = conf.get(name)
        if not isinstance(value, str):
            continue
        converted = parse_bool(value)
        if isinstance(converted, str):
            raise ConfError(
                _("配置项 {0} 只能是 true/false 或 yes/no").format(name),
                key=name,
                value=value,
            )
        conf[name] = converted
    return conf


# 数字类配置项允许的最小值；max_counts 为 0 表示不限制
NUMBER_OPTION_MINIMUMS: Dict[str, int] = {
    "timeout": 1,
    "max_retries": 1,
    "max_connections": 1,
    "max_tasks": 1,
    "page_counts": 1,
    "max_counts": 0,
}
# 可以是小数的数字配置项
FLOAT_OPTIONS = frozenset({"timeout"})


def check_number_options(
    conf: Dict[str, Any], names: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    """
    检查数字类配置项的取值 (Check the values of numeric settings)

    此前 max_tasks 为 0 时下载一直等待、程序卡住，为负数时报 Semaphore 的 ValueError；
    timeout 为 0 时每个请求都立即超时，max_retries 为 0 时请求根本不发出，却只提示检查网络。
    命令行的值已由 click 转为整数，这里同时处理配置文件中写成字符串的数字。

    Args:
        conf (Dict[str, Any]): 合并后的配置 (Merged configuration)
        names (Iterable[str]): 只检查这些配置项，默认检查全部 (Settings to check, all by default)

    Returns:
        Dict[str, Any]: 数字已转换的配置 (The configuration with numbers converted)

    Raises:
        ConfError: 值不是数字、应为整数却有小数或小于允许的最小值时
    """
    for name in NUMBER_OPTION_MINIMUMS if names is None else names:
        minimum = NUMBER_OPTION_MINIMUMS[name]
        value = conf.get(name)
        if value is None:
            continue
        try:
            if isinstance(value, bool):
                raise ValueError(value)
            number = (
                value if isinstance(value, (int, float)) else float(str(value).strip())
            )
            if name not in FLOAT_OPTIONS:
                if number != int(number):
                    raise ValueError(value)
                number = int(number)
        except (ValueError, OverflowError):
            raise ConfError(
                _("配置项 {0} 必须是数字，当前为 {1}").format(name, value),
                key=name,
                value=value,
            ) from None
        if number < minimum:
            raise ConfError(
                _("配置项 {0} 不能小于 {1}，当前为 {2}").format(name, minimum, value),
                key=name,
                value=value,
            )
        conf[name] = number
    return conf
