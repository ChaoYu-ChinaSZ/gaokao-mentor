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
import sys
sys.path.insert(0, "/home/yuchao/.hermes/skills/productivity/gaokao-mentor/references")
from engine import MentorEngine, CandidateProfile

# student_id：微信用户的 openid（如果是微信消息可从 event context 获取）
openid = "weixin_user"
profile = CandidateProfile.load(openid)
if profile is None:
    profile = CandidateProfile(student_id=openid)

engine = MentorEngine(profile)
reply = engine.process_input(user_message)
profile.save()
print(reply)
```

### Step 2：传递用户消息
将用户发送的原始消息作为 `user_message` 传入 `engine.process_input(user_message)`。

### Step 3：返回回复
`process_input` 的返回值（字符串）即为推送给用户的微信消息。直接将该字符串作为最终回复。

### Step 4：反馈收集
用户在任何时候发送"反馈"、"意见"或"建议"，立即触发反馈收集流程（无需退出当前状态）。

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
IKIGAI_SUMMARY（自我认知小结）
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
FEEDBACK_RATING ←─────────────┐
  ↓                         │
FEEDBACK_DETAIL              │ 用户任何时候
  ↓                         │ 输入"反馈"/
FEEDBACK_SAVED               │ "意见"/"建议"
  ↓                         │ 均可触发
END ─────────────────────────┘
```

---

## 反馈收集机制

### 触发方式
1. **自动触发**：OUTPUT 状态结束后，自动进入 FEEDBACK_RATING
2. **手动触发**：用户在任何状态发送"反馈"/"意见"/"建议"，立即拦截并进入反馈流程

### 反馈层级

**第一层：满意度评分（必填，但可跳过）**
```
这次对话，你感觉：
① 有帮助  ② 一般  ③ 没用
直接回复数字 1、2 或 3 即可
```

**第二层：深度反馈（可选）**
```
你愿意花2分钟填写详细反馈吗？
回复"详细反馈"开始，或直接说"不用了"关闭对话。
```

**第三层：结构化问题**
```
1. 推荐的专业方向，你之前了解过吗？
   A. 完全没听说过  B. 听说过但没深入  C. 了解过
2. 推荐结果和你的自我认知相比：
   A. 非常符合  B. 部分符合  C. 不太符合  D. 完全不符
3. 对话中哪个部分最有价值？
   A. Ikigai四问  B. 现实约束探测  C. RIASEC测评  D. 最终推荐
请依次回复，如：A B C
```

**第四层：自由文字**
```
收到！你觉得哪里可以更好？
（直接打字发过来，或者回复"没有"跳过）
```

### 反馈数据存储
```python
profile.feedback_rating = 1/2/3
profile.feedback_match = "A/B/C/D"
profile.feedback_valuable = "A/B/C/D"
profile.feedback_free = "文字内容"
```

---

## 核心类参考

### CandidateProfile
```python
@dataclass
class CandidateProfile:
    student_id: str                    # OpenID
    ikigai_love: str                  # Q1 热爱
    ikigai_good_at: str               # Q2 擅长
    ikigai_world_needs: str           # Q3 使命
    ikigai_vision: str                # Q4 愿景
    constraint_family: str             # F1
    constraint_economic: str          # F2
    constraint_only_child: str         # F3
    life_work_choice: str            # L1
    life_work_pace: str              # L2
    life_work_meaning: str           # L3
    inferred_anchors: list           # 推断职业锚
    riasec_answers: dict             # {qid: score}
    riasec_scores: dict              # {R: %, I: %, ...}
    top_dimensions: list             # [dim1, dim2]
    recommended_majors: list          # 推荐专业
    current_state: State
    clarity_level: str               # 清晰/初步清晰/模糊
    # 反馈（V2.0新增）
    feedback_rating: int             # 1/2/3
    feedback_match: str              # A/B/C/D
    feedback_valuable: str           # A/B/C/D
    feedback_free: str              # 自由文字
```

档案路径：`~/.hermes/gaokao_profiles/{openid}.json`

---

## 职业锚推断规则

| 条件 | 推断锚 |
|---|---|
| RIASEC I强 + 家庭自由度大 | AU、CH、TF |
| RIASEC E强 + 家庭自由度大 | EC、GM |
| RIASEC S强 + 使命感强 | SV |
| L1选"准时下班"或"平稳" | LS |

---

## 文件结构

```
~/.hermes/skills/gaokao-mentor/
├── SKILL.md
├── references/
│   └── engine.py        # 核心引擎（已含反馈系统 V2.0）
└── scripts/
    └── test_engine.py    # 单元测试（已含反馈测试）
```

## 技术要求

- Python 3.12+
- json、dataclasses、re（stdlib）
- 档案目录：`~/.hermes/gaokao_profiles/`（自动创建）

## 运行状态检查

```bash
# 本地引擎测试
python3 ~/.hermes/skills/gaokao-mentor/scripts/test_engine.py
```

## 进度

- [x] V1.1 引擎开发完成，测试通过
- [x] V1.1 微信端到端测试
- [x] V2.0 反馈收集系统（自动+手动，4层结构）
- [x] 完整文档（README + PROMOTION + FEEDBACK + MANUAL + CONTRIBUTING）
- [ ] GitHub Stars 50+
- [ ] 高考出分冲刺（200 Stars）
- [ ] V2.0 院校匹配层（分数→院校）
