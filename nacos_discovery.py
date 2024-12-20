#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nacos Service Discovery Module

This module provides functionality to discover services registered in Nacos
and generate Prometheus target configuration files. It includes features for
authentication, service discovery, and configuration file management.

Author: Wengliang Zeng
Date: 2024-12-20
"""

import os
import json
import shutil
import logging
from typing import List, Dict, Any
import requests
from requests.exceptions import RequestException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NacosConfig:
    """Nacos 配置类，存储所有 Nacos 相关的配置参数"""
    
    def __init__(self):
        self.server = os.getenv("NACOS_SERVER", "http://127.0.0.1:8848")
        self.namespace = os.getenv("NACOS_NAMESPACE", "dev")
        self.username = os.getenv("NACOS_USERNAME", "nacos")
        self.password = os.getenv("NACOS_PASSWORD", "nacos")
        self.group_name = os.getenv("GROUP_NAME", "DEFAULT_GROUP")
        self.token = ""

class NacosClient:
    """Nacos 客户端类，处理与 Nacos 服务器的所有交互"""

    def __init__(self, config: NacosConfig):
        """
        初始化 Nacos 客户端
        
        Args:
            config: NacosConfig 实例，包含所有必要的配置参数
        """
        self.config = config
        self.session = requests.Session()

    def authenticate(self) -> None:
        """
        获取 Nacos 的访问令牌
        
        Raises:
            RequestException: 当认证请求失败时抛出
        """
        auth_url = f"{self.config.server}/nacos/v1/auth/login"
        auth_data = {
            "username": self.config.username,
            "password": self.config.password
        }
        
        try:
            response = self.session.post(auth_url, data=auth_data)
            response.raise_for_status()
            self.config.token = response.json().get("accessToken")
            if not self.config.token:
                raise ValueError("Failed to retrieve access token")
            logger.info("Successfully authenticated with Nacos server")
        except RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

    def get_services(self) -> List[str]:
        """
        获取所有注册的服务列表
        
        Returns:
            List[str]: 服务名称列表
        """
        try:
            response = self.session.get(
                f"{self.config.server}/nacos/v1/ns/service/list",
                params={
                    "namespaceId": self.config.namespace,
                    "groupName": self.config.group_name,
                    "pageNo": 1,
                    "pageSize": 100,
                    "accessToken": self.config.token
                }
            )
            response.raise_for_status()
            services = response.json().get('doms', [])
            logger.info(f"Retrieved {len(services)} services")
            return services
        except RequestException as e:
            logger.error(f"Failed to fetch services: {str(e)}")
            return []

    def get_service_instances(self, service_name: str) -> List[Dict[str, Any]]:
        """
        获取特定服务的所有实例
        
        Args:
            service_name: 服务名称
            
        Returns:
            List[Dict]: 服务实例列表
        """
        try:
            response = self.session.get(
                f"{self.config.server}/nacos/v1/ns/instance/list",
                params={
                    "namespaceId": self.config.namespace,
                    "serviceName": service_name,
                    "groupName": self.config.group_name,
                    "clusters": "",
                    "healthyOnly": False,
                    "accessToken": self.config.token
                }
            )
            response.raise_for_status()
            instances = response.json().get('hosts', [])
            logger.info(f"Retrieved {len(instances)} instances for service {service_name}")
            return instances
        except RequestException as e:
            logger.error(f"Failed to fetch instances for {service_name}: {str(e)}")
            return []

class PrometheusConfigGenerator:
    """Prometheus 配置生成器，负责生成和管理 Prometheus 目标配置"""

    @staticmethod
    def generate_target_config(instances: List[Dict[str, Any]], service_name: str) -> List[Dict[str, Any]]:
        """
        为服务实例生成 Prometheus 目标配置
        
        Args:
            instances: 服务实例列表
            service_name: 服务名称
            
        Returns:
            List[Dict]: Prometheus 目标配置列表
        """
        targets = []
        for instance in instances:
            # 添加原始端口配置
            targets.append({
                "targets": [f"{instance['ip']}:{instance['port']}"],
                "labels": {
                    "instance": f"{instance['ip']}:{instance['port']}",
                    "job": "nacos-discovery",
                    "service": service_name
                }
            })
        return targets

    @staticmethod
    def save_config(targets: List[Dict[str, Any]], output_path: str, config_dir: str) -> None:
        """
        保存并复制 Prometheus 配置文件
        
        Args:
            targets: 目标配置列表
            output_path: 输出文件路径
            config_dir: Prometheus 配置目录
        """
        try:
            # 确保配置目录存在
            os.makedirs(config_dir, exist_ok=True)
            
            # 写入配置文件
            with open(output_path, 'w') as f:
                json.dump(targets, f, indent=2)
            logger.info(f"Configuration written to {output_path}")

            # 复制到 Prometheus 配置目录
            dest_path = os.path.join(config_dir, os.path.basename(output_path))
            shutil.copy(output_path, dest_path)
            logger.info(f"Configuration copied to {dest_path}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to save or copy configuration: {str(e)}")
            raise

def main():
    """主函数，协调整个服务发现和配置生成过程"""
    try:
        # 初始化配置和客户端
        config = NacosConfig()
        client = NacosClient(config)
        
        # 认证
        client.authenticate()
        
        # 获取服务列表
        services = client.get_services()
        
        # 收集所有目标
        all_targets = []
        for service_name in services:
            instances = client.get_service_instances(service_name)
            targets = PrometheusConfigGenerator.generate_target_config(instances, service_name)
            all_targets.extend(targets)
        
        # 保存配置
        output_path = './app/services.json'
        config_dir = './prometheus/conf'
        PrometheusConfigGenerator.save_config(all_targets, output_path, config_dir)
        
        logger.info("Service discovery and configuration generation completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
