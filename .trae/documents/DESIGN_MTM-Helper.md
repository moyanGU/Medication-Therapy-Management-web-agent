# MTM-Helper 系统架构设计文档

## 1. 整体架构图

### 1.1 系统总体架构

```mermaid
graph TB
    subgraph "用户层"
        U1[老年用户]
        U2[管理员用户]
    end
    
    subgraph "前端层 - Vue3 SPA"
        FE[Vue3 + TypeScript + Vite]
        R[Vue Router 4]
        S[Pinia 状态管理]
        UI[UI组件库]
    end
    
    subgraph "网络层"
        HTTP[HTTP/HTTPS]
        WS[WebSocket]
    end
    
    subgraph "后端层 - Django"
        API[Django REST Framework]
        AUTH[认证中间件]
        CORS[CORS中间件]
        CACHE[缓存中间件]
    end
    
    subgraph "业务逻辑层"
        USER_SVC[用户服务]
        MED_SVC[药品服务]
        REC_SVC[记录服务]
        REM_SVC[提醒服务]
        PLAN_SVC[计划服务]
        AI_SVC[AI搜索服务]
    end
    
    subgraph "数据层"
        MYSQL[(MySQL 8.0+)]
        REDIS[(Redis 7.0+)]
    end
    
    subgraph "外部服务"
        AI_API[AI大模型API]
        SMS[短信服务]
    end
    
    U1 --> FE
    U2 --> FE
    FE --> HTTP
    FE --> WS
    HTTP --> API
    WS --> API
    API --> AUTH
    API --> CORS
    API --> CACHE
    API --> USER_SVC
    API --> MED_SVC
    API --> REC_SVC
    API --> REM_SVC
    API --> PLAN_SVC
    API --> AI_SVC
    
    USER_SVC --> MYSQL
    MED_SVC --> MYSQL
    REC_SVC --> MYSQL
    REM_SVC --> MYSQL
    PLAN_SVC --> MYSQL
    
    AUTH --> REDIS
    CACHE --> REDIS
    REM_SVC --> REDIS
    
    AI_SVC --> AI_API
    USER_SVC --> SMS
```

### 1.2 技术栈架构

```mermaid
graph LR
    subgraph "前端技术栈"
        V[Vue 3.4+]
        T[TypeScript 5.0+]
        VT[Vite 5.0+]
        VR[Vue Router 4.0+]
        P[Pinia 2.0+]
        TC[TailwindCSS]
    end
    
    subgraph "后端技术栈"
        D[Django 4.2+]
        DRF[Django REST Framework 3.14+]
        DC[Django CORS Headers]
        DR[Django Redis]
    end
    
    subgraph "数据库技术栈"
        M[MySQL 8.0+]
        R[Redis 7.0+]
    end
    
    subgraph "部署技术栈"
        DOC[Docker]
        COMP[Docker Compose]
        NG[Nginx]
    end
```

## 2. 分层设计和核心组件

### 2.1 前端分层架构

```mermaid
graph TD
    subgraph "表现层 (Presentation Layer)"
        VIEWS[页面组件]
        COMPS[通用组件]
        LAYOUTS[布局组件]
    end
    
    subgraph "状态管理层 (State Management Layer)"
        STORES[Pinia Stores]
        ACTIONS[Actions]
        GETTERS[Getters]
    end
    
    subgraph "服务层 (Service Layer)"
        API_CLIENT[API客户端]
        AUTH_SVC[认证服务]
        STORAGE[本地存储服务]
        UTILS[工具函数]
    end
    
    subgraph "路由层 (Router Layer)"
        ROUTES[路由配置]
        GUARDS[路由守卫]
        MIDDLEWARE[中间件]
    end
    
    VIEWS --> STORES
    COMPS --> STORES
    STORES --> API_CLIENT
    API_CLIENT --> AUTH_SVC
    ROUTES --> GUARDS
    GUARDS --> AUTH_SVC
```

### 2.2 后端分层架构

