---
name: growth
description: 个人成长追踪技能，围绕健康、英语学习、财务计划三大板块，支持日常记录与周期报告生成。触发命令：growth log health / growth log english / growth log finance / growth report
---

# Personal Growth Tracker

一站式个人成长追踪工具，帮助你系统化地记录健康状况、英语学习进度和财务状况，并生成周期性对比报告。

## 子命令

| 命令 | 说明 |
|------|------|
| `growth log health` | 记录当日健康数据 |
| `growth log english` | 记录当日英语学习情况 |
| `growth log finance` | 记录当日收支与投资 |
| `growth report` | 生成周/月对比报告 |

## Instructions

### 1. `growth log health` — 健康日志

1. 读取 `templates/daily_health.md` 模板
2. 引导用户逐项填写：睡眠、运动、饮食、体重、身体状态
3. 用户可以只提供部分信息，未提供的标记为"未记录"
4. 保存到 `logs/health/YYYY-MM-DD.md`

### 2. `growth log english` — 英语学习日志

1. 读取 `templates/daily_english.md` 模板
2. 引导用户填写：新学词汇、阅读材料、口语/听力练习、今日收获
3. 用户可以自由描述，助手帮助结构化整理
4. 保存到 `logs/english/YYYY-MM-DD.md`

### 3. `growth log finance` — 财务记录

1. 读取 `templates/daily_finance.md` 模板
2. 引导用户记录：收支明细、分类、投资动态、储蓄进度
3. 自动计算当日净收支
4. 保存到 `logs/finance/YYYY-MM-DD.md`

### 4. `growth report` — 周期报告

1. 询问用户生成报告的周期：**周报** 或 **月报**
2. 读取 `templates/weekly_report.md` 模板
3. 扫描 `logs/` 下对应周期内的所有日志文件
4. 汇总三大板块数据，与上一周期对比
5. 生成趋势分析与改进建议
6. 保存到 `reports/report_YYYY-MM-DD.md`

**报告包含：**
- 📊 健康数据周汇总（平均睡眠、运动频次、体重变化）
- 📚 英语学习周汇总（词汇总量、学习时长、进步点）
- 💰 财务周汇总（总收入、总支出、净储蓄、投资收益）
- 📈 与上周期对比（↑ 提升 / ↓ 下降 / → 持平）
- 🎯 下周期目标建议

## Examples

**示例 1: 记录健康**
```
用户: growth log health
助手: 请提供今天的健康数据：
用户: 昨晚11点睡7点起，跑步30分钟，体重72kg
助手: [生成结构化日志并保存]
```

**示例 2: 生成周报**
```
用户: growth report
助手: 请选择报告周期：周报 / 月报？
用户: 周报
助手: [扫描本周日志，生成对比报告]
```
