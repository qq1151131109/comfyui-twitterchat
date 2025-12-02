"""重试装饰器工具"""
import time
import functools
from typing import Callable, Tuple, Type, Optional


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    重试装饰器（支持指数退避）

    使用方式:
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        def api_call():
            # 可能失败的操作
            pass

    Args:
        max_attempts: 最大尝试次数（包括首次尝试）
        delay: 初始延迟时间（秒）
        backoff: 退避因子（每次失败后延迟时间乘以此因子）
        exceptions: 需要重试的异常类型元组
        on_retry: 重试前的回调函数，接收 (attempt, exception, delay) 参数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # 如果是最后一次尝试，直接抛出异常
                    if attempt == max_attempts:
                        print(f"[Retry] {func.__name__} 失败（已重试 {max_attempts-1} 次）: {str(e)}")
                        raise

                    # 执行重试回调
                    if on_retry:
                        on_retry(attempt, e, current_delay)
                    else:
                        print(f"[Retry] {func.__name__} 第 {attempt}/{max_attempts} 次尝试失败: {str(e)}")
                        print(f"[Retry] 等待 {current_delay:.2f} 秒后重试...")

                    # 等待
                    time.sleep(current_delay)

                    # 指数退避
                    current_delay *= backoff

            # 理论上不会到达这里，但为了类型安全
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def retry_with_exponential_backoff(
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    max_attempts: int = 5
):
    """
    指数退避重试装饰器（带抖动）

    使用方式:
        @retry_with_exponential_backoff(max_attempts=5, initial_delay=1.0)
        def llm_api_call():
            # LLM API 调用
            pass

    Args:
        initial_delay: 初始延迟（秒）
        max_delay: 最大延迟（秒）
        exponential_base: 指数基数
        jitter: 是否添加随机抖动（避免同时重试）
        max_attempts: 最大尝试次数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import random

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        print(f"[RetryBackoff] {func.__name__} 最终失败: {str(e)}")
                        raise

                    # 计算延迟时间（指数退避）
                    delay = min(initial_delay * (exponential_base ** (attempt - 1)), max_delay)

                    # 添加随机抖动（0-50%）
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    print(f"[RetryBackoff] {func.__name__} 尝试 {attempt}/{max_attempts} 失败: {str(e)}")
                    print(f"[RetryBackoff] 等待 {delay:.2f} 秒后重试...")

                    time.sleep(delay)

        return wrapper
    return decorator


class RetryContext:
    """重试上下文管理器（用于非装饰器场景）"""

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        初始化重试上下文

        Args:
            max_attempts: 最大尝试次数
            delay: 初始延迟时间（秒）
            backoff: 退避因子
            exceptions: 需要重试的异常类型
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.attempt = 0

    def execute(self, func: Callable, *args, **kwargs):
        """
        执行函数并处理重试逻辑

        使用方式:
            retry_ctx = RetryContext(max_attempts=3)
            result = retry_ctx.execute(api_call, arg1, arg2, kwarg1=value1)

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值
        """
        current_delay = self.delay
        last_exception = None

        for self.attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e

                if self.attempt == self.max_attempts:
                    print(f"[RetryContext] 执行失败（已重试 {self.max_attempts-1} 次）: {str(e)}")
                    raise

                print(f"[RetryContext] 第 {self.attempt}/{self.max_attempts} 次尝试失败: {str(e)}")
                print(f"[RetryContext] 等待 {current_delay:.2f} 秒后重试...")

                time.sleep(current_delay)
                current_delay *= self.backoff

        if last_exception:
            raise last_exception