```mermaid
graph TD
    subgraph "接口层 (API Layer)"
        URLS[URL路由]
        VIEWS[DRF视图]
        SERIALIZERS[序列化器]
    end
    
    subgraph "业务逻辑层 (Business Logic Layer)"
        SERVICES[业务服务]
        VALIDATORS[验证器]
        PERMISSIONS[权限控制]
    end
    
    subgraph "数据访问层 (Data Access Layer)"
        MODELS[Django模型]
        MANAGERS[模型管理器]
        QUERYSETS[查询集]
    end
    
    subgraph "中间件层 (Middleware Layer)"
        AUTH_MW[认证中间件]
        CORS_MW[CORS中间件]
        CACHE_MW[缓存中间件]
        LOG_MW[日志中间件]
    end
    
    URLS --> VIEWS
    VIEWS --> SERIALIZERS
    VIEWS --> SERVICES
    SERVICES --> VALIDATORS
    SERVICES --> PERMISSIONS
    SERVICES --> MODELS
    MODELS --> MANAGERS
    MANAGERS --> QUERYSETS
```

### 2.3 核心组件定义

| 组件类型 | 组件名称 | 职责描述 |
|----------|----------|----------|
| 前端组件 | AuthGuard | 路由认证守卫，控制页面访问权限 |
| 前端组件 | ApiClient | HTTP请求封装，统一处理API调用 |
| 前端组件 | UserStore | 用户状态管理，处理登录状态和用户信息 |
| 前端组件 | MedicineStore | 药品状态管理，处理药品列表和操作 |
| 前端组件 | NotificationService | 通知服务，处理系统提醒和消息 |
| 后端组件 | AuthenticationService | 认证服务，处理用户登录和token验证 |
| 后端组件 | MedicineService | 药品业务服务，处理药品相关业务逻辑 |
| 后端组件 | ReminderService | 提醒业务服务，处理用药提醒逻辑 |
| 后端组件 | AISearchService | AI搜索服务，集成大模型API |
| 后端组件 | CacheService | 缓存服务，处理Redis缓存操作 |

## 3. 模块依赖关系图

### 3.1 前端模块依赖

```mermaid
graph TD
    subgraph "页面模块"
        WELCOME[欢迎页面]
        DASHBOARD[主导航页面]
        MEDICINES[药品管理页面]
        RECORDS[用药记录页面]
        REMINDERS[用药提醒页面]
        PLANS[用药计划页面]
        MEDICAL[就医记录页面]
        ADMIN[后台管理页面]
    end
    
    subgraph "共享模块"
        AUTH[认证模块]
        API[API模块]
        STORE[状态管理模块]
        UTILS[工具模块]
        COMPONENTS[组件模块]
    end
    
    WELCOME --> AUTH
    DASHBOARD --> AUTH
    DASHBOARD --> STORE
    MEDICINES --> AUTH
    MEDICINES --> API
    MEDICINES --> STORE
    RECORDS --> AUTH
    RECORDS --> API
    REMINDERS --> AUTH
    REMINDERS --> API
    PLANS --> AUTH
    PLANS --> API
    MEDICAL --> AUTH
    MEDICAL --> API
    ADMIN --> AUTH
    ADMIN --> API
    
    API --> UTILS
    STORE --> API
    AUTH --> API
    
    MEDICINES --> COMPONENTS
    RECORDS --> COMPONENTS
    REMINDERS --> COMPONENTS
    PLANS --> COMPONENTS
    MEDICAL --> COMPONENTS
```

### 3.2 后端模块依赖

