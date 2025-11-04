# pkg_resources 弃用警告修复方案

## 问题描述

在应用侧连通性自检过程中，发现以下警告：

`
DeprecationWarning: pkg_resources is deprecated as an API
`

这是因为 pkg_resources 模块已被标记为弃用，将在未来版本中移除。

## 修复方案

### 方案一：固定 setuptools 版本 (短期解决方案)

在 equirements.txt 中添加以下内容：

`
setuptools<81.0.0
`

这将固定 setuptools 版本在 81.0.0 以下，避免弃用警告。

**优点**：
- 实施简单，只需修改一行代码
- 不需要修改现有代码逻辑
- 立即解决警告问题

**缺点**：
- 只是临时解决方案
- 限制了 setuptools 的版本更新
- 未来仍需迁移到新 API

### 方案二：迁移到 importlib.metadata (长期解决方案)

将代码中的 pkg_resources 替换为 importlib.metadata：

`python
# 旧代码
import pkg_resources
version = pkg_resources.get_distribution("package_name").version

# 新代码
from importlib.metadata import version
version = version("package_name")
`

**优点**：
- 符合 Python 未来发展方向
- 使用官方推荐的 API
- 彻底解决弃用警告

**缺点**：
- 需要修改所有使用 pkg_resources 的代码
- 可能需要适配不同的 API 差异
- Python 3.8+ 才完全支持 importlib.metadata

## 实施建议

1. **短期**：先实施方案一，固定 setuptools 版本，快速消除警告
2. **长期**：计划实施方案二，逐步迁移到 importlib.metadata

## 实施步骤

### 方案一实施步骤

1. 编辑 equirements.txt：
   `
   # 添加以下行
   setuptools<81.0.0
   `

2. 重新安装依赖：
   `
   pip install -r requirements.txt
   `

3. 验证警告是否消除：
   `
   python test_db.py
   `

### 方案二实施步骤

1. 搜索项目中所有使用 pkg_resources 的地方：
   `
   grep -r "pkg_resources" .
   `

2. 逐一替换为 importlib.metadata：
   - 对于版本获取：使用 importlib.metadata.version
   - 对于入口点：使用 importlib.metadata.entry_points
   - 对于资源访问：使用 importlib.resources

3. 更新 requirements.txt：
   - Python 3.8 以下需添加：importlib-metadata
   - Python 3.8+ 无需额外依赖

4. 测试所有功能，确保迁移无误

## 参考资源

- [importlib.metadata 文档](https://docs.python.org/3/library/importlib.metadata.html)
- [setuptools 弃用公告](https://setuptools.pypa.io/en/latest/pkg_resources.html)
- [Python 打包用户指南](https://packaging.python.org/en/latest/guides/tool-recommendations/)
