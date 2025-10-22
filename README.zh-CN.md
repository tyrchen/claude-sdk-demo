# PostgreSQL 数据库架构生成器 🚀

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 使用 AI 将你的应用创意转化为生产就绪的 PostgreSQL 数据库架构

[English](README.md) | [中文](README.zh-CN.md)

## ✨ 功能特性

- 🤖 **AI 驱动的架构生成** - 用自然语言描述你的应用，自动生成专业的 PostgreSQL 迁移脚本
- 📊 **实时进度追踪** - 精美的 CLI 界面，实时显示任务更新和进度动画
- ✅ **自动验证** - 在保存前对临时数据库测试每个迁移脚本
- 🔄 **智能迭代** - 自动修复错误并重试直到成功
- 📝 **真实种子数据** - 生成尊重所有约束和关系的示例数据
- 🎯 **生产就绪** - 遵循 PostgreSQL 最佳实践，包含适当的索引、约束和事务

## 📸 演示

```bash
$ uv run build-idea -p /tmp/blog-app

Describe your idea: 一个包含用户、文章和评论的博客平台

Agent Execution (15.2s) - 正在生成文章表的迁移脚本...

[✓] 检查现有迁移和种子数据 (1.2s)
[✓] 设计博客平台架构 (3.5s)
[⠋] 生成迁移文件 (5.1s)
[ ] 生成种子数据
[ ] 验证迁移和种子数据
```

**最终输出：**

```markdown
## ✅ 博客平台架构创建成功！

### 📁 已创建的文件
- 迁移脚本：`./migrations/20250122103045_create_blog_schema.sql`
- 种子数据：`./seeds/20250122103045_initial_blog_data.sql`

### 🗄️ 数据库架构
**users 表** - 用户认证和个人资料
**posts 表** - 博客内容，关联用户
**comments 表** - 嵌套评论，级联删除

### ✅ 验证结果
✓ 迁移执行成功
✓ 插入了 15 条示例记录
✓ 所有约束和索引已验证
```

## 🚀 快速开始

### 前置要求

- Python 3.12 或更高版本
- PostgreSQL（用于验证）
- 已配置 API 访问的 Claude CLI

### 安装

```bash
# 克隆仓库
git clone <your-repo-url>
cd claude-sdk-bbl

# 安装依赖
uv sync

# 安装软件包
uv pip install -e .
```

### 使用方法

```bash
# 从你的想法生成架构
uv run build-idea -p /path/to/project

# 示例
uv run build-idea -p /tmp/my-app
```

当提示时，用自然语言描述你的应用创意：

```
Describe your idea: 一个包含商品、购物车和订单的电商平台
```

工具将会：
1. ✅ 分析你的需求
2. ✅ 检查现有迁移（如果有）
3. ✅ 生成全面的迁移文件
4. ✅ 创建真实的种子数据
5. ✅ 使用临时数据库验证一切正常
6. ✅ 自动修复错误直到成功

## 📁 输出结构

```
/your/project/
├── migrations/
│   └── 20250122103045_create_schema.sql
└── seeds/
    └── 20250122103045_initial_data.sql
```

### 迁移文件示例

```sql
-- Migration: 创建电商架构
-- Created: 20250122103045

BEGIN;

CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

COMMIT;
```

## 🏗️ 架构设计

### 代理系统 (`./agents/`)

**`postgres_agent.py`** - 主代理实现
- 使用 Claude SDK 进行 AI 驱动的架构生成
- 实现钩子通过 `TodoWrite` 捕获进度
- 流式传输消息以实现实时 UI 更新

### CLI 界面 (`./cli/`)

**`main.py`** - 交互式命令行界面
- 使用 **Click** 进行参数解析
- 使用 **Rich** 实现精美的实时更新 UI
- 功能特性：
  - 带有动画的实时进度追踪
  - 任务计时和状态指示器
  - 优雅的 Markdown 结果渲染

### 系统提示词 (`./specs/`)

**`system-prompt.md`** - PostgreSQL 专家提示词
- 迁移生成的全面工作流程
- 架构设计的最佳实践
- 自动验证和错误处理
- 每次执行强制生成单个迁移文件

## 🎯 工作原理

1. **用户输入** → 描述你的应用创意
2. **AI 分析** → Claude 分析并规划架构
3. **架构生成** → 创建包含以下内容的迁移：
   - 适当的数据类型和约束
   - 外键关系
   - 性能索引
   - 事务安全
4. **种子数据** → 生成真实的示例数据
5. **验证** → 针对临时 PostgreSQL 数据库测试
6. **错误处理** → 自动修复并重试直到成功

## 🛠️ 开发

```bash
# 以开发模式安装
uv pip install -e .

# 运行并输出调试信息
uv run build-idea -p /tmp/test

# 检查生成的文件
ls -la /tmp/test/migrations/
ls -la /tmp/test/seeds/
```

## 📋 系统要求

- **Python 3.12+** - 现代 async/await 支持
- **PostgreSQL** - 用于架构验证
  - `createdb` - 创建临时数据库
  - `psql` - 执行 SQL 脚本
  - `dropdb` - 清理临时数据库
- **Claude API** - 通过 Claude CLI 配置

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 基于 [Claude SDK for Python](https://github.com/anthropics/claude-sdk-python) 构建
- UI 由 [Rich](https://github.com/Textualize/rich) 驱动
- CLI 框架：[Click](https://click.palletsprojects.com/)

## 💡 使用技巧

### 增量迁移

对于复杂应用，从简单开始逐步构建：

```bash
# 第一次运行 - 基础架构
uv run build-idea -p /tmp/app
# 输入："用户认证系统"

# 第二次运行 - 添加功能
uv run build-idea -p /tmp/app
# 输入："添加用户头像和个人简介字段"
```

### 最佳实践

- ✅ 在生产环境运行前检查生成的迁移脚本
- ✅ 将迁移文件纳入版本控制
- ✅ 测试种子数据是否符合应用需求
- ✅ 运行验证以确保架构正确性

## 🐛 故障排除

### 钩子未捕获待办事项？

确保使用支持 `ClaudeSDKClient` 的最新版本。

### 找不到 PostgreSQL 命令？

确保 PostgreSQL 已安装并在 PATH 中：
```bash
which psql createdb dropdb
```

### 权限错误？

代理以 `bypassPermissions` 模式运行。检查你的 Claude CLI 配置。

---

**祝你架构生成愉快！🎉**

如果这个工具对你有帮助，请为仓库点个 ⭐ 星标！
