# -*- coding: utf-8 -*-
"""
gaokao-mentor engine — 核心对话引擎 V1.1
状态机 + Mentor角色 + Ikigai破冰 + 现实约束探测 + RIASEC测评 + 带备注推荐
"""

import json
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

# ═══════════════════════════════════════════════════════════
# 0. 全局配置
# ═══════════════════════════════════════════════════════════

PROFILE_DIR = os.path.expanduser("~/.hermes/gaokao_profiles")
os.makedirs(PROFILE_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════
# 1. 状态机定义
# ═══════════════════════════════════════════════════════════

class State(Enum):
    START = "START"
    IKIGAI_Q1 = "IKIGAI_Q1"
    IKIGAI_Q2 = "IKIGAI_Q2"
    IKIGAI_Q3 = "IKIGAI_Q3"
    IKIGAI_Q4 = "IKIGAI_Q4"
    IKIGAI_SUMMARY = "IKIGAI_SUMMARY"
    CONSTRAINT_CHECK = "CONSTRAINT_CHECK"      # V1.1新增
    RIASEC_INTRO = "RIASEC_INTRO"
    RIASEC_QUESTIONS = "RIASEC_QUESTIONS"
    CLARITY_CHECK = "CLARITY_CHECK"
    OUTPUT = "OUTPUT"
    END = "END"


# ═══════════════════════════════════════════════════════════
# 2. Mentor 角色定义
# ═══════════════════════════════════════════════════════════

@dataclass
class MentorProfile:
    name: str
    title: str
    greeting: str
    style: str

    def system_prompt(self) -> str:
        return "你是「%s」，%s。风格：%s。核心原则：%s" % (
            self.name, self.title, self.style, self.greeting)


MENTORS = {
    "清言": MentorProfile(
        name="清言",
        title="自我认知教练",
        greeting="不直接给答案，通过提问帮助你思考。你说的每一句话，我都会认真听，然后继续追问，直到你自己看清方向。",
        style="coaching"
    ),
    "远见": MentorProfile(
        name="远见",
        title="可能性展示者",
        greeting="我擅长展示各种可能性，帮助你看到之前没想过的方向。不评判对错，只展示丰富。",
        style="possibility"
    ),
}


# ═══════════════════════════════════════════════════════════
# 3. Ikigai 提问模板
# ═══════════════════════════════════════════════════════════

IKIGAI_QUESTIONS = [
    {
        "id": "Q1",
        "state": State.IKIGAI_Q1,
        "question": "什么时候你感觉时间过得很快、做得很投入，完全忘记其他事情？",
        "hint": "可以是一件很小的事——比如搭乐高、画画、写小说、和朋友聊天、玩游戏……什么都行",
        "key": "love"
    },
    {
        "id": "Q2",
        "state": State.IKIGAI_Q2,
        "question": "你觉得什么东西是你特别擅长的，即使没怎么学也比别人做得好？",
        "hint": "可以是学业、运动、手艺、跟人打交道……你有这种感觉吗？",
        "key": "good_at"
    },
    {
        "id": "Q3",
        "state": State.IKIGAI_Q3,
        "question": "你觉得这个世界最需要什么？哪怕是很小的事情也行。",
        "hint": "可以是技术进步、社会公平、环境保护、人的幸福……你觉得什么重要？",
        "key": "world_needs"
    },
    {
        "id": "Q4",
        "state": State.IKIGAI_Q4,
        "question": "想象5年后——你过上了一种理想的生活。描述一下普通的一天。",
        "hint": "早上醒来，你在哪里？在做什么？跟谁在一起？不用想太久，随直觉写就行",
        "key": "vision"
    },
]


# ═══════════════════════════════════════════════════════════
# 4. 现实约束快速探测（3问，V1.1新增）
# ═══════════════════════════════════════════════════════════

CONSTRAINT_QUESTIONS = [
    {
        "id": "F1",
        "question": "家里人对你学什么专业，有没有明确的期待或反对？",
        "note": "了解家庭干预程度。无期待→自由度最大；明确反对→需处理冲突；完全不管→自主权最大"
    },
    {
        "id": "F2",
        "question": "从经济角度看，你选择专业/学校时，有没有哪些是你家承担不起的？",
        "note": "识别经济约束：学费、生活费、出国、留学等"
    },
    {
        "id": "F3",
        "question": "你是家里的独生子女吗？（了解家庭依赖程度）",
        "note": "辅助判断家庭养老等隐性约束"
    },
]


# ═══════════════════════════════════════════════════════════
# 5. 生活型权重快速判断（3问，V1.1新增）
# ═══════════════════════════════════════════════════════════

LIFE_RHYTHM_QUESTIONS = [
    {
        "id": "L1",
        "question": "如果一个工作工资很高，但你没有自己的时间；另一个工作工资一般，但每天准时下班、周末不加班。你选哪个？",
        "key": "work_life_choice"
    },
    {
        "id": "L2",
        "question": "你理想中的生活，是拼命工作几年然后自由，还是一直保持平稳的工作节奏？",
        "key": "work_pace"
    },
    {
        "id": "L3",
        "question": "你觉得工作是什么？是一辈子的事，还是一个阶段的事？",
        "key": "work_meaning"
    },
]


# ═══════════════════════════════════════════════════════════
# 6. RIASEC 题目（24题，V1.1版本）
# ═══════════════════════════════════════════════════════════

RIASEC_QUESTIONS = [
    {"id": "R1", "dimension": "R", "text": "拆解电脑硬件，自己研究内部结构"},
    {"id": "R2", "dimension": "R", "text": "用代码写一个能自动整理文件的程序"},
    {"id": "R3", "dimension": "R", "text": "组装一件家具，说明书很复杂"},
    {"id": "R4", "dimension": "R", "text": "维修一台坏了的电子设备"},
    {"id": "R5", "dimension": "R", "text": "按照步骤指南组装一件电子产品"},
    {"id": "R6", "dimension": "R", "text": "编程实现一个算法解决问题"},
    {"id": "I1", "dimension": "I", "text": "分析数据，找出其中的规律"},
    {"id": "I2", "dimension": "I", "text": "自己查资料，把一个复杂的技术原理研究清楚"},
    {"id": "I3", "dimension": "I", "text": "研究一个新技术的原理和实现方式"},
    {"id": "I4", "dimension": "I", "text": "参加一场辩论赛，为自己的观点辩护"},
    {"id": "I5", "dimension": "I", "text": "做实验验证一个科学假设"},
    {"id": "I6", "dimension": "I", "text": "研究怎么让一个产品更好用、更受用户欢迎"},
    {"id": "A1", "dimension": "A", "text": "设计一个logo或海报"},
    {"id": "A2", "dimension": "A", "text": "写一首诗或一首歌表达某种感受"},
    {"id": "A3", "dimension": "A", "text": "写一本小说"},
    {"id": "A4", "dimension": "A", "text": "拍摄一组照片讲述一个故事"},
    {"id": "S1", "dimension": "S", "text": "帮朋友解决一个感情问题"},
    {"id": "S2", "dimension": "S", "text": "给一个朋友详细讲解技术问题，带他一起理解"},
    {"id": "S3", "dimension": "S", "text": "跟一群人讨论某个社会问题的解决方案"},
    {"id": "S4", "dimension": "S", "text": "跟一个迷茫的人聊天，帮他理清思路"},
    {"id": "E1", "dimension": "E", "text": "组织一群人一起完成一个项目，你是主导者"},
    {"id": "E2", "dimension": "E", "text": "在讨论中提出一个完全没人想到的新方向"},
    {"id": "E3", "dimension": "E", "text": "成立一个新团队，制定战略让公司盈利"},
    {"id": "C1", "dimension": "C", "text": "按照模板整理一份数据报表"},
    {"id": "C2", "dimension": "C", "text": "凭空想象，设计一个完全新的产品"},
]


# ═══════════════════════════════════════════════════════════
# 7. 方向性输出映射
# ═══════════════════════════════════════════════════════════

RIASEC_DIMENSIONS = ["R", "I", "A", "S", "E", "C"]
RIASEC_NAMES = {
    "R": "实际型", "I": "研究型", "A": "艺术型",
    "S": "社会型", "E": "企业型", "C": "常规型"
}

RIASEC_TO_MAJORS = {
    ("R", "I"): ["机械工程", "电子信息", "计算机科学与技术", "自动化", "材料科学"],
    ("R", "S"): ["体育教育", "护理学", "康复治疗", "园林", "畜牧兽医"],
    ("R", "E"): ["工程管理", "工商管理", "市场营销", "物流工程"],
    ("R", "C"): ["会计学", "财务管理", "工程造价", "土木工程"],
    ("I", "A"): ["心理学", "建筑学", "统计学", "人工智能"],
    ("I", "S"): ["医学", "药学", "生物科学", "环境科学"],
    ("I", "E"): ["金融学", "经济学", "管理科学与工程"],
    ("I", "C"): ["计算机应用", "软件工程", "信息管理"],
    ("A", "S"): ["教育学", "学前教育", "社会工作", "新闻传播"],
    ("A", "E"): ["广告学", "广播电视编导", "艺术设计", "会展经济"],
    ("A", "C"): ["服装设计", "视觉传达", "产品设计", "数字媒体"],
    ("S", "E"): ["人力资源管理", "公共事业管理", "行政管理", "劳动关系学"],
    ("S", "C"): ["法学", "社会学", "政治学", "应用心理学"],
    ("E", "C"): ["工商管理", "市场营销", "电子商务", "国际贸易"],
    "R": ["机械类", "电子信息类", "计算机类", "建筑类", "交通运输类"],
    "I": ["数学类", "物理学类", "化学类", "生物类", "计算机类"],
    "A": ["设计类", "建筑类", "新闻传播类", "音乐与舞蹈类", "美术学类"],
    "S": ["教育类", "法学类", "公共管理类", "护理学类", "社会工作类"],
    "E": ["工商管理类", "市场营销类", "电子商务类", "金融学类"],
    "C": ["会计学", "财务管理", "审计学", "法学类", "行政管理"],
}

CAREER_DIRECTIONS = {
    "R": "[R] 实际型 — 喜欢动手做事，用双手解决问题。适合工程类、技术类、动手操作类的工作。",
    "I": "[I] 研究型 — 喜欢追根究底，对未知充满好奇。适合科研、技术研发、学术类的工作。",
    "A": "[A] 艺术型 — 重视个性和美感，讨厌被束缚。适合设计、艺术创作、传媒类的工作。",
    "S": "[S] 社会型 — 善于与人相处，关注他人感受。适合教育、医疗、社会工作、公共服务类的工作。",
    "E": "[E] 企业型 — 喜欢影响他人，追求成就和权力。适合管理、销售、创业、政治类的工作。",
    "C": "[C] 常规型 — 喜欢有秩序的环境，做事细致认真。适合财务、行政、法务、统计类的工作。",
}


# ═══════════════════════════════════════════════════════════
# 8. 职业锚推断逻辑（Mentor内部用，V1.1新增）
# ═══════════════════════════════════════════════════════════

CAREER_ANCHORS_CN = {
    "TF": "技术/职能型 — 追求专业领域的深度，不愿做管理",
    "GM": "管理型 — 追求全面管理责任，承担责任重大",
    "AU": "自主/独立型 — 希望用自己的方式工作，不受组织束缚",
    "SE": "安全/稳定型 — 追求长期稳定和安全，不喜欢风险",
    "EC": "创业型 — 希望创造完全属于自己的事业，愿意冒险",
    "SV": "服务/奉献型 — 通过工作帮助他人/社会，追求意义",
    "CH": "挑战型 — 追求难题和新奇，认为一切皆可征服",
    "LS": "生活型 — 工作为生活服务，不愿让工作侵占生活",
}

ANCHOR_INFER_RULES = [
    # (条件描述, 推断锚)
    ("RIASEC I强 + 家庭自由度大", ["AU", "CH", "TF"]),
    ("RIASEC E强 + 家庭自由度大", ["EC", "GM"]),
    ("RIASEC S强 + 使命感强", ["SV"]),
    ("生活型L1选准时下班 + L2选平稳", ["LS", "SE"]),
    ("RIASEC I强 + E强 + 家庭自由度大", ["EC", "AU", "CH"]),
]


# ═══════════════════════════════════════════════════════════
# 9. 考生会话状态
# ═══════════════════════════════════════════════════════════

@dataclass
class CandidateProfile:
    student_id: str = ""
    name: str = ""
    # Ikigai 四问
    ikigai_love: str = ""
    ikigai_good_at: str = ""
    ikigai_world_needs: str = ""
    ikigai_vision: str = ""
    # 现实约束（V1.1新增）
    constraint_family: str = ""    # F1
    constraint_economic: str = ""  # F2
    constraint_only_child: str = "" # F3
    constraint_freedom_score: int = 0  # 1-10
    # 生活型权重（V1.1新增）
    life_work_choice: str = ""     # L1
    life_work_pace: str = ""        # L2
    life_work_meaning: str = ""    # L3
    # 推断锚
    inferred_anchors: list = field(default_factory=list)
    # RIASEC
    riasec_answers: dict = field(default_factory=dict)
    riasec_scores: dict = field(default_factory=dict)
    top_dimensions: list = field(default_factory=list)
    # 状态
    current_state: State = State.START
    current_mentor: str = "清言"
    ikigai_question_index: int = 0
    riasec_question_index: int = 0
    constraint_question_index: int = 0
    clarity_level: str = ""
    recommended_majors: list = field(default_factory=list)
    conversation_history: list = field(default_factory=list)

    def save(self) -> str:
        path = os.path.join(PROFILE_DIR, "%s.json" % self.student_id)
        data = asdict(self)
        data["current_state"] = self.current_state.value
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    @classmethod
    def load(cls, student_id: str) -> Optional["CandidateProfile"]:
        path = os.path.join(PROFILE_DIR, "%s.json" % student_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["current_state"] = State(data["current_state"])
        return cls(**data)


# ═══════════════════════════════════════════════════════════
# 10. Mentor 对话引擎
# ═══════════════════════════════════════════════════════════

class MentorEngine:
    def __init__(self, profile: CandidateProfile):
        self.profile = profile
        self.mentor = MENTORS.get(profile.current_mentor, MENTORS["清言"])

    def enter_state(self, state: State) -> str:
        self.profile.current_state = state
        handlers = {
            State.START: self._handle_start,
            State.IKIGAI_Q1: self._handle_ikigai_q,
            State.IKIGAI_Q2: self._handle_ikigai_q,
            State.IKIGAI_Q3: self._handle_ikigai_q,
            State.IKIGAI_Q4: self._handle_ikigai_q,
            State.IKIGAI_SUMMARY: self._handle_ikigai_summary,
            State.CONSTRAINT_CHECK: self._handle_constraint_q,
            State.RIASEC_INTRO: self._handle_riasec_intro,
            State.RIASEC_QUESTIONS: self._handle_riasec_questions,
            State.CLARITY_CHECK: self._handle_clarity_check,
            State.OUTPUT: self._handle_output,
            State.END: self._handle_end,
        }
        return handlers[state]()

    # ─── 状态处理 ──────────────────────────────────────────

    def _handle_start(self) -> str:
        return (
            "\n%s | 自我认知教练\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "你好，我叫清言，是你的自我认知教练。\n\n"
            "今天我们用大约20分钟，一起做一个完整的自我探索——\n"
            "我会问一些问题，帮你看清自己真正想要什么方向。\n\n"
            "整个过程没有\"正确答案\"，我也不会替你做决定。\n"
            "准备好了吗？我们从第一个问题开始：\n\n"
            "%s\n\n%s"
        ) % (
            self.mentor.name,
            self.mentor.greeting,
            IKIGAI_QUESTIONS[0]["question"],
        )

    def _handle_ikigai_q(self) -> str:
        q = IKIGAI_QUESTIONS[self.profile.ikigai_question_index]
        return q["question"]

    def _handle_ikigai_summary(self) -> str:
        return (
            "\n%s | 自我认知小结\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "【你热爱的事】\n%s\n\n"
            "【你擅长的事】\n%s\n\n"
            "【你觉得世界需要的】\n%s\n\n"
            "【你理想的生活】\n%s\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "现在，我们来快速了解一下你的现实情况和偏好。\n"
            "回复【继续】进入下一组问题。"
        ) % (
            self.mentor.name,
            self.profile.ikigai_love or "（未填写）",
            self.profile.ikigai_good_at or "（未填写）",
            self.profile.ikigai_world_needs or "（未填写）",
            self.profile.ikigai_vision or "（未填写）",
        )

    def _handle_constraint_q(self) -> str:
        idx = self.profile.constraint_question_index
        total = len(CONSTRAINT_QUESTIONS) + len(LIFE_RHYTHM_QUESTIONS)

        if idx < len(CONSTRAINT_QUESTIONS):
            q = CONSTRAINT_QUESTIONS[idx]
            return (
                "\n【现实情况 %d/%d】\n%s\n\n"
                "（直接回答即可，不用考虑太多）"
            ) % (idx + 1, total, q["question"])
        else:
            li = idx - len(CONSTRAINT_QUESTIONS)
            q = LIFE_RHYTHM_QUESTIONS[li]
            return (
                "\n【生活偏好 %d/%d】\n%s\n\n"
                "（凭直觉回答，没有对错）"
            ) % (li + 1, len(LIFE_RHYTHM_QUESTIONS), q["question"])

    def _handle_riasec_intro(self) -> str:
        return (
            "\n%s | RIASEC 职业兴趣测评\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "接下来是一个短测评，帮助你量化自己的兴趣类型。\n\n"
            "每道题给你两个场景，选你更自然会去做的那个。\n"
            "不是\"哪个更好\"，是\"哪个更接近你本能会做的事\"。\n\n"
            "准备好了吗？我们现在开始第1题：\n"
        )

    def _handle_riasec_questions(self) -> str:
        idx = self.profile.riasec_question_index
        q = RIASEC_QUESTIONS[idx]
        return (
            "\n【%d/25】\n\n%s\n\nA: %s\nB: [另一选项]\n\n请回复 A 或 B："
        ) % (idx + 1, q["text"], q["text"][:50])

    def _handle_clarity_check(self) -> str:
        self._calc_riasec_scores()
        self._infer_career_anchors()
        radar = self._render_radar()
        clarity = self._assess_clarity()
        self.profile.clarity_level = clarity["level"]

        lines = [
            "\n%s | RIASEC 测评结果\n" % self.mentor.name,
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            radar,
            "",
            "你的主导维度：【%s】" % self._top_two_cn(),
            "",
            clarity["advice"],
        ]
        return "\n".join(lines)

    def _handle_output(self) -> str:
        self._calc_recommendations()
        self._infer_career_anchors()
        majors = self.profile.recommended_majors
        top_dims = self.profile.top_dimensions

        # 构建约束/节奏备注
        notes = []
        if self.profile.inferred_anchors:
            anchor_str = "、".join(self.profile.inferred_anchors)
            notes.append("职业锚倾向：%s" % anchor_str)
        if self.profile.constraint_family:
            notes.append("家庭约束：%s" % self.profile.constraint_family)
        if self.profile.life_work_choice:
            notes.append("生活偏好：%s" % self.profile.life_work_choice)

        lines = [
            "\n%s | 方向建议\n" % self.mentor.name,
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "基于你的自我认知，你的职业兴趣画像是：",
            "",
        ]
        for dim in top_dims:
            lines.append(CAREER_DIRECTIONS.get(dim, ""))

        lines.extend([
            "",
            "推荐关注的专业群：",
        ])
        for m in majors:
            lines.append("  · %s" % m)

        if notes:
            lines.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "  补充背景（不强制约束，仅供参考）",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ])
            for n in notes:
                lines.append("  · %s" % n)

        lines.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  下一步你可以",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  ① 继续深入聊某个方向",
            "  ② 换个方向继续探索",
            "  ③ 保存结果，改天继续",
            "",
            "你想怎么做？",
        ])
        return "\n".join(lines)

    def _handle_end(self) -> str:
        path = self.profile.save()
        return (
            "\n已保存你的探索记录。\n"
            "有需要随时回来继续探索，祝你找到自己的方向！"
        )

    # ─── 用户输入处理 ─────────────────────────────────────

    def process_input(self, user_input: str) -> str:
        state = self.profile.current_state
        text = user_input.strip()
        self.profile.conversation_history.append({"state": state.value, "user": text})

        if state == State.START:
            return self._do_transition(State.IKIGAI_Q1)

        elif state in [State.IKIGAI_Q1, State.IKIGAI_Q2, State.IKIGAI_Q3, State.IKIGAI_Q4]:
            return self._handle_ikigai_answer(text)

        elif state == State.IKIGAI_SUMMARY:
            if "继续" in text:
                self.profile.constraint_question_index = 0
                return self._do_transition(State.CONSTRAINT_CHECK)
            return self._do_transition(State.CONSTRAINT_CHECK)

        elif state == State.CONSTRAINT_CHECK:
            return self._handle_constraint_answer(text)

        elif state == State.RIASEC_INTRO:
            if "继续" in text or "开始" in text:
                self.profile.riasec_question_index = 0
                return self._do_transition(State.RIASEC_QUESTIONS)
            return self._do_transition(State.RIASEC_QUESTIONS)

        elif state == State.RIASEC_QUESTIONS:
            return self._handle_riasec_answer(text)

        elif state == State.CLARITY_CHECK:
            return self._do_transition(State.OUTPUT)

        elif state == State.OUTPUT:
            return self._handle_output_choice(text)

        return "（未知状态）"

    def _handle_ikigai_answer(self, text: str) -> str:
        if not text or len(text) < 2:
            return "我需要更多一点信息。能再说说吗？"

        q_idx = self.profile.ikigai_question_index
        q = IKIGAI_QUESTIONS[q_idx]
        key = q["key"]

        # 存答案
        if key == "love": self.profile.ikigai_love = text
        elif key == "good_at": self.profile.ikigai_good_at = text
        elif key == "world_needs": self.profile.ikigai_world_needs = text
        elif key == "vision": self.profile.ikigai_vision = text

        next_idx = q_idx + 1
        self.profile.ikigai_question_index = next_idx

        if next_idx < 4:
            return self._do_transition(IKIGAI_QUESTIONS[next_idx]["state"])
        else:
            return self._do_transition(State.IKIGAI_SUMMARY)

    def _handle_constraint_answer(self, text: str) -> str:
        idx = self.profile.constraint_question_index
        total = len(CONSTRAINT_QUESTIONS) + len(LIFE_RHYTHM_QUESTIONS)

        if idx < len(CONSTRAINT_QUESTIONS):
            q = CONSTRAINT_QUESTIONS[idx]
            if idx == 0: self.profile.constraint_family = text
            elif idx == 1: self.profile.constraint_economic = text
            elif idx == 2: self.profile.constraint_only_child = text
        else:
            li = idx - len(CONSTRAINT_QUESTIONS)
            q = LIFE_RHYTHM_QUESTIONS[li]
            if li == 0: self.profile.life_work_choice = text
            elif li == 1: self.profile.life_work_pace = text
            elif li == 2: self.profile.life_work_meaning = text

        next_idx = idx + 1
        self.profile.constraint_question_index = next_idx

        if next_idx < total:
            return self._do_transition(State.CONSTRAINT_CHECK)
        else:
            return self._do_transition(State.RIASEC_INTRO)

    def _handle_riasec_answer(self, text: str) -> str:
        # 简化：只处理 A/B 选择
        choices = ["A", "B", "a", "b"]
        if text.strip() not in choices:
            return "\n请回复 A 或 B："

        q_id = RIASEC_QUESTIONS[self.profile.riasec_question_index]["id"]
        # A=5分，B=1分（简化处理）
        score = 5 if text.upper() == "A" else 2
        self.profile.riasec_answers[q_id] = score

        next_idx = self.profile.riasec_question_index + 1
        self.profile.riasec_question_index = next_idx

        if next_idx < len(RIASEC_QUESTIONS):
            return self._do_transition(State.RIASEC_QUESTIONS)
        else:
            return self._do_transition(State.CLARITY_CHECK)

    def _handle_output_choice(self, text: str) -> str:
        if "继续" in text or "深入" in text or "①" in text:
            return "太好了，告诉我想深入聊哪个方向？"
        elif "换" in text or "其他" in text or "②" in text:
            self.profile.current_state = State.RIASEC_INTRO
            self.profile.riasec_question_index = 0
            return "好的，我们换一个角度重新探索。"
        else:
            return self._do_transition(State.END)

    def _do_transition(self, next_state: State) -> str:
        self.profile.current_state = next_state
        return self.enter_state(next_state)

    # ─── 辅助计算方法 ─────────────────────────────────────

    def _calc_riasec_scores(self):
        scores = {d: [] for d in RIASEC_DIMENSIONS}
        for q in RIASEC_QUESTIONS:
            dim = q["dimension"]
            qid = q["id"]
            if qid in self.profile.riasec_answers:
                scores[dim].append(self.profile.riasec_answers[qid])

        final = {}
        for dim, vals in scores.items():
            if vals:
                final[dim] = round(sum(vals) / len(vals) / 5.0 * 100.0, 1)
            else:
                final[dim] = 0.0

        self.profile.riasec_scores = final
        sorted_dims = sorted(final.items(), key=lambda x: x[1], reverse=True)
        self.profile.top_dimensions = [d[0] for d in sorted_dims[:2]]

    def _infer_career_anchors(self):
        """Mentor内部推断职业锚倾向，不让学生做完整测评"""
        anchors = []
        top = self.profile.top_dimensions
        riasec_scores = self.profile.riasec_scores
        life_choice = self.profile.life_work_choice or ""

        # 推断逻辑
        if top:
            top0, top1 = top[0], top[1] if len(top) > 1 else top[0]
            if top0 == "I" or (top0 == "R" and top1 == "I"):
                anchors.extend(["AU", "CH", "TF"])
            elif top0 == "E":
                anchors.extend(["EC", "GM"])
            elif top0 == "S":
                anchors.extend(["SV", "SE"])
            elif top0 == "A":
                anchors.extend(["EC", "AU"])

        # 生活型权重
        if any(k in life_choice for k in ["准时下班", "周末不加班", "平稳", "一般"]):
            anchors.append("LS")

        # 去重，保留前3
        seen = set()
        unique = []
        for a in anchors:
            if a not in seen:
                seen.add(a)
                unique.append(a)
        self.profile.inferred_anchors = unique[:3]

    def _render_radar(self) -> str:
        scores = self.profile.riasec_scores
        if not scores:
            return ""
        ordered = [scores.get(d, 0) for d in RIASEC_DIMENSIONS]
        names = [RIASEC_NAMES[d] for d in RIASEC_DIMENSIONS]
        lines = ["        RIASEC 职业兴趣雷达图", ""]
        for level in [5, 4, 3, 2, 1]:
            threshold = level * 20
            row = "  %3d%% |" % threshold
            for val in ordered:
                row += "  %s  " % ("●" if val >= threshold else "·")
            lines.append(row)
        lines.append("       " + "-" * 30)
        lines.append("         R     I     A     S     E     C")
        lines.append("")
        lines.append("  各维度得分：")
        for d in RIASEC_DIMENSIONS:
            bar = "█" * int(scores.get(d, 0) / 5)
            lines.append("  %s %s [%s] %5.1f%%" % (d, RIASEC_NAMES[d].ljust(4), bar.ljust(20), scores.get(d, 0)))
        return "\n".join(lines)

    def _top_two_cn(self) -> str:
        dims = self.profile.top_dimensions
        if len(dims) >= 2:
            return "%s(%s) + %s(%s)" % (dims[0], RIASEC_NAMES[dims[0]], dims[1], RIASEC_NAMES[dims[1]])
        elif len(dims) == 1:
            return "%s(%s)" % (dims[0], RIASEC_NAMES[dims[0]])
        return "（尚未评测）"

    def _assess_clarity(self) -> dict:
        scores = self.profile.riasec_scores
        spread = (max(scores.values()) - min(scores.values())) if scores else 0
        ikigai_lengths = [
            len(self.profile.ikigai_love),
            len(self.profile.ikigai_good_at),
            len(self.profile.ikigai_world_needs),
            len(self.profile.ikigai_vision),
        ]
        avg_ikigai = sum(ikigai_lengths) / len(ikigai_lengths) if ikigai_lengths else 0

        if spread >= 40 and avg_ikigai >= 30:
            level = "清晰"
            detail = (
                "你的职业兴趣特征非常明显，且在自我探索中能够清晰表达自己。\n"
                "这意味着你可以比较自信地进入下一阶段的院校/专业匹配。"
            )
            next_step = "回复【继续】进入方向建议，或直接告诉我你最想深入了解哪个方向。"
        elif spread >= 20 or avg_ikigai >= 15:
            level = "初步清晰"
            detail = (
                "你有一定的自我认知，但某些维度还不够明确。\n"
                "（维度跨度 %.0f%%，自我探索平均回答长度 %.0f字）\n"
                "这种情况很正常，很多人到这个阶段都会有几个'都可以'的方向。"
            ) % (spread, avg_ikigai)
            next_step = "回复【继续】，我们一起深入看看你的方向。"
        else:
            level = "模糊"
            detail = (
                "目前你的兴趣维度分布比较均衡。\n"
                "这完全正常——高考前的学生很少有人能完全确定自己的方向。"
            )
            next_step = "回复【继续】，我们可以从更多角度来了解你。"

        advice_map = {
            "清晰": "你的方向感已经比较强了，接下来重点是验证和细化。",
            "初步清晰": "你有了一些初步方向，但还需要一些探索来确认。",
            "模糊": "现在不需要硬逼自己确定方向，先广泛了解再说。"
        }
        return {"level": level, "detail": detail, "next_step": next_step, "advice": advice_map[level]}

    def _calc_recommendations(self):
        top = self.profile.top_dimensions
        majors = []
        if len(top) >= 2:
            key = tuple(top[:2])
            if key in RIASEC_TO_MAJORS:
                majors.extend(RIASEC_TO_MAJORS[key])
        for d in top:
            if d in RIASEC_TO_MAJORS and isinstance(RIASEC_TO_MAJORS[d], list):
                for m in RIASEC_TO_MAJORS[d]:
                    if m not in majors:
                        majors.append(m)
        if len(majors) < 5:
            general = ["计算机类", "数学类", "英语", "工商管理", "新闻传播类"]
            for g in general:
                if g not in majors:
                    majors.append(g)
        self.profile.recommended_majors = majors[:8]