```mermaid
graph TD
    subgraph "应用模块"
        AUTH_APP[认证应用]
        USER_APP[用户应用]
        MEDICINE_APP[药品应用]
        RECORD_APP[记录应用]
        REMINDER_APP[提醒应用]
        PLAN_APP[计划应用]
        MEDICAL_APP[就医应用]
    end
    
    subgraph "核心模块"
        CORE[核心模块]
        UTILS[工具模块]
        MIDDLEWARE[中间件模块]
        CACHE[缓存模块]
    end
    
    subgraph "第三方模块"
        DRF[Django REST Framework]
        REDIS_CLIENT[Redis客户端]
        AI_CLIENT[AI客户端]
    end
    
    AUTH_APP --> CORE
    USER_APP --> CORE
    MEDICINE_APP --> CORE
    RECORD_APP --> CORE
    REMINDER_APP --> CORE
    PLAN_APP --> CORE
    MEDICAL_APP --> CORE
    
    MEDICINE_APP --> USER_APP
    RECORD_APP --> MEDICINE_APP
    REMINDER_APP --> MEDICINE_APP
    PLAN_APP --> MEDICINE_APP
    MEDICAL_APP --> USER_APP
    
    CORE --> UTILS
    CORE --> MIDDLEWARE
    CORE --> CACHE
    
    MIDDLEWARE --> DRF
    CACHE --> REDIS_CLIENT
    MEDICINE_APP --> AI_CLIENT
```

## 4. 接口契约定义

### 4.1 前端接口契约

```typescript
// 用户认证接口
interface AuthAPI {
  login(credentials: LoginRequest): Promise<AuthResponse>
  register(userData: RegisterRequest): Promise<AuthResponse>
  logout(): Promise<void>
  refreshToken(): Promise<TokenResponse>
  sendVerificationCode(phone: string): Promise<void>
}

// 药品管理接口
interface MedicineAPI {
  getMedicines(params?: MedicineQueryParams): Promise<MedicineListResponse>
  getMedicine(id: number): Promise<MedicineResponse>
  createMedicine(data: CreateMedicineRequest): Promise<MedicineResponse>
  updateMedicine(id: number, data: UpdateMedicineRequest): Promise<MedicineResponse>
  deleteMedicine(id: number): Promise<void>
  searchMedicines(query: string): Promise<MedicineSearchResponse>
}

// 用药记录接口
interface RecordAPI {
  getRecords(params?: RecordQueryParams): Promise<RecordListResponse>
  createRecord(data: CreateRecordRequest): Promise<RecordResponse>
  getStatistics(params?: StatisticsParams): Promise<StatisticsResponse>
}

// 用药提醒接口
interface ReminderAPI {
  getReminders(params?: ReminderQueryParams): Promise<ReminderListResponse>
  createReminder(data: CreateReminderRequest): Promise<ReminderResponse>
  updateReminder(id: number, data: UpdateReminderRequest): Promise<ReminderResponse>
  deleteReminder(id: number): Promise<void>
  toggleReminder(id: number, active: boolean): Promise<void>
}
```

### 4.2 后端接口契约

```python
# 认证视图接口
class AuthViewSet:
    def login(self, request) -> Response
    def register(self, request) -> Response
    def logout(self, request) -> Response
    def refresh_token(self, request) -> Response
    def send_verification_code(self, request) -> Response

# 药品管理视图接口
class MedicineViewSet:
    def list(self, request) -> Response
    def retrieve(self, request, pk) -> Response
    def create(self, request) -> Response
    def update(self, request, pk) -> Response
    def destroy(self, request, pk) -> Response
    def search(self, request) -> Response

# 业务服务接口
class MedicineService:
    def get_user_medicines(self, user_id: int, filters: dict) -> QuerySet
    def create_medicine(self, user_id: int, data: dict) -> Medicine
    def update_medicine(self, medicine_id: int, data: dict) -> Medicine
    def delete_medicine(self, medicine_id: int) -> bool
    def search_medicines(self, user_id: int, query: str) -> List[Medicine]
    def check_expiry_warnings(self, user_id: int) -> List[Medicine]
```

### 4.3 数据传输对象(DTO)

