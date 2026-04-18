# 贡献指南

感谢你愿意为 gaokao-mentor 贡献！

---

## 如何贡献

### 方式一：反馈使用体验

- 在 [GitHub Discussions](https://github.com/ChaoYu-ChinaSZ/gaokao-mentor/discussions) 分享你的使用案例
- 在 [Issues](https://github.com/ChaoYu-ChinaSZ/gaokao-mentor/issues) 报告问题或提建议
- 完成对话后填写反馈（系统会自动邀请）

### 方式二：完善文档

- 发现文档错误或有表述不清的地方？直接提交 PR
- 翻译成其他语言？非常欢迎
- 补充更多使用场景和案例？

### 方式三：代码贡献

- 修复 BUG
- 优化推荐算法
- 增加新功能（如院校匹配层）

---

## 开发流程

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/ChaoYu-ChinaSZ/gaokao-mentor.git
cd gaokao-mentor

# 安装依赖（开发测试用）
pip install pytest -q

# 运行测试
python3 scripts/test_engine.py
```

### 提交规范

- commit message 格式：`[类型] 简短描述`
  - `[feat]` 新功能
  - `[fix]` 修复
  - `[docs]` 文档
  - `[test]` 测试
  - `[refactor]` 重构

### Pull Request 流程

1. Fork 仓库
2. 创建新分支：`git checkout -b feat/your-feature-name`
3. 提交改动
4. Push 到你的 Fork
5. 在 GitHub 发起 PR

---

## 项目结构

```
gaokao-mentor/
├── SKILL.md              # Skill元信息
├── references/
│   └── engine.py        # 核心引擎（主要修改这里）
├── scripts/
│   └── test_engine.py   # 测试脚本
└── docs/                # 文档
    ├── README.md
    ├── DEPLOY.md
    ├── USER_GUIDE.md
    ├── TECHNICAL.md
    ├── PROMOTION.md
    ├── FEEDBACK.md
    └── MANUAL.md
```

---

## 重大决策

涉及以下内容的改动，需要先开 Issue 讨论：
- 状态机流程变更
- 推荐算法重大调整
- 新增外部依赖
