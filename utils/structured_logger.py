"""结构化日志系统"""
import json
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class StructuredLogger:
    """结构化日志记录器（JSON格式，便于生产环境监控）"""

    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        enable_console: bool = True,
        enable_file: bool = True
    ):
        """
        初始化结构化日志记录器

        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录
            log_file: 日志文件名（None则使用默认名称）
            level: 日志级别
            enable_console: 是否启用控制台输出
            enable_file: 是否启用文件输出
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # 避免重复输出

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 添加控制台处理器
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(ColoredFormatter())
            self.logger.addHandler(console_handler)

        # 添加文件处理器
        if enable_file:
            log_dir_path = Path(log_dir)
            log_dir_path.mkdir(parents=True, exist_ok=True)

            if log_file is None:
                log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.jsonl"

            file_path = log_dir_path / log_file

            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)

    def _build_log_entry(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        构建日志条目

        Args:
            level: 日志级别
            message: 日志消息
            context: 上下文信息
            error: 异常对象

        Returns:
            日志条目字典
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }

        if context:
            entry["context"] = context

        if error:
            entry["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": self._format_traceback(error)
            }

        return entry

    def _format_traceback(self, error: Exception) -> Optional[str]:
        """格式化异常堆栈"""
        import traceback
        if hasattr(error, "__traceback__"):
            return "".join(traceback.format_tb(error.__traceback__))
        return None

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """记录 DEBUG 级别日志"""
        entry = self._build_log_entry("DEBUG", message, context)
        self.logger.debug(json.dumps(entry, ensure_ascii=False))

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """记录 INFO 级别日志"""
        entry = self._build_log_entry("INFO", message, context)
        self.logger.info(json.dumps(entry, ensure_ascii=False))

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """记录 WARNING 级别日志"""
        entry = self._build_log_entry("WARNING", message, context)
        self.logger.warning(json.dumps(entry, ensure_ascii=False))

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """记录 ERROR 级别日志"""
        entry = self._build_log_entry("ERROR", message, context, error)
        self.logger.error(json.dumps(entry, ensure_ascii=False))

    def log_workflow_start(
        self,
        workflow_id: str,
        user_id: str,
        persona_name: str,
        **kwargs
    ):
        """记录工作流开始"""
        self.info("Workflow started", {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "persona_name": persona_name,
            **kwargs
        })

    def log_workflow_end(
        self,
        workflow_id: str,
        user_id: str,
        success: bool,
        duration: float,
        **kwargs
    ):
        """记录工作流结束"""
        level = "info" if success else "error"
        getattr(self, level)("Workflow completed", {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "success": success,
            "duration_seconds": duration,
            **kwargs
        })

    def log_api_call(
        self,
        api_name: str,
        method: str,
        status: str,
        duration: float,
        **kwargs
    ):
        """记录 API 调用"""
        self.info("API call", {
            "api_name": api_name,
            "method": method,
            "status": status,
            "duration_seconds": duration,
            **kwargs
        })

    def log_generation(
        self,
        user_id: str,
        persona_name: str,
        date: str,
        success: bool,
        tweet_length: Optional[int] = None,
        **kwargs
    ):
        """记录内容生成"""
        level = "info" if success else "error"
        context = {
            "user_id": user_id,
            "persona_name": persona_name,
            "date": date,
            "success": success,
            **kwargs
        }
        if tweet_length is not None:
            context["tweet_length"] = tweet_length

        getattr(self, level)("Content generated", context)


class JSONFormatter(logging.Formatter):
    """JSON 格式化器（文件输出）"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为 JSON"""
        # 日志消息已经是 JSON 字符串，直接返回
        return record.getMessage()


class ColoredFormatter(logging.Formatter):
    """彩色格式化器（控制台输出）"""

    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为彩色文本"""
        try:
            # 解析 JSON 日志消息
            log_data = json.loads(record.getMessage())

            level = log_data.get("level", "INFO")
            color = self.COLORS.get(level, self.COLORS['RESET'])
            reset = self.COLORS['RESET']

            # 格式化为可读文本
            timestamp = log_data.get("timestamp", "")
            message = log_data.get("message", "")
            context = log_data.get("context", {})
            error = log_data.get("error")

            # 基本格式
            formatted = f"{color}[{level}]{reset} {timestamp} - {message}"

            # 添加上下文信息
            if context:
                context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
                formatted += f" | {context_str}"

            # 添加错误信息
            if error:
                formatted += f"\n  Error: {error.get('type')} - {error.get('message')}"

            return formatted
        except json.JSONDecodeError:
            # 如果不是 JSON，直接返回
            return record.getMessage()


# 全局日志实例（便于快速使用）
_global_logger: Optional[StructuredLogger] = None


def get_logger(
    name: str = "comfyui-twitterchat",
    log_dir: str = "logs",
    **kwargs
) -> StructuredLogger:
    """
    获取全局日志实例（单例模式）

    Args:
        name: 日志记录器名称
        log_dir: 日志目录
        **kwargs: 其他参数

    Returns:
        StructuredLogger 实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name, log_dir, **kwargs)
    return _global_logger