```typescript
// 请求对象
interface LoginRequest {
  username: string
  password: string
}

interface CreateMedicineRequest {
  name: string
  specification?: string
  manufacturer?: string
  expiry_date?: string
  quantity: number
  storage_conditions?: string
  image?: File
  description?: string
}

// 响应对象
interface AuthResponse {
  success: boolean
  data: {
    user: User
    access_token: string
    refresh_token: string
  }
  message: string
}

interface MedicineResponse {
  success: boolean
  data: Medicine
  message: string
}

// 数据模型
interface User {
  id: number
  username: string
  phone: string
  email?: string
  is_admin: boolean
  created_at: string
}

interface Medicine {
  id: number
  name: string
  specification?: string
  manufacturer?: string
  expiry_date?: string
  quantity: number
  storage_conditions?: string
  image_url?: string
  description?: string
  created_at: string
  updated_at: string
}
```

## 5. 数据流向图

### 5.1 用户认证流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant A as 认证API
    participant D as 数据库
    participant R as Redis
    
    U->>F: 输入登录信息
    F->>A: POST /api/auth/login/
    A->>D: 验证用户凭据
    D-->>A: 返回用户信息
    A->>R: 存储会话信息
    A-->>F: 返回JWT Token
    F->>F: 存储Token到本地
    F-->>U: 跳转到主页面
```

### 5.2 药品管理流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant M as 药品API
    participant AI as AI服务
    participant D as 数据库
    participant C as 缓存
    
    U->>F: 搜索药品
    F->>M: GET /api/medicines/search/
    M->>C: 检查缓存
    alt 缓存命中
        C-->>M: 返回缓存结果
    else 缓存未命中
        M->>AI: 调用AI搜索
        AI-->>M: 返回搜索结果
        M->>D: 查询数据库
        D-->>M: 返回药品数据
        M->>C: 更新缓存
    end
    M-->>F: 返回搜索结果
    F-->>U: 显示药品列表
```

### 5.3 用药提醒流程

```mermaid
sequenceDiagram
    participant S as 系统调度器
    participant R as 提醒服务
    participant D as 数据库
    participant N as 通知服务
    participant U as 用户
    
    S->>R: 定时检查提醒
    R->>D: 查询活跃提醒
    D-->>R: 返回提醒列表
    loop 处理每个提醒
        R->>R: 检查提醒时间
        alt 到达提醒时间
            R->>N: 发送通知
            N->>U: 推送提醒消息
            R->>D: 记录提醒日志
        end
    end
```

## 6. 异常处理策略

### 6.1 前端异常处理

```mermaid
graph TD
    subgraph "异常类型"
        NET_ERR[网络异常]
        AUTH_ERR[认证异常]
        VALID_ERR[验证异常]
        SYS_ERR[系统异常]
    end
    
    subgraph "处理策略"
        RETRY[自动重试]
        REDIRECT[页面重定向]
        TOAST[消息提示]
        LOG[错误日志]
    end
    
    subgraph "用户体验"
        LOADING[加载状态]
        FALLBACK[降级方案]
        OFFLINE[离线模式]
    end
    
    NET_ERR --> RETRY
    NET_ERR --> TOAST
    NET_ERR --> OFFLINE
    
    AUTH_ERR --> REDIRECT
    AUTH_ERR --> TOAST
    
    VALID_ERR --> TOAST
    VALID_ERR --> LOG
    
    SYS_ERR --> FALLBACK
    SYS_ERR --> LOG
    SYS_ERR --> TOAST
```

### 6.2 后端异常处理

```mermaid
graph TD
    subgraph "异常层级"
        VIEW_EXC[视图层异常]
        SERVICE_EXC[服务层异常]
        MODEL_EXC[模型层异常]
        DB_EXC[数据库异常]
    end
    
    subgraph "处理机制"
        GLOBAL_HANDLER[全局异常处理器]
        CUSTOM_HANDLER[自定义异常处理器]
        MIDDLEWARE[异常中间件]
        LOGGER[日志记录器]
    end
    
    subgraph "响应策略"
        ERROR_RESP[错误响应]
        RETRY_LOGIC[重试逻辑]
        FALLBACK[降级处理]
        ALERT[告警通知]
    end
    
    VIEW_EXC --> GLOBAL_HANDLER
    SERVICE_EXC --> CUSTOM_HANDLER
    MODEL_EXC --> MIDDLEWARE
    DB_EXC --> MIDDLEWARE
    
    GLOBAL_HANDLER --> ERROR_RESP
    CUSTOM_HANDLER --> RETRY_LOGIC
    MIDDLEWARE --> LOGGER
    
    ERROR_RESP --> ALERT
    RETRY_LOGIC --> FALLBACK
```

