# 高考志愿 Mentor 系统

> AI驱动的自我认知与专业选择对话引擎

**让每一个高三学生，在填报志愿之前，先真正认识自己。**

---

## 是什么

高考志愿 Mentor 是一个基于 Hermens Agent 的对话式咨询系统。它不像传统志愿工具那样"告诉你应该选什么"，而是**通过对话，引导学生梳理自己的兴趣、能力和价值观**，从而做出更自主、更清晰的选择。

核心方法论：
- **Ikigai 四问** — 热爱、擅长、世界需要、愿景
- **现实约束探测** — 家庭因素、经济条件、生活节奏
- **RIASEC 职业兴趣测评** — 量化职业兴趣维度

---

## 效果

学生完成整个对话流程后，获得：
- 个人 RIASEC 职业兴趣雷达图
- 推荐专业方向（3-5个）
- 职业锚倾向推断（供内部参考）
- 基于现实约束的个性化备注

---

## 快速开始

### 前提条件

- 已安装 [Hermes Agent](https://github.com/ChaoYu-ChinaSZ/hermes-agent)
- Python 3.12+
- 微信/飞书/钉钉等消息平台（用于接收用户消息）

### 安装

```bash
# 1. 克隆仓库到本地 skills 目录
git clone https://github.com/ChaoYu-ChinaSZ/gaokao-mentor.git ~/.hermes/skills/gaokao-mentor

# 2. 测试引擎是否正常
python3 ~/.hermes/skills/gaokao-mentor/scripts/test_engine.py

# 3. 重启 hermes-agent，使新 skill 生效
hermes agent restart
```

### 使用

用户在微信发送以下任一消息，自动触发对话：

- "高考志愿"
- "高考咨询"
- "开始咨询"
- "我不知道选什么专业"

系统将自动引导用户完成完整的自我认知对话。

---

## 文档

- [使用指南](docs/USER_GUIDE.md) — 学生如何使用
- [部署指南](docs/DEPLOY.md) — 如何对接自己的 Hermes Gateway
- [技术说明](docs/TECHNICAL.md) — 架构、原理、核心算法

---

## 设计原则

1. **不 push** — 不给结论，让学生自己得出方向
2. **不贴标签** — 不说"你是XX型人"，而是展示维度分布
3. **尊重选择** — 家庭约束、经济条件是真实约束，不是障碍
4. **透明可解释** — 每个推荐都有推理路径，不是黑箱

---

## 未来计划

- [ ] V2.0 DYL 奥德赛计划（初步清晰学生适用）
- [ ] V2.0 院校匹配层（分数 → 可用院校）
- [ ] 多语言支持

---

## 相关项目

- [hermes-agent](https://github.com/ChaoYu-ChinaSZ/hermes-agent) — 本系统运行的 Agent 平台
- [mentor-prototype](https://github.com/ChaoYu-ChinaSZ/mentor-prototype) — 手动原型验证版本

---

MIT License. 自由使用，署名引用。
