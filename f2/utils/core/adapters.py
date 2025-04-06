# path: f2/utils/core/adapters.py

import typing

import click


def adapt_validation_call(validation_func, ctx, value):
    """
    处理 Click 验证函数的类型适配

    将None参数转换为Click.Parameter类型，使验证函数可以在非回调环境中调用

    Args:
        validation_func (Callable): Click验证回调函数
        ctx (click.Context): Click上下文对象
        value (Any): 需要验证的值

    Returns:
        Any: 与原始验证函数相同的返回值
    """
    return validation_func(ctx, typing.cast(click.Parameter, None), value)
