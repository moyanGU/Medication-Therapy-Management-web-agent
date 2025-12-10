# 后端Dockerfile
# 基础镜像改为官方完整版，保证系统依赖更完整，提升兼容性与拉取成功率
# 说明：此前使用 python:3.11-slim 为减少体积，但在当前网络环境下拉取速度与稳定性存在问题；
#       切换为 python:3.12.6（Debian 完整版），与项目依赖（Django 4.2 LTS 等）兼容，同时提高拉取成功率。
FROM docker.m.daocloud.io/library/python:3.12.6

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
# 进一步减少构建时间与镜像体积：禁用 pip 缓存与版本检查
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# 为国内网络环境准备的默认 PyPI 镜像（可在构建时通过 --build-arg 覆盖）
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_DEFAULT_TIMEOUT=120

# 精简系统依赖：项目使用 PyMySQL，无需 mysqlclient 的 C 扩展，去掉编译工具链以加快构建
# 如后续改为使用 mysqlclient 或需编译其他依赖，再恢复 apt 安装
RUN true

# 设置工作目录
WORKDIR /app

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
# 先升级 pip/工具链，随后使用稳定镜像安装；若镜像不可达，回退到官方 PyPI
RUN python -m pip install --upgrade pip setuptools wheel \
    && echo "Using index: ${PIP_INDEX_URL}" \
    && (pip install --no-cache-dir -r requirements.txt -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} --default-timeout=${PIP_DEFAULT_TIMEOUT} \
        || pip install --no-cache-dir -r requirements.txt --default-timeout=${PIP_DEFAULT_TIMEOUT})

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p logs media staticfiles

# 设置权限
RUN chmod +x manage.py

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]