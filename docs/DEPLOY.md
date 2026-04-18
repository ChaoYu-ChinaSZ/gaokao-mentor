# 部署指南

本文档说明如何将 gaokao-mentor skill 部署到自己的 Hermes Gateway，使其可以被其他用户加载使用。

---

## 前置要求

- 已安装 Hermes Agent（建议最新版本）
- 消息平台接入（微信/飞书/钉钉等）
- Python 3.12+
- Git

---

## 安装步骤

### Step 1：克隆到本地 skills 目录

```bash
git clone https://github.com/ChaoYu-ChinaSZ/gaokao-mentor.git ~/.hermes/skills/gaokao-mentor
```

这会将仓库克隆到你的 Hermes skills 目录。

### Step 2：测试引擎

```bash
python3 ~/.hermes/skills/gaokao-mentor/scripts/test_engine.py
```

应看到类似输出：

```
测试通过！
模拟推荐专业：['计算机科学与技术', '电子信息']
推荐职业锚：AU, CH, TF
```

### Step 3：验证 skill 被加载

重启 hermes-agent：

```bash
hermes agent restart
```

或者在新消息到来时，agent 会自动扫描 skills 目录并加载。

### Step 4：确认微信接入（可选）

如果你希望通过微信对外服务，需要确保 hermes-gateway 已配置微信接入：

```bash
hermes gateway status
```

确保 `weixin` 状态为 `connected`。

---

## 配置说明

### Skill 路径

Skill 放在 `~/.hermes/skills/gaokao-mentor/` 目录下。

目录结构：

```
~/.hermes/skills/gaokao-mentor/
├── SKILL.md                        # Skill 元信息（Hermes 自动识别）
├── references/
│   └── engine.py                  # 核心引擎
└── scripts/
    └── test_engine.py            # 测试脚本
```

### 用户档案存储

用户对话数据存储在：

```
~/.hermes/gaokao_profiles/
```

每个用户一个 JSON 文件，文件名为 OpenID。

**如需迁移**：将整个 `gaokao_profiles/` 目录复制到新环境即可。

### Skill 更新

```bash
cd ~/.hermes/skills/gaokao-mentor
git pull origin main
```

---

## 对接自定义消息平台

如果你希望接入除了微信以外的消息平台（如飞书、钉钉、Telegram），需要查阅 [hermes-agent 文档](https://github.com/ChaoYu-ChinaSZ/hermes-agent)。

核心原则：消息通过 hermes-gateway 接收后，gateway 将消息转发给 Hermes Agent，Agent 根据消息内容判断是否触发 gaokao-mentor skill。整个流程不依赖于具体消息平台。

---

## 常见问题

### Q: agent 没有触发 skill，一直是闲聊回复

A: 检查 agent.log 确认 skill 是否被加载。SKILL.md 必须放在 `~/.hermes/skills/gaokao-mentor/SKILL.md`，agent 启动时会扫描 skills 目录。如果 skill 已加载但仍未触发，可能是 agent 判断逻辑问题，可以手动调用 `skill_view("gaokao-mentor")` 强制加载。

### Q: 微信消息收到但回复很短

A: 说明 agent 触发了 skill 但 engine.py 路径不对。请确保 engine.py 放在正确路径，并在 SKILL.md 中检查引用路径是否与实际路径一致。

### Q: 如何修改对话流程

A: 编辑 `references/engine.py` 中的状态机逻辑。如需修改问题文案，直接编辑对应的 prompt 文本即可。

---

## 生产环境注意事项

1. **用户档案备份**：定期备份 `~/.hermes/gaokao_profiles/` 目录
2. **LLM 调用限制**：确保 hermes-agent 的 LLM 配置满足并发需求
3. **微信接口稳定**：微信平台有消息接收限制，确保 gateway 稳定在线
