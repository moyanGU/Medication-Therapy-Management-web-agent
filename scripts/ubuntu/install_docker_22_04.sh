#!/usr/bin/env bash
# Ubuntu 22.04 LTS 官方源安装 Docker + Compose v2，并配置镜像加速器
# 使用方法：
#   sudo bash scripts/ubuntu/install_docker_22_04.sh
# 说明：
# - 仅使用 Docker 官方 apt 源
# - 安装 docker-compose-plugin（Compose v2）
# - 写入 /etc/docker/daemon.json 配置镜像加速与日志轮转
# - 重启并验证版本
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "请以 root 权限运行该脚本 (sudo)" >&2
  exit 1
fi

# 1) 清理旧版本（忽略不存在的包）
apt-get update
apt-get remove -y docker docker-engine docker.io containerd runc || true

# 2) 安装依赖与添加官方 GPG 与 apt 源
apt-get install -y ca-certificates curl gnupg lsb-release
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

. /etc/os-release
ARCH=$(dpkg --print-architecture)
CODENAME=${VERSION_CODENAME:-jammy}
echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update

# 3) 安装 Docker 引擎与 Compose v2 插件
apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# 4) Docker 守护进程配置（镜像加速、日志轮转、cgroupdriver）
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://qztpf1t5.mirror.aliyuncs.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF

# 5) 启用与重启
systemctl enable docker
systemctl restart docker

# 6) 将当前 sudo 用户加入 docker 组（若存在）
if [ -n "${SUDO_USER:-}" ] && id -nG "$SUDO_USER" | grep -qv "docker"; then
  usermod -aG docker "$SUDO_USER" || true
  echo "已将用户 $SUDO_USER 加入 docker 组（需要重新登录生效）"
fi

# 7) 打印版本验证
set +e
echo "Docker 版本:"
docker --version || true

echo "Docker Compose 版本:"
docker compose version || true
set -e

echo "安装完成。若首次拉取镜像缓慢，请确认 /etc/docker/daemon.json 已包含镜像加速器并重启 Docker。"