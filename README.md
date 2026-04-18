# 高考志愿 Mentor 系统

> AI驱动的自我认知与专业选择对话引擎

**让每一个高三学生，在填报志愿之前，先真正认识自己。**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 是什么

高考志愿 Mentor 是一个基于 Hermes Agent 的对话式咨询系统。它不像传统志愿工具那样"告诉你应该选什么"，而是**通过对话，引导学生梳理自己的兴趣、能力和价值观**，从而做出更自主、更清晰的选择。

**完全免费。不问成绩。不承诺录取。只帮你更了解自己。**

---

## 效果

学生完成整个对话流程后，获得：
- 个人 **RIASEC 职业兴趣雷达图**
- 推荐专业方向（3-5个）
- 职业锚倾向推断（供内部参考）
- 基于现实约束的个性化备注

---

## 快速开始

### 前提条件

- [Hermes Agent](https://github.com/ChaoYu-ChinaSZ/hermes-agent)
- Python 3.12+
- 微信/飞书/钉钉等消息平台

### 安装

```bash
# 克隆到本地 skills 目录
git clone https://github.com/ChaoYu-ChinaSZ/gaokao-mentor.git ~/.hermes/skills/gaokao-mentor

# 测试引擎
python3 ~/.hermes/skills/gaokao-mentor/scripts/test_engine.py

# 重启 hermes-agent 使新 skill 生效
hermes agent restart
```

### 使用

在微信发送以下任一消息，自动触发对话：

```
高考咨询
```

---

## 反馈机制

系统内置用户反馈收集（V2.0+）：

- **自动触发**：对话结束后自动邀请评分（30秒）
- **深度反馈**：可选的5问结构化反馈（2分钟）
- **随时反馈**：任何时候输入"反馈"均可触发

你的反馈会直接推动下一版本优化。查看 [反馈收集方案](docs/FEEDBACK.md)。

---

## 文档

| 文档 | 内容 |
|---|---|
| [使用手册](docs/MANUAL.md) | 学生使用指南 / 机构运营指南 / 技术部署指南 |
| [推广方案](docs/PROMOTION.md) | 多平台推广策略与执行计划 |
| [反馈收集方案](docs/FEEDBACK.md) | 反馈收集机制、数据存储、闭环追踪 |
| [技术说明](docs/TECHNICAL.md) | 架构、推荐算法、核心原理 |
| [部署指南](docs/DEPLOY.md) | 对接自己的 Hermes Gateway |
| [贡献指南](CONTRIBUTING.md) | 如何参与贡献 |

---

## 设计原则

1. **不 push** — 不给结论，让学生自己得出方向
2. **不贴标签** — 不说"你是XX型人"，展示维度分布
3. **尊重选择** — 家庭约束是真实约束，不是障碍
4. **透明可解释** — 每个推荐都有推理路径
5. **反馈驱动** — 真实用户反馈持续优化产品

---

## 里程碑

| 版本 | 功能 | 状态 |
|---|---|---|
| V1.0 | 手动原型验证（微信演示） | ✅ 完成 |
| V1.1 | 自动化引擎 + 微信端到端 | ✅ 完成 |
| V2.0 | 反馈收集系统 + 院校匹配层 | 进行中 |

---

## 致谢

- [Hermes Agent](https://github.com/ChaoYu-ChinaSZ/hermes-agent) — 本系统运行的 Agent 平台
- [Ikigai](https://en.wikipedia.org/wiki/Ikigai) — 自我认知框架
- [RIASEC/Holland Code](https://en.wikipedia.org/wiki/Holland_Code_Theory) — 职业兴趣理论

---

MIT License. 自由使用，欢迎贡献。
