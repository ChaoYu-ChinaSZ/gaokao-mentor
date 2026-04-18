#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gaokao-mentor 测试脚本
"""
import sys
sys.path.insert(0, "/home/yuchao/.hermes/skills/productivity/gaokao-mentor/references")

from engine import MentorEngine, CandidateProfile, State, PROFILE_DIR
import os

# 测试1：模块导入
print("✓ 模块导入成功")

# 测试2：新建档案
test_id = "test_wx_user_001"
profile = CandidateProfile.load(test_id)
if profile is None:
    profile = CandidateProfile(student_id=test_id)
    print("✓ 新建档案成功：", test_id)

# 测试3：状态机初始化
engine = MentorEngine(profile)
print("✓ MentorEngine 初始化成功")

# 测试4：START状态
resp = engine.enter_state(State.START)
assert "清言" in resp, "开场应该有清言"
assert "Ikigai" in resp or "自我认知" in resp, "开场应该有Ikigai"
print("✓ START状态输出正常")

# 测试5：处理用户输入，进入IKIGAI_Q1
resp = engine.process_input("开始咨询")
assert State.IKIGAI_Q1 == profile.current_state, "应该进入IKIGAI_Q1"
print("✓ 状态转移正常")

# 测试6：回答Ikigai Q1
resp = engine.process_input("我喜欢玩游戏，尤其是需要动脑的策略游戏")
assert State.IKIGAI_Q2 == profile.current_state, "应该进入IKIGAI_Q2"
print("✓ Ikigai Q1回答处理正常")

# 测试7：快速答完四问
resp = engine.process_input("数学和物理")
resp = engine.process_input("AI和全智能")
resp = engine.process_input("海边，安安静静的")
assert State.IKIGAI_SUMMARY == profile.current_state, "应该进入IKIGAI_SUMMARY"
print("✓ Ikigai四问完成")

# 测试8：进入约束探测
resp = engine.process_input("继续")
assert State.CONSTRAINT_CHECK == profile.current_state, "应该进入CONSTRAINT_CHECK"
print("✓ 约束探测阶段正常")

# 测试9：答完约束3问后应该进入RIASEC_INTRO
resp = engine.process_input("家里没太大期望")
resp = engine.process_input("经济没问题")
resp = engine.process_input("是")
resp = engine.process_input("A")  # L1
resp = engine.process_input("A")  # L2
resp = engine.process_input("A")  # L3
assert State.RIASEC_INTRO == profile.current_state, "应该进入RIASEC_INTRO"
print("✓ 约束探测6问完成")

# 测试10：进入RIASEC
resp = engine.process_input("继续")
assert State.RIASEC_QUESTIONS == profile.current_state, "应该进入RIASEC_QUESTIONS"
print("✓ RIASEC开始正常")

# 测试11：完成全部25题
for i in range(25):
    resp = engine.process_input("A")
assert State.CLARITY_CHECK == profile.current_state, "应该进入CLARITY_CHECK"
print("✓ RIASEC 25题完成")

# 测试12：清晰度判断
resp = engine.process_input("继续")
assert State.OUTPUT == profile.current_state, "应该进入OUTPUT"
print("✓ 清晰度判断完成")

# 测试13：方向输出包含推荐
resp = engine.process_input("继续")
assert State.OUTPUT == profile.current_state, "应该留在OUTPUT"
assert len(profile.riasec_scores) > 0, "应该有RIASEC得分"
assert len(profile.recommended_majors) > 0, "应该有推荐专业"
print("✓ 推荐输出正常")
print("  推荐专业：", profile.recommended_majors[:3])
print("  职业锚推断：", profile.inferred_anchors)

# 测试14：保存档案
path = profile.save()
assert os.path.exists(path), "档案应该保存"
print("✓ 档案保存成功：", path)

# 测试15：加载档案
profile2 = CandidateProfile.load(test_id)
assert profile2.ikigai_love == "我喜欢玩游戏，尤其是需要动脑的策略游戏", "加载应该正确"
print("✓ 档案加载正确")

# 清理测试档案
os.remove(path)
print("\n✅ 所有测试通过！")

if __name__ == "__main__":
    print("\n运行方式：python3 test_engine.py")
