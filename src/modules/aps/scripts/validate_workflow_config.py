#!/usr/bin/env python3
"""
APS Workflow Configuration Validator
验证 workflow 和 config 的完整性，确保状态文件管理机制正确配置

Version: 1.0
Author: BMAD APS Team
"""

import sys
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any


class WorkflowConfigValidator:
    """Workflow 和 Config 配置验证器"""

    def __init__(self, aps_root: str):
        self.aps_root = Path(aps_root)
        self.config_path = self.aps_root / "config.yaml"
        self.workflow_path = self.aps_root / "workflows" / "scheduling-orchestration" / "workflow.yaml"

        self.errors = []
        self.warnings = []
        self.config = None
        self.workflow = None

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        print("=" * 80)
        print("🔍 APS Workflow Configuration Validator")
        print("=" * 80)

        # 1. 加载配置文件
        if not self._load_configs():
            return False

        # 2. 验证 config.yaml 必需配置
        self._validate_config_yaml()

        # 3. 验证 workflow.yaml 状态管理机制
        self._validate_workflow_state_management()

        # 4. 验证目录结构
        self._validate_directory_structure()

        # 5. 验证状态文件保存和加载的一致性
        self._validate_state_save_load_consistency()

        # 6. 输出结果
        return self._print_results()

    def _load_configs(self) -> bool:
        """加载配置文件"""
        print("\n📂 加载配置文件...")

        # 加载 config.yaml
        if not self.config_path.exists():
            self.errors.append(f"❌ config.yaml 不存在: {self.config_path}")
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"  ✓ config.yaml 加载成功")
        except Exception as e:
            self.errors.append(f"❌ config.yaml 加载失败: {e}")
            return False

        # 加载 workflow.yaml
        if not self.workflow_path.exists():
            self.errors.append(f"❌ workflow.yaml 不存在: {self.workflow_path}")
            return False

        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                self.workflow = yaml.safe_load(f)
            print(f"  ✓ workflow.yaml 加载成功")
        except Exception as e:
            self.errors.append(f"❌ workflow.yaml 加载失败: {e}")
            return False

        return True

    def _validate_config_yaml(self):
        """验证 config.yaml 必需配置"""
        print("\n📋 验证 config.yaml 必需配置...")

        required_fields = [
            'output_folder',
            'models_folder',
            'docs_folder',
            'state_management'
        ]

        for field in required_fields:
            if field not in self.config:
                self.errors.append(f"❌ config.yaml 缺少必需字段: {field}")
            else:
                print(f"  ✓ {field}: {self.config[field]}")

        # 验证 state_management 子字段
        if 'state_management' in self.config:
            state_mgmt = self.config['state_management']

            required_state_fields = ['state_folder', 'state_format']
            for field in required_state_fields:
                if field not in state_mgmt:
                    self.errors.append(f"❌ state_management 缺少必需字段: {field}")
                else:
                    print(f"  ✓ state_management.{field}: {state_mgmt[field]}")

            # 验证 state_format 值
            if 'state_format' in state_mgmt:
                if state_mgmt['state_format'] not in ['yaml', 'json']:
                    self.errors.append(
                        f"❌ state_format 必须是 'yaml' 或 'json'，当前: {state_mgmt['state_format']}"
                    )

    def _validate_workflow_state_management(self):
        """验证 workflow.yaml 状态管理机制"""
        print("\n🔄 验证 workflow 状态管理机制...")

        phases = self.workflow.get('phases', [])

        # 检查每个 Phase
        for phase in phases:
            phase_id = phase.get('phase_id')
            print(f"\n  检查 {phase_id}:")

            steps = phase.get('steps', [])

            # 检查是否有状态保存步骤
            has_save_step = False
            has_load_step = False
            save_step = None
            load_step = None

            for step in steps:
                step_id = step.get('step_id')
                target = step.get('target', '')

                # 检查保存步骤
                if 'save-phase-state.md' in target:
                    has_save_step = True
                    save_step = step

                    # 验证保存步骤配置
                    if not step.get('mandatory_save'):
                        self.warnings.append(
                            f"⚠ {phase_id} 的状态保存步骤 {step_id} 未设置 mandatory_save: true"
                        )

                    if not step.get('critical'):
                        self.warnings.append(
                            f"⚠ {phase_id} 的状态保存步骤 {step_id} 未设置 critical: true"
                        )

                    # 验证 post_action_verify
                    if not step.get('post_action_verify'):
                        self.errors.append(
                            f"❌ {phase_id} 的状态保存步骤 {step_id} 缺少 post_action_verify"
                        )

                    print(f"    ✓ 发现保存步骤: {step_id}")

                # 检查加载步骤
                if 'load-phase-state.md' in target:
                    has_load_step = True
                    load_step = step

                    # 验证加载步骤配置
                    if not step.get('critical'):
                        self.warnings.append(
                            f"⚠ {phase_id} 的状态加载步骤 {step_id} 未设置 critical: true"
                        )

                    # 验证 pre_condition_check
                    if not step.get('pre_condition_check'):
                        self.errors.append(
                            f"❌ {phase_id} 的状态加载步骤 {step_id} 缺少 pre_condition_check"
                        )

                    print(f"    ✓ 发现加载步骤: {step_id}")

            # Phase 1-3 必须有保存步骤
            if phase_id in ['phase-1', 'phase-1.5', 'phase-2', 'phase-3']:
                if not has_save_step:
                    self.errors.append(
                        f"❌ {phase_id} 缺少状态保存步骤 (save-phase-state.md)"
                    )

            # Phase 1 之后的所有 Phase 都应该有加载步骤
            if phase_id in ['phase-1.5', 'phase-2', 'phase-3', 'phase-4']:
                if not has_load_step:
                    self.warnings.append(
                        f"⚠ {phase_id} 缺少状态加载步骤 (load-phase-state.md)"
                    )

    def _validate_directory_structure(self):
        """验证目录结构"""
        print("\n📁 验证目录结构...")

        # 从 config 读取目录配置
        state_folder = self.config.get('state_management', {}).get('state_folder', '')
        output_folder = self.config.get('output_folder', '')
        docs_folder = self.config.get('docs_folder', '')
        models_folder = self.config.get('models_folder', '')

        # 替换占位符
        project_root = self.aps_root.parent.parent

        folders_to_check = {
            'output_folder': output_folder.replace('{project-root}', str(project_root)),
            'state_folder': state_folder.replace('{project-root}', str(project_root)),
            'docs_folder': docs_folder.replace('{project-root}', str(project_root)),
            'models_folder': models_folder.replace('{project-root}', str(project_root))
        }

        for folder_name, folder_path in folders_to_check.items():
            folder = Path(folder_path)
            if not folder.exists():
                self.warnings.append(
                    f"⚠ {folder_name} 目录不存在: {folder_path} (将在首次运行时自动创建)"
                )
                print(f"  ⚠ {folder_name}: {folder_path} (不存在)")
            else:
                print(f"  ✓ {folder_name}: {folder_path}")

    def _validate_state_save_load_consistency(self):
        """验证状态保存和加载的一致性"""
        print("\n🔗 验证状态保存和加载的一致性...")

        phases = self.workflow.get('phases', [])

        # 记录每个 Phase 保存的状态
        saved_states = {}

        for phase in phases:
            phase_id = phase.get('phase_id')
            steps = phase.get('steps', [])

            for step in steps:
                target = step.get('target', '')

                # 记录保存的 Phase
                if 'save-phase-state.md' in target:
                    inputs = step.get('inputs', [])
                    for inp in inputs:
                        if isinstance(inp, dict) and 'phase_id' in inp:
                            saved_phase_id = inp['phase_id']
                            saved_states[saved_phase_id] = phase_id
                            break

                # 检查加载的 Phase 是否已保存
                if 'load-phase-state.md' in target:
                    inputs = step.get('inputs', [])
                    for inp in inputs:
                        if isinstance(inp, dict) and 'phase_id' in inp:
                            load_phase_id = inp['phase_id']

                            # 检查是否有对应的保存步骤
                            if load_phase_id not in saved_states:
                                self.errors.append(
                                    f"❌ {phase_id} 尝试加载 {load_phase_id} 的状态，但该 Phase 没有保存步骤"
                                )
                            else:
                                print(f"  ✓ {phase_id} 加载 {load_phase_id} 状态: 一致")
                            break

    def _print_results(self) -> bool:
        """输出验证结果"""
        print("\n" + "=" * 80)
        print("📊 验证结果汇总")
        print("=" * 80)

        # 输出错误
        if self.errors:
            print(f"\n❌ 发现 {len(self.errors)} 个错误:")
            for error in self.errors:
                print(f"  {error}")
        else:
            print("\n✅ 没有发现错误")

        # 输出警告
        if self.warnings:
            print(f"\n⚠  发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  {warning}")
        else:
            print("\n✅ 没有发现警告")

        # 总结
        print("\n" + "=" * 80)
        if not self.errors and not self.warnings:
            print("✅ 所有验证通过！配置完整且一致。")
            return True
        elif not self.errors:
            print("⚠  验证通过，但有警告项需要注意。")
            return True
        else:
            print("❌ 验证失败！请修复上述错误后重试。")
            return False


def main():
    """主函数"""
    # 确定 APS 根目录
    script_dir = Path(__file__).parent
    aps_root = script_dir.parent

    print(f"APS Root: {aps_root}")

    # 创建验证器并执行验证
    validator = WorkflowConfigValidator(str(aps_root))
    success = validator.validate_all()

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
