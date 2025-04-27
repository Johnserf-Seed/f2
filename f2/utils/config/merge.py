# path: f2/utils/config/merge.py


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
        raise ValueError("主配置参数不能为空，请检查配置文件是否正确加载")

    if not custom_conf:
        raise ValueError("自定义配置参数不能为空或空字典，请提供有效的自定义配置")

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