### 6.3 异常处理规范

| 异常类型 | 处理策略 | 用户体验 | 技术实现 |
|----------|----------|----------|----------|
| 网络超时 | 自动重试3次，失败后提示 | 显示重试按钮 | axios拦截器 + 指数退避 |
| 认证失效 | 自动刷新token，失败后跳转登录 | 无感知刷新 | JWT自动刷新机制 |
| 数据验证失败 | 显示具体错误信息 | 表单字段高亮 | DRF序列化器验证 |
| 服务器错误 | 记录日志，显示友好提示 | 通用错误页面 | Django全局异常处理 |
| 数据库连接失败 | 启用缓存降级 | 显示缓存数据 | Redis缓存策略 |
| AI服务异常 | 降级到本地搜索 | 搜索功能正常 | 服务降级机制 |

### 6.4 监控和告警

```mermaid
graph LR
    subgraph "监控指标"
        PERF[性能指标]
        ERR[错误率]
        AVAIL[可用性]
        USAGE[使用量]
    end
    
    subgraph "告警规则"
        THRESHOLD[阈值告警]
        TREND[趋势告警]
        ANOMALY[异常检测]
    end
    
    subgraph "通知渠道"
        EMAIL[邮件通知]
        SMS[短信通知]
        WEBHOOK[Webhook]
    end
    
    PERF --> THRESHOLD
    ERR --> THRESHOLD
    AVAIL --> ANOMALY
    USAGE --> TREND
    
    THRESHOLD --> EMAIL
    TREND --> EMAIL
    ANOMALY --> SMS
    ANOMALY --> WEBHOOK
```

## 7. 安全架构设计

### 7.1 认证授权架构

```mermaid
graph TD
    subgraph "认证层"
        JWT[JWT Token]
        REFRESH[Refresh Token]
        SESSION[Session管理]
    end
    
    subgraph "授权层"
        RBAC[基于角色的访问控制]
        PERM[权限验证]
        GUARD[路由守卫]
    end
    
    subgraph "安全防护"
        CORS[跨域保护]
        CSRF[CSRF防护]
        XSS[XSS防护]
        RATE[频率限制]
    end
    
    JWT --> RBAC
    REFRESH --> SESSION
    RBAC --> PERM
    PERM --> GUARD
    
    GUARD --> CORS
    GUARD --> CSRF
    GUARD --> XSS
    GUARD --> RATE
```

### 7.2 数据安全策略

| 安全层面 | 保护措施 | 实现方式 |
|----------|----------|----------|
| 传输安全 | HTTPS加密 | SSL/TLS证书 |
| 存储安全 | 密码加密 | bcrypt哈希 |
| 接口安全 | API限流 | Django-ratelimit |
| 数据脱敏 | 敏感信息脱敏 | 序列化器过滤 |
| 访问控制 | 权限验证 | DRF权限类 |
| 审计日志 | 操作记录 | Django日志系统 |

## 8. 性能优化策略

### 8.1 前端性能优化

```mermaid
graph LR
    subgraph "加载优化"
        LAZY[懒加载]
        SPLIT[代码分割]
        CACHE[浏览器缓存]
    end
    
    subgraph "渲染优化"
        VDOM[虚拟DOM]
        MEMO[组件缓存]
        DEBOUNCE[防抖节流]
    end
    
    subgraph "网络优化"
        CDN[CDN加速]
        GZIP[Gzip压缩]
        HTTP2[HTTP/2]
    end
    
    LAZY --> VDOM
    SPLIT --> MEMO
    CACHE --> DEBOUNCE
    
    VDOM --> CDN
    MEMO --> GZIP
    DEBOUNCE --> HTTP2
```

