# Prometheus Nacos Service Discovery

这是一个用于 Nacos 服务发现的 Prometheus 集成工具。该工具可以自动发现注册在 Nacos 中的服务，并生成 Prometheus 可用的目标配置文件。

## 功能特点

- 自动服务发现：自动发现注册在 Nacos 中的所有服务
- Prometheus 集成：生成 Prometheus 可用的目标配置文件
- 安全认证：支持 Nacos 的用户名密码认证
- 灵活配置：支持通过环境变量配置所有参数
- 完整日志：提供详细的运行日志，便于问题排查
- Docker 支持：提供 Docker 部署支持，包含健康检查和安全性配置

## 系统要求

- Python 3.8+
- Docker（可选，用于容器化部署）
- Nacos 服务器（1.x 或 2.x）

## 安装

1. 克隆项目：
```bash
git clone https://github.com/your-username/prometheus-nacos.git
cd prometheus-nacos
```

2. 安装依赖：
```bash
pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

## 配置

### 环境变量配置

| 环境变量 | 描述 | 默认值 |
|----------|------|---------|
| NACOS_SERVER | Nacos 服务器地址 | http://127.0.0.1:8848 |
| NACOS_NAMESPACE | Nacos 命名空间 | public |
| NACOS_USERNAME | Nacos 用户名 | nacos |
| NACOS_PASSWORD | Nacos 密码 | nacos |
| GROUP_NAME | 服务组名 | DEFAULT_GROUP |

## 使用方法

### 直接运行

```bash
python main.py
```

### Docker 部署

1. 构建镜像：
```bash
docker build -t prometheus-nacos .
```

2. 运行容器：
```bash
docker run -d \
  --name prometheus-nacos \
  -e NACOS_SERVER=http://nacos-server:8848 \
  -e NACOS_NAMESPACE=public \
  -e NACOS_USERNAME=nacos \
  -e NACOS_PASSWORD=nacos \
  -v /path/to/prometheus:/prometheus \
  --health-start-period=5s \
  --health-interval=30s \
  --health-timeout=30s \
  --health-retries=3 \
  prometheus-nacos
```

### 与 Prometheus 集成

1. 在 Prometheus 配置文件中添加以下配置：

```yaml
scrape_configs:
  - job_name: 'nacos-discovery'
    # 如果需要进行基本认证
    #basic_auth:
    #  username: admin
    #  password: admin
    file_sd_configs:
      - files:
        - '/prometheus/conf/services.json'
    refresh_interval: 10s
    metrics_path: '/actuator/prometheus'
```

## 输出文件

工具会生成两个配置文件：

1. `/app/services.json`: 主配置文件
2. `/prometheus/conf/services.json`: Prometheus 使用的配置文件

配置文件格式示例：
```json
[
  {
    "targets": ["192.168.1.100:8080"],
    "labels": {
      "job": "nacos-discovery",
      "instance": "192.168.1.100:8080",
      "service": "service-name"
    }
  }
]
```

## 日志

日志默认输出到标准输出，包含以下级别：
- INFO：正常运行信息
- ERROR：错误信息
- WARNING：警告信息

## 故障排除

1. 连接 Nacos 失败
   - 检查 NACOS_SERVER 地址是否正确
   - 确认 Nacos 服务是否正常运行
   - 验证用户名密码是否正确

2. 配置文件未生成
   - 检查目录权限
   - 确认挂载卷配置是否正确
   - 查看日志中是否有错误信息

3. 服务发现不工作
   - 确认服务是否正确注册到 Nacos
   - 检查 GROUP_NAME 和 NAMESPACE 配置
   - 验证 Prometheus 配置是否正确

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 作者

- Wengliang Zeng