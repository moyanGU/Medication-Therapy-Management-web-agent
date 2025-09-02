# MTM-用药助手 药品管理系统

## 项目简介

MTM-用药助手是一款专为老年人设计的智能药品管理系统，旨在帮助用户安全、便捷地管理个人药品，提供用药提醒、有效期监控、用药记录等功能。

系统通过简洁易用的界面设计和智能化的提醒机制，解决老年人在药品管理中遇到的忘记服药、药品过期、用药冲突等问题，提升用药安全性和依从性。

## 核心功能

- **用户认证系统**：安全的注册登录，支持手机验证码
- **药品管理**：药品信息录入、图片上传、存储条件管理
- **用药记录**：服药历史记录、统计分析、依从性评价
- **用药提醒**：智能提醒设置、定时推送、闹钟集成
- **用药计划**：长短期用药计划、冲突检测、方案管理
- **就医记录**：就诊信息记录、诊断治疗方案管理
- **AI智能搜索**：基于大模型的药品智能搜索
- **管理后台**：用户管理、系统配置、数据统计

## 技术架构

### 前端技术栈
- **Vue 3.4+** - 渐进式JavaScript框架
- **TypeScript 5.0+** - 类型安全的JavaScript超集
- **Vite 5.0+** - 快速的前端构建工具
- **Vue Router 4.0+** - Vue.js官方路由管理器
- **Pinia 2.0+** - Vue.js状态管理库
- **TailwindCSS** - 实用优先的CSS框架

### 后端技术栈
- **Django 4.2+** - Python Web框架
- **Django REST Framework 3.14+** - 强大的API框架
- **MySQL 8.0+** - 关系型数据库
- **Redis 7.0+** - 内存数据库，用于缓存和会话
- **JWT** - JSON Web Token认证

### 部署技术栈
- **Docker** - 容器化部署
- **Docker Compose** - 多容器应用编排
- **Nginx** - 反向代理和静态文件服务

## 项目结构

```
mtm-helper/
├── src/                    # 前端源码
│   ├── components/         # Vue组件
│   ├── pages/             # 页面组件
│   ├── router/            # 路由配置
│   ├── composables/       # 组合式函数
│   └── lib/               # 工具库
├── backend/               # 后端源码
│   ├── mtm_helper/        # Django项目配置
│   ├── apps/              # Django应用
│   │   ├── authentication/# 认证应用
│   │   ├── users/         # 用户管理
│   │   ├── medicines/     # 药品管理
│   │   ├── records/       # 用药记录
│   │   ├── reminders/     # 用药提醒
│   │   ├── plans/         # 用药计划
│   │   ├── medical_records/# 就医记录
│   │   └── core/          # 核心功能
│   └── requirements.txt   # Python依赖
├── docker-compose.yml     # Docker编排配置
├── Dockerfile.frontend    # 前端Docker配置
└── README.md             # 项目说明
```

## 快速开始

### 环境要求

- Node.js 22.0+
- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (可选)

### 本地开发

#### 1. 克隆项目
```bash
git clone <repository-url>
cd mtm-helper
```

#### 2. 前端开发
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 3. 后端开发
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库和Redis连接

# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### Docker部署

#### 开发环境
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 生产环境
```bash
# 启动生产环境（包含Nginx）
docker-compose --profile production up -d
```

## 开发指南

### 代码规范

- 前端使用ESLint + Prettier进行代码格式化
- 后端使用Black + Flake8 + isort进行代码规范检查
- 提交前请运行代码检查：`npm run lint` 和 `black . && flake8`

### API文档

- 后端API文档：http://localhost:8000/api/docs/
- 管理后台：http://localhost:8000/admin/

### 测试

```bash
# 前端测试
npm run test

# 后端测试
cd backend
python manage.py test
```

## 部署说明

### 环境变量配置

复制 `backend/.env.example` 到 `backend/.env` 并配置以下变量：

- `SECRET_KEY`: Django密钥
- `DB_*`: 数据库连接配置
- `REDIS_*`: Redis连接配置
- `*_API_KEY`: 第三方服务API密钥

### 数据库初始化

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE mtm_helper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 运行迁移
python manage.py migrate

# 加载初始数据
python manage.py loaddata initial_data.json
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目维护者：MTM-用药助手 Team
- 邮箱：support@mtm-helper.com
- 项目地址：https://github.com/mtm-helper/mtm-helper

## 更新日志

### v1.0.0 (2025-01-XX)
- 初始版本发布
- 完成核心功能开发
- 支持Docker部署
