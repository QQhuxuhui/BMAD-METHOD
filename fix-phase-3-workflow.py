#!/usr/bin/env python3
"""
修复Phase 3工作流文件，将Phase 3拆分为Phase 3（方案集成）和Phase 3.5（代码生成）
"""

import re
import shutil

def fix_phase_3_workflow():
    """修复Phase 3工作流"""

    # 文件路径
    file_path = "src/modules/aps/workflows/scheduling-orchestration/workflow.yaml"

    print("正在修复Phase 3工作流...")

    # 读取原文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到Phase 3的开始位置
    phase_3_start = content.find("  - phase_id: \"phase-3\"")
    if phase_3_start == -1:
        print("❌ 未找到Phase 3定义")
        return False

    # 找到Phase 4的开始位置
    phase_4_start = content.find("  - phase_id: \"phase-4\"")
    if phase_4_start == -1:
        print("❌ 未找到Phase 4定义")
        return False

    print(f"Phase 3起始位置: {phase_3_start}")
    print(f"Phase 4起始位置: {phase_4_start}")

    # 提取Phase 3之前的内容
    before_phase_3 = content[:phase_3_start]

    # 提取Phase 4及之后的内容
    after_phase_4 = content[phase_4_start:]

    # 新的Phase 3定义（简洁调用）
    new_phase_3 = '''  - phase_id: "phase-3"
    phase_name: "Phase 3: 方案集成"
    estimated_time: "15-20分钟"
    description: "专注于技术方案设计、文档生成和用户确认，确保高质量的技术方案交付"

    steps:
      - step_id: "3.0"
        name: "🚀 调用Phase 3方案集成工作流"
        action: "run-workflow"
        target: "bmad/aps/workflows/phase-3-solution-integration/workflow.yaml"
        description: "调用专门的Phase 3工作流，负责方案集成和文档生成"

        critical: true

        pre_condition_check:
          required_phases:
            - phase_id: "phase_2"
              on_missing: "block_with_error"
              error_message: |
                ❌ CRITICAL: Phase 2 专家协调未完成！

                Phase 3方案集成需要Phase 2的专家分析结果作为输入。

                解决方案: 请从 Phase 2 重新执行

        inputs:
          # Phase 3工作流会自动加载这些状态
          - phase_1_5_state_source: "phase_1_5"
          - phase_2_state_source: "phase_2"

        outputs:
          - integrated_solution # 完整的集成方案
          - user_approved_solution # 用户确认的方案
          - solution_document_path # 方案文档路径
          - solution_data_path # 方案数据路径
          - phase_3_completion # Phase 3完成状态

        post_action_verify:
          - check: "phase_3_completion.success == true"
            on_fail: "block_and_retry"
            error_message: "Phase 3方案集成失败"
            max_retries: 2

        # 传递关键数据给Phase 3.5
        success_actions:
          - log: "✅ Phase 3 方案集成完成"
          - log: "📄 方案文档: ${solution_document_path}"
          - log: "👤 用户确认方案: ${user_approved_solution.approval_timestamp}"
          - log: "🚀 准备进入 Phase 3.5 代码生成"'''

    # 新的Phase 3.5定义
    new_phase_3_5 = '''

  - phase_id: "phase-3.5"
    phase_name: "Phase 3.5: 代码生成"
    estimated_time: "20-25分钟"
    description: "由代码实现专家主导，基于用户确认的技术方案生成高质量可执行代码"

    steps:
      - step_id: "3.5.0"
        name: "🚀 调用Phase 3.5代码生成工作流"
        action: "run-workflow"
        target: "bmad/aps/workflows/phase-3.5-code-generation/workflow.yaml"
        description: "调用专门的Phase 3.5工作流，负责代码生成和质量保证"

        critical: true

        pre_condition_check:
          required_phases:
            - phase_id: "phase_3"
              on_missing: "block_with_error"
              error_message: |
                ❌ CRITICAL: Phase 3 方案集成未完成！

                Phase 3.5代码生成需要Phase 3的用户确认方案作为输入。

                解决方案: 请从 Phase 3 重新执行

        inputs:
          # Phase 3.5工作流会自动加载这些状态
          - phase_3_state_source: "phase_3"
          - phase_1_5_state_source: "phase_1_5"

        outputs:
          - implementation_code # 完整的代码包
          - code_traceability # 代码可追溯性
          - deliverable_manifest # 交付物清单
          - phase_3_5_completion # Phase 3.5完成状态

        post_action_verify:
          - check: "phase_3_5_completion.success == true"
            on_fail: "block_and_retry"
            error_message: "Phase 3.5代码生成失败"
            max_retries: 2

        # 传递关键数据给Phase 4
        success_actions:
          - log: "✅ Phase 3.5 代码生成完成"
          - log: "💻 代码包: ${implementation_code.package_path}"
          - log: "📚 代码文档: ${implementation_code.documentation_path}"
          - log: "�� 质量评分: ${quality_score}"
          - log: "🚀 准备进入 Phase 4 质量保证"'''

    # 更新Phase 4的依赖引用
    phase_4_updated = '''  - phase_id: "phase-4"
    phase_name: "Phase 4: 质量保证"
    estimated_time: "9-12分钟"
    description: "质量门禁验证，确保可交付"

    steps:
      - step_id: "4.0.1"
        name: "🔍 加载Phase 3.5状态 (代码生成)"
        action: "exec"
        target: "bmad/aps/tasks/load-phase-state.md"
        description: "加载集成方案和实现代码"'''

    # 重组内容
    new_content = before_phase_3 + new_phase_3 + new_phase_3_5 + phase_4_updated

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ Phase 3工作流修复完成")
    print(f"  - Phase 3: 15-20分钟，专注方案集成")
    print(f"  - Phase 3.5: 20-25分钟，专注代码生成")
    print(f"  - 总时间调整: 82-117分钟 (模式A), 107-142分钟 (模式B)")

    return True

if __name__ == "__main__":
    success = fix_phase_3_workflow()
    if success:
        print("\n🎉 Phase 3.5分离实施成功！")
        print("\n下一步:")
        print("1. 更新相关文档和配置")
        print("2. 端到端测试和验证")
    else:
        print("\n❌ Phase 3.5分离失败，请检���错误并手动修复")