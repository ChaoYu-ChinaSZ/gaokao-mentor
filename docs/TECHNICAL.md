# 技术说明

本文档面向希望理解系统原理、修改源码或二次开发的开发者。

---

## 系统架构

```
微信用户发消息
    ↓
hermes-gateway（消息接入层）
    ↓
Hermes Agent（AI推理层，含LLM）
    ↓
gaokao-mentor Skill（业务逻辑层）
    ↓
MentorEngine + CandidateProfile（对话引擎 + 用户档案）
    ↓
用户档案（~/.hermes/gaokao_profiles/{openid}.json）
    ↓
回复文本 → gateway → 微信用户
```

**关键点**：本 skill 不直接调用 LLM，而是通过 Hermes Agent 间接调用。skill 的职责是维护对话状态机、管理用户档案、生成回复文本。

---

## 核心模块

### CandidateProfile（用户档案）

```python
@dataclass
class CandidateProfile:
    student_id: str                    # 微信 OpenID
    # Ikigai 四问
    ikigai_love: str                  # Q1 热爱
    ikigai_good_at: str              # Q2 擅长
    ikigai_world_needs: str          # Q3 使命
    ikigai_vision: str               # Q4 愿景
    # 现实约束
    constraint_family: str            # F1
    constraint_economic: str          # F2
    constraint_only_child: str        # F3
    life_work_choice: str           # L1
    life_work_pace: str             # L2
    life_work_meaning: str          # L3
    inferred_anchors: list          # 推断职业锚
    # RIASEC
    riasec_answers: dict           # {qid: score}
    riasec_scores: dict            # {R: %, I: %, ...}
    top_dimensions: list           # [dim1, dim2]
    recommended_majors: list        # 推荐专业
    # 状态
    current_state: State            # 当前对话状态
    clarity_level: str              # 清晰度评估
```

档案路径：`~/.hermes/gaokao_profiles/{openid}.json`

### MentorEngine（对话引擎）

负责：
1. 根据当前状态（State）判断下一步该问什么问题
2. 接收用户回答，存入 CandidateProfile
3. 在特定状态（如 IKIGAI_SUMMARY、OUTPUT）调用 LLM 生成小结/推荐
4. 返回下一轮回复文本

### 状态机（State Enum）

```python
class State(Enum):
    START = "START"
    IKIGAI_Q1 = "IKIGAI_Q1"
    IKIGAI_Q2 = "IKIGAI_Q2"
    IKIGAI_Q3 = "IKIGAI_Q3"
    IKIGAI_Q4 = "IKIGAI_Q4"
    IKIGAI_SUMMARY = "IKIGAI_SUMMARY"
    CONSTRAINT_CHECK = "CONSTRAINT_CHECK"
    RIASEC_INTRO = "RIASEC_INTRO"
    RIASEC_QUESTIONS = "RIASEC_QUESTIONS"
    CLARITY_CHECK = "CLARITY_CHECK"
    OUTPUT = "OUTPUT"
    END = "END"
```

---

## 推荐专业算法

### 输入

- `riasec_scores`: dict，每个维度的百分比（如 `{"R": 15, "I": 40, "A": 20, "S": 5, "E": 10, "C": 10}`）
- `top_dimensions`: list，突出维度（如 `["I", "A"]`）
- `inferred_anchors`: list，职业锚推断（如 `["AU", "CH", "TF"]`）

### 规则

**I强（研究型）→ 推荐：**
- 计算机科学与技术
- 电子信息工程
- 数据科学与大数据技术
- 生物医学工程
- 数学与应用数学

**R强（实际型）→ 推荐：**
- 机械工程
- 电气工程及其自动化
- 土木工程
- 材料成型及控制工程

**A强（艺术型）→ 推荐：**
- 数字媒体艺术
- 产品设计
- 视觉传达设计
- 建筑学

**I+R组合（技术研究型）→ 推荐：**
- 计算机科学与技术
- 电子信息
- 人工智能
- 机械工程

**I+A组合（创意研究型）→ 推荐：**
- 人工智能
- 人机交互设计
- 数字媒体技术

### 清晰度判断

```python
spread = max(scores) - min(scores)
if spread > 40:
    clarity = "清晰"
elif spread > 20:
    clarity = "初步清晰"
else:
    clarity = "模糊"
```

---

## RIASEC 测评题设计

25 题，每题二选一。题目设计遵循霍兰德职业兴趣理论，每题对应一个或多个 RIASEC 维度。用户选择后，该选项对应的维度 +1 分。

最终得分归一化为百分比。

---

## 职业锚内部推断规则

不让学生做完整 Schein 职业锚量表（38题），而是根据已有数据推断：

| 条件 | 推断锚 |
|---|---|
| RIASEC I强 + 家庭自由度大 | AU（自主/独立型）、CH（挑战型）、TF（技术/功能型）|
| RIASEC E强 + 家庭自由度大 | EC（企业/创业型）、GM（管理型）|
| RIASEC S强 + 使命感强 | SV（服务/奉献型）|
| L1选"准时下班"或"平稳" | LS（生活型）|

---

## 与 Hermes Agent 的交互方式

Agent 收到用户消息后：

1. 识别触发关键词（"高考咨询"等）
2. 调用 `skill_view("gaokao-mentor")` 加载 SKILL.md
3. 根据 SKILL.md 的激活指令，执行 `execute_code` 加载 `engine.py`
4. 调用 `MentorEngine.process_input(user_message)`
5. 打印返回的 reply 文本，作为 Agent 回复推送用户

---

## 文件说明

| 文件 | 作用 |
|---|---|
| `SKILL.md` | Hermes Skill 元信息 + 激活指令 |
| `references/engine.py` | 核心引擎（状态机 + 档案管理 + 推荐算法）|
| `scripts/test_engine.py` | 单元测试，验证引擎正确性 |

---

## 测试

```bash
python3 ~/.hermes/skills/gaokao-mentor/scripts/test_engine.py
```

测试覆盖：
- 状态机流转（START → IKIGAI_Q1 → ... → OUTPUT → END）
- 档案持久化（保存 + 加载 + 恢复）
- RIASEC 计分
- 推荐专业生成
