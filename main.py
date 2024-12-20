#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nacos Service Discovery Scheduler

This script schedules and runs the Nacos service discovery process periodically.
It uses the schedule library to run the discovery process every 10 seconds,
ensuring that the Prometheus configuration stays up to date with the services
registered in Nacos.

Author: Wengliang Zeng
Date: 2024-12-20
"""

import logging
import schedule
import signal
import sys
import time
from typing import NoReturn

import nacos_discovery

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum: int, frame) -> None:
    """
    处理进程信号，确保程序优雅退出
    
    Args:
        signum: 信号编号
        frame: 当前栈帧
    """
    logger.info(f"接收到信号 {signum}，准备退出程序...")
    sys.exit(0)

def discovery_job() -> None:
    """
    执行服务发现任务的包装函数
    
    捕获并记录任务执行过程中的任何异常，确保调度器继续运行
    """
    try:
        logger.info("开始执行服务发现任务")
        nacos_discovery.main()
        logger.info("服务发现任务执行完成")
    except Exception as e:
        logger.error(f"服务发现任务执行失败: {str(e)}", exc_info=True)

def run_scheduler() -> NoReturn:
    """
    运行调度器，定期执行服务发现任务
    
    每10秒执行一次服务发现任务，并处理键盘中断信号
    """
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 设置调度任务
    schedule.every(10).seconds.do(discovery_job)
    logger.info("服务发现调度器已启动，每10秒执行一次")
    
    try:
        # 立即执行一次任务
        discovery_job()
        
        # 持续运行调度器
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号，程序退出")
        sys.exit(0)

if __name__ == "__main__":
    run_scheduler()
