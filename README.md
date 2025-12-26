# ComfyUI-HDD-Story-Assistant

基于阿里通义千问 (Qwen) API 的 AI 漫剧/分镜/视频提示词辅助工具，为 ComfyUI 自定义节点扩展。

## 功能特性

本项目包含 4 个核心节点，全界面参数已强制为中文显示：

### 📊 HDD📊 剧本转分镜表格 V1.5
- 将文本剧本或已有分镜表格转换为标准化的分镜表格（包含镜号、阶段、角色、场景等9列）
- 支持文本剧本模式（自动分镜）和已有分镜表格模式（标准化整理）
- 输出标准 Excel 格式，可直接用于其他节点

### 👤 HDD👤 AI剧本角色分析 V1.5
- 读取剧本文件（Txt/Docx/Excel），分析并提取角色名及外貌特征
- 输出标准 JSON 格式（Key: 角色名, Value: 外貌描述）
- 支持测试模式，可直接测试 AI 功能

### 🎬 HDD🎬 AI漫剧分镜转绘图 V1.5
- 将小说/分镜脚本转换为绘图提示词（Midjourney/Flux 格式）
- 支持文件上传（自动分镜）或表格读取
- 支持角色设定数据注入（可连接角色分析节点）
- 内置详细的 System Prompt（包含光影、镜头语言等强制指令）

### 🎥 HDD🎥 AI漫剧图生视频 V1.5
- 结合单张图片 + 分镜文本，生成视频生成模型（Runway/Kling）的提示词
- 支持单图模式和批量模式
- 支持音效、BGM、台词提示生成
- 使用视觉模型（VL）进行多模态理解

## 安装方法

### 方法一：使用 Git（推荐）

1. 进入 ComfyUI 的 `custom_nodes` 目录：
```bash
cd ComfyUI/custom_nodes
```

2. 克隆仓库：
```bash
git clone https://github.com/你的用户名/ComfyUI-HDD-Story-Assistant.git
```

3. 安装依赖：
```bash
cd ComfyUI-HDD-Story-Assistant
pip install -r requirements.txt
```

### 方法二：手动安装

1. 下载或克隆本项目到 `ComfyUI/custom_nodes/ComfyUI-HDD-Story-Assistant` 目录

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 重启 ComfyUI

## 依赖要求

- Python 3.8+
- ComfyUI
- 以下 Python 包（会自动安装）：
  - pandas
  - openpyxl
  - xlrd>=2.0.1
  - openai
  - python-docx

## 配置说明

### API 密钥配置

所有节点都需要配置**阿里云 DashScope API 密钥**：

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 创建 API Key
3. 在节点中输入 API Key（格式：`sk-...`）

### 网络环境适配

代码已内置代理关闭逻辑，适配 AutoDL 等国内服务器环境。

## 使用说明

### 工作流程示例

1. **剧本转分镜表格** → 生成标准化的分镜表格
2. **角色分析** → 提取角色设定（可选）
3. **分镜转绘图** → 生成绘图提示词（可连接角色分析节点）
4. **图生视频** → 结合图片和分镜生成视频提示词

### 节点连接示例

```
[剧本转分镜表格] → [分镜转绘图]
                    ↓
[角色分析] ────────┘
                    ↓
              [图生视频]
```

## 文件结构

```
ComfyUI-HDD-Story-Assistant/
├── __init__.py              # 节点注册入口
├── hdd_nodes.py             # 核心 Python 后端逻辑
├── requirements.txt         # 依赖库列表
├── README.md                # 本文件
├── .gitignore               # Git 忽略文件
├── js/
│   └── hdd_ui.js            # 前端扩展脚本
└── locales/
    └── zh/
        └── nodeDefs.json    # 中文本地化定义
```

## 版本信息

- **当前版本**: V1.5
- **最后更新**: 2025年

## 注意事项

1. **API 供应商限制**：本项目仅支持阿里云 DashScope (Qwen) API，已移除其他 API 供应商支持
2. **网络环境**：代码已内置代理关闭逻辑，适配 AutoDL 等国内服务器
3. **文件格式**：支持 Txt、Docx、Excel (xlsx/xls)、CSV 格式

## 常见问题

### Q: 节点无法加载？
A: 确保已安装所有依赖：`pip install -r requirements.txt`

### Q: API 调用失败？
A: 检查 API 密钥是否正确，以及网络连接是否正常

### Q: 文件上传失败？
A: 确保文件格式正确，且文件大小在合理范围内

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

