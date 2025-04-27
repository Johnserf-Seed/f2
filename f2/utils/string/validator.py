# path: f2/utils/string/validator.py


def check_invalid_naming(
    naming: str, allowed_patterns: list, allowed_separators: list
) -> list:
    """
    检查命名是否符合命名模板 (Check if the naming conforms to the naming template)

    Args:
        naming (str): 命名字符串 (Naming string)
        allowed_patterns (list): 允许的模式列表 (List of allowed patterns)
        allowed_separators (list): 允许的分隔符列表 (List of allowed separators)
    Returns:
        list: 无效的模式列表 (List of invalid patterns)
    """
    if not naming or not allowed_patterns or not allowed_separators:
        return []

    temp_naming = naming
    invalid_patterns = []

    # 检查提供的模式是否有效
    for pattern in allowed_patterns:
        if pattern in temp_naming:
            temp_naming = temp_naming.replace(pattern, "")

    # 此时，temp_naming应只包含分隔符
    for char in temp_naming:
        if char not in allowed_separators:
            invalid_patterns.append(char)

    # 检查连续的无效模式或分隔符
    for pattern in allowed_patterns:
        # 检查像"{xxx}{xxx}"这样的模式
        if pattern + pattern in naming:
            invalid_patterns.append(pattern + pattern)
        for sep in allowed_patterns:
            # 检查像"{xxx}-{xxx}"这样的模式
            if pattern + sep + pattern in naming:
                invalid_patterns.append(pattern + sep + pattern)

    return invalid_patterns
