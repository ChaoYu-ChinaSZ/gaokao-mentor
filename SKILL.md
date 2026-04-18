---
name: gaokao-mentor
description: 高考志愿Mentor系统 — 微信自动化对话引擎
category: productivity
---

# gaokao-mentor Skill

## 激活条件（必须严格遵守）

**当用户在微信发送以下任何一条消息时，必须立即激活本 skill：**
- "高考志愿" / "高考咨询" / "志愿咨询"
- "帮我看看我适合什么" / "我不知道选什么专业"
- "开始咨询" / "专业咨询"
- 任何询问大学专业选择、高考志愿填报的消息

**激活后立即执行以下步骤：**

### Step 1：加载引擎
使用 `execute_code` 执行以下 Python 代码：

```python
import sys, os
sys.path.insert(0, "/home/yuchao/.hermes/skills/productivity/gaokao-mentor/references")

from engine import MentorEngine, CandidateProfile

# 从事件上下文获取 openid（微信用户的唯一标识）
# 如果不知道 openid，使用 "weixin_user" 作为默认值
openid = "weixin_user"  # 实际使用时从 event context 获取

# 加载或新建用户档案
profile = CandidateProfile.load(openid)
if profile is None:
    profile = CandidateProfile(student_id=openid)

# 创建引擎
engine = MentorEngine(profile)

# 处理用户消息，返回回复文本
reply = engine.process_input(user_message)

# 保存档案
profile.save()

print(reply)  # 输出即为推送给用户的回复
```

### Step 2：传递用户消息
将用户发送的原始消息作为 `user_message` 传入 `engine.process_input(user_message)`。

### Step 3：返回回复
`process_input` 的返回值（字符串）即为推送给用户的微信消息。直接将该字符串作为最终回复，无需额外处理。

---

## 状态机流程（完整）

```
START
  ↓
IKIGAI_Q1（热爱：什么时候时间过得很快？）
  ↓
IKIGAI_Q2（擅长：什么事情你稍微一认真就比人强？）
  ↓
IKIGAI_Q3（使命：世界最需要什么？）
  ↓
IKIGAI_Q4（愿景：5年后理想生活的一天）
  ↓
IKIGEA_SUMMARY（自我认知小结）
  ↓
CONSTRAINT_CHECK（现实约束探测，6问）
  F1: 家里人对你学什么专业，有没有明确期待或反对？
  F2: 经济角度看，有哪些承担不起的？
  F3: 是不是独生子女？
  L1: 工资高没时间 vs 工资一般准时下班，选哪个？
  L2: 拼命工作几年然后自由，还是一直平稳？
  L3: 工作是一辈子的事，还是一个阶段的事？
  ↓
RIASEC_INTRO（RIASEC测评说明）
  ↓
RIASEC_QUESTIONS（25题，选A或B）
  ↓
CLARITY_CHECK（清晰度判断 + 雷达图）
  ↓
OUTPUT（方向建议 + 约束/节奏备注）
  ↓
END
```

## 核心类参考

### CandidateProfile
```python
@dataclass
class CandidateProfile:
    student_id: str                    # OpenID
    # Ikigai四问
    ikigai_love: str                   # Q1 热爱
    ikigai_good_at: str               # Q2 擅长
    ikigai_world_needs: str           # Q3 使命
    ikigai_vision: str                # Q4 愿景
    # 现实约束
    constraint_family: str             # F1
    constraint_economic: str           # F2
    constraint_only_child: str         # F3
    life_work_choice: str             # L1
    life_work_pace: str               # L2
    life_work_meaning: str             # L3
    inferred_anchors: list            # 推断职业锚
    # RIASEC
    riasec_answers: dict              # {qid: score}
    riasec_scores: dict              # {R: %, I: %, ...}
    top_dimensions: list              # [dim1, dim2]
    recommended_majors: list           # 推荐专业
    # 状态
    current_state: State
    clarity_level: str                # 清晰/初步清晰/模糊
```

档案路径：`~/.hermes/gaokao_profiles/{openid}.json`

### MentorEngine
```python
from gaokao_mentor.references.engine import MentorEngine, CandidateProfile

engine = MentorEngine(profile)
reply = engine.process_input(user_message)
profile.save()
```

## 职业锚Mentor内部推断规则

不让学生做完整测评，由Mentor从Ikigai+RIASEC结果推断：

| 条件 | 推断锚 |
|---|---|
| RIASEC I强 + 家庭自由度大 | AU、CH、TF |
| RIASEC E强 + 家庭自由度大 | EC、GM |
| RIASEC S强 + 使命感强 | SV |
| L1选"准时下班"或"平稳" | LS |

推断结果作为推荐备注，不作为独立评估。

## 文件结构

```
~/.hermes/skills/productivity/gaokao-mentor/
├── SKILL.md
├── references/
│   ├── engine.py        # 核心引擎（已测试通过）
│   └── __pycache__/
└── scripts/
    └── test_engine.py    # 单元测试
```

## 技术要求

- Python 3.12+
- json、dataclasses（stdlib）
- 档案目录：`~/.hermes/gaokao_profiles/`（自动创建）
- 使用 Hermes Agent 内置 LLM（本 skill 不直接调用 LLM）

## 运行状态检查

```bash
# 本地引擎测试
python3 ~/.hermes/skills/productivity/gaokao-mentor/scripts/test_engine.py
```

## 经验记录：Agent为什么不触发Skill

**症状：** 用户发"高考咨询"到微信 → gateway日志显示消息收到（193字回复）→ agent没有跑MentorEngine状态机

**根因：** hermes-gateway的agent和CLI agent是**同一套skills系统**，共享~/.hermes/skills/目录。agent看到触发关键词后，**需要主动调用skill_view("gaokao-mentor")才会加载skill内容**。默认行为是直接用LLM聊天回复，不会自动触发。

**诊断方法：**
- gateway日志显示消息收到但回复很短（68~193字）→ skill未被加载
- agent日志(agent.log)搜"gaokao-mentor"无结果 → agent未调用该skill
- sqlite state.db: messages表role=assistant的content长度<200字 → 基本是闲聊回复

**教训：** SKILL.md不能写成"架构参考文档"，必须写成"激活执行文档"——明确写"当看到X时，**必须**执行以下Step 1/2/3"，用具体的Python代码和精确的文件路径告诉agent怎么做。

**进度**

- [x] V1.1 引擎开发完成，测试通过
- [x] V1.1 SKILL.md激活指令优化（让agent明确触发）
- [ ] V1.1 真实用户微信端到端测试
- [ ] V2.0 DYL奥德赛计划
- [ ] V2.0 院校匹配层（分数→院校）
