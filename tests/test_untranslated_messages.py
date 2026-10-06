# path: tests/test_untranslated_messages.py

import ast
import re
from pathlib import Path

import f2

CJK = re.compile(r"[一-鿿]")
SOURCE = Path(f2.__file__).parent


def literal_text(node):
    """
    没有经过 _() 的文字：字符串常量、f-string、对常量调用 .format() 与字符串拼接；
    其他表达式（如 _() 的结果）返回 None
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            v.value
            for v in node.values
            if isinstance(v, ast.Constant) and isinstance(v.value, str)
        )
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "format"
    ):
        return literal_text(node.func.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return (literal_text(node.left) or "") + (literal_text(node.right) or "")
    return None


def untranslated_messages():
    found = []
    for path in sorted(SOURCE.rglob("*.py")):
        if path.name.endswith("_pb2.py") or "test" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            message = None
            # logger 的用户可见级别（debug 与 trace_logger 只写日志文件，不要求翻译）
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("info", "warning", "error", "critical")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "logger"
                and node.args
            ):
                message = literal_text(node.args[0])
            # 抛出的异常会显示给用户
            elif (
                isinstance(node, ast.Raise)
                and isinstance(node.exc, ast.Call)
                and node.exc.args
            ):
                message = literal_text(node.exc.args[0])
            if message and CJK.search(message):
                found.append(f"{path.relative_to(SOURCE.parent)}:{node.lineno}")
    return found


def test_user_visible_messages_are_translatable():
    # 直接写中文、没有经过 _() 的提示在英文界面下仍是中文
    assert untranslated_messages() == []
