# ➕ 如何添加新 Skill

本文档介绍如何为个人小助手 Skill 合集添加新技能。

---

## 1. 确定分类

将你的 Skill 归入以下类别之一：

| 类别 | 路径 | 适用场景 |
|------|------|---------|
| **Agent** | `Agent/your-skill-name/` | Agent 协作、上下文管理、技能维护、代码审查流程等通用 AI 工作流 |
| **External** | `External/README.md` | 第三方外部 skill 索引，只记录名称、仓库地址、使用场景和迁移状态，不作为可加载 skill |
| **Work** | `Work/your-skill-name/` | 周报、演示文稿、发布、内容转换等工作场景 |
| **Fun** | `Fun/your-skill-name/` | 视频、壁纸、漫画、图片生成等休闲创作场景 |

## 2. 创建目录

```
personal-skills/
└── Agent/  (或 Work/Fun/)
    └── your-skill-name/       # 使用 kebab-case 命名
        ├── SKILL.md            # 必须：技能说明文件
        ├── scripts/            # 可选：辅助脚本
        ├── references/         # 可选：参考资料/模板
        └── examples/           # 可选：示例文件
```

如果只是记录第三方外部 skill，不要创建普通 skill 目录，直接更新：

```text
External/README.md
```

`External/` 不要求包含 `SKILL.md`，它不是可加载 skill，只是迁移和安装索引。

## 3. 编写 SKILL.md

每个 Skill **必须** 包含一个 `SKILL.md` 文件，使用以下模板：

```markdown
---
name: your-skill-name
version: 1.0.0
description: 一句话描述该技能的功能和触发关键字
---

# Skill 名称

简要说明该技能的用途。

## 前置依赖

列出需要安装的工具或依赖（如没有则省略此节）。

## 使用说明

### 步骤1：[描述]
详细说明每个步骤...

### 步骤2：[描述]
...

## 示例

提供一个典型的使用场景对话示例。

## 错误处理

列出常见问题及解决方案（如适用）。
```

## 4. 更新 README

在 `README.md` 对应分类的表格中添加一行：

```markdown
| [your-skill-name](Work/your-skill-name/) | `触发关键字` | 简要功能描述 |
```

如果 README 表格包含“直接调用示例”列，也补充一条可复制的调用句：

```markdown
| [your-skill-name](Agent/your-skill-name/) | `触发关键字` | `使用 your-skill-name skill，完成...` | 简要功能描述 |
```

如果只是新增第三方外部 skill 记录，更新 `External/README.md` 的索引表即可；通常不需要修改根目录 README，除非新增了新的外部索引分组或规则。

## 5. 命名规范

- 目录名：使用 **kebab-case**（如 `weekly-report`、`video-downloader`）
- SKILL.md 中的 `name` 字段与目录名保持一致
- `description` 字段包含中英文触发关键字，方便检索

---

## 💡 Tips

- 尽量让 SKILL.md **自包含**，AI Agent 只需读取一个文件就能理解如何执行
- 如果 Skill 依赖外部脚本，放在 `scripts/` 子目录
- 如果需要模板或参考资料，放在 `references/` 子目录
- 保持每个 Skill 目录独立，避免跨 Skill 的依赖