### 8.2 后端性能优化

```mermaid
graph LR
    subgraph "数据库优化"
        INDEX[索引优化]
        QUERY[查询优化]
        POOL[连接池]
    end
    
    subgraph "缓存策略"
        REDIS_CACHE[Redis缓存]
        QUERY_CACHE[查询缓存]
        PAGE_CACHE[页面缓存]
    end
    
    subgraph "服务优化"
        ASYNC[异步处理]
        QUEUE[任务队列]
        LOAD_BALANCE[负载均衡]
    end
    
    INDEX --> REDIS_CACHE
    QUERY --> QUERY_CACHE
    POOL --> PAGE_CACHE
    
    REDIS_CACHE --> ASYNC
    QUERY_CACHE --> QUEUE
    PAGE_CACHE --> LOAD_BALANCE
```

## 9. 部署架构设计

### 9.1 容器化部署

```mermaid
graph TD
    subgraph "开发环境"
        DEV_FE[前端开发容器]
        DEV_BE[后端开发容器]
        DEV_DB[开发数据库]
    end
    
    subgraph "测试环境"
        TEST_FE[前端测试容器]
        TEST_BE[后端测试容器]
        TEST_DB[测试数据库]
    end
    
    subgraph "生产环境"
        PROD_FE[前端生产容器]
        PROD_BE[后端生产容器]
        PROD_DB[生产数据库]
        NGINX[Nginx代理]
    end
    
    DEV_FE --> TEST_FE
    DEV_BE --> TEST_BE
    DEV_DB --> TEST_DB
    
    TEST_FE --> PROD_FE
    TEST_BE --> PROD_BE
    TEST_DB --> PROD_DB
    
    NGINX --> PROD_FE
    NGINX --> PROD_BE
```

### 9.2 服务编排

```yaml
# docker-compose.yml 架构示例
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    environment:
      - DATABASE_URL=mysql://user:pass@mysql:3306/mtm_helper
      - REDIS_URL=redis://redis:6379/0
  
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=mtm_helper
    volumes:
      - mysql_data:/var/lib/mysql
  
  redis:
    image: redis:7.0
    command: redis-server --requirepass Med_Helper_Redis_2025!
    volumes:
      - redis_data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
```

## 10. 质量保证策略

### 10.1 测试策略

```mermaid
graph TD
    subgraph "测试金字塔"
        UNIT[单元测试]
        INTEGRATION[集成测试]
        E2E[端到端测试]
    end
    
    subgraph "测试类型"
        FUNC[功能测试]
        PERF[性能测试]
        SEC[安全测试]
        COMPAT[兼容性测试]
    end
    
    subgraph "自动化"
        CI[持续集成]
        CD[持续部署]
        MONITOR[监控告警]
    end
    
    UNIT --> FUNC
    INTEGRATION --> PERF
    E2E --> SEC
    E2E --> COMPAT
    
    FUNC --> CI
    PERF --> CI
    SEC --> CD
    COMPAT --> MONITOR
```

### 10.2 代码质量控制

| 质量维度 | 检查工具 | 质量标准 |
|----------|----------|----------|
| 代码规范 | ESLint + Prettier | 0 Lint错误 |
| 类型安全 | TypeScript | 严格模式 |
| 测试覆盖率 | Jest + Coverage | >80% |
| 代码复杂度 | SonarQube | 圈复杂度<10 |
| 安全扫描 | Snyk | 0高危漏洞 |
| 性能监控 | Lighthouse | 性能分数>90 |

---

**文档版本**: v1.0  
**创建日期**: 2025年1月  
**更新日期**: 2025年1月  
**负责人**: 系统架构师  
**审核状态**: 待审核