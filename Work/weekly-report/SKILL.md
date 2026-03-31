---
name: weekly-report
description: 生成每周报告，当用户输入"weekly report"时，触发该技能，让用户先提供本周的工作内容，然后参考周报模板进行生成
---

# Weekly Report

This skill generates a weekly report for the user.
## Instructions

1.  当用户输入"weekly report"或者"生成周报"或者"写周报"时，触发该技能
2.  让用户先提供本周的工作内容明细
3.  然后读取REFERENCE.md里的周报模板，参考周报模板进行生成
4.  生成的周报内容以markdown格式保存到reports文件夹下，文件名为report_YYYY-MM-DD_<timestamp>.md

## Examples

1.  当用户输入"weekly report"或者"生成周报"或者"写周报"时，触发该技能
2.  让用户先提供本周的工作内容明细
3.  然后读取REFERENCE.md里的周报模板，参考周报模板进行生成
4.  生成的周报内容以markdown格式保存到reports文件夹下，文件名为report_YYYY-MM-DD_<timestamp>.md
