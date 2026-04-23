#!/usr/bin/env python3
"""
Generate starter context-collection questions for a task.

The skill's "开工前协议" requires Claude to collect sufficient context via
AskUserQuestion before starting analysis. This helper returns a curated
starter set of questions for common task types, so Claude doesn't have to
reinvent them each time.

Usage:
    python context_questions.py "我想在上海买房"
    python context_questions.py --task housing
    python context_questions.py --list
    python context_questions.py --task housing --format json

Output is either a human-readable prompt (default) or raw JSON suitable for
feeding into AskUserQuestion.

The templates are deliberately conservative — Claude should treat them as a
starting point and add/drop questions based on the actual user input.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Templates: each task type → list of (question, options) tuples.
# Options are left as free text ("Other") when the answer space is too open.
# ---------------------------------------------------------------------------

TEMPLATES = {
    "housing": {
        "label": "买房决策",
        "keywords": ["买房", "房子", "房产", "购房", "置业", "楼盘", "小区", "house", "housing", "property", "apartment"],
        "questions": [
            ("预算范围(含贷款总价)?", ["<300 万", "300-600 万", "600-1000 万", "1000-2000 万", ">2000 万"]),
            ("主要诉求?", ["首套自住", "改善置换", "投资属性", "学区刚需"]),
            ("时间窗口 + 打算住几年?", ["年内 / <5 年换", "年内 / 长住", "1-2 年 / 长住", "不急"]),
            ("家庭结构与孩子情况?", ["单身/两人", "三口之家/孩子未入学", "三口之家/孩子已在学", "三代同堂"]),
            ("城市 + 主要通勤点?(自由回答)", []),
        ],
    },
    "car": {
        "label": "买车决策",
        "keywords": ["买车", "汽车", "购车", "选车", "car", "vehicle"],
        "questions": [
            ("预算(落地价)?", ["<15 万", "15-25 万", "25-40 万", "40-80 万", ">80 万"]),
            ("主要用途?", ["家用通勤", "家庭出行+偶尔长途", "长途自驾为主", "商务/社交", "越野"]),
            ("家庭结构 + 主要乘员数?", ["1-2 人", "3 人(含小孩)", "4-5 人(含老人/小孩)", ">5 人"]),
            ("燃料偏好?", ["纯电", "插电混动", "油混", "燃油", "没想好"]),
            ("是否第一辆车 + 打算开几年?", ["首辆 / <5 年", "首辆 / 长期", "增购 / <5 年", "增购 / 长期"]),
        ],
    },
    "schooling": {
        "label": "择校/教育规划",
        "keywords": ["择校", "选学校", "上学", "升学", "学区", "幼儿园", "小学", "初中", "高中", "school", "education"],
        "questions": [
            ("学段?", ["幼儿园", "小学", "初中", "高中", "大学/留学"]),
            ("学段性质偏好?", ["公立", "民办", "国际学校", "没想好"]),
            ("长期升学路径?", ["国内高考", "出国", "两手准备", "没想好"]),
            ("孩子特点?", ["活泼外向/需宽松", "安静内向/需稳定", "自驱强/适合精英", "需较多引导"]),
            ("家庭可支持度(接送/学费/时间)?(自由回答)", []),
        ],
    },
    "medical": {
        "label": "医疗方案决策",
        "keywords": ["手术", "治疗", "化疗", "用药", "医疗", "疾病", "诊断", "medical", "treatment", "surgery"],
        "questions": [
            ("目前有的诊断/检查结果(尽量详细)?(自由回答)", []),
            ("患者情况?", ["本人 / 年轻", "本人 / 中年", "本人 / 老年", "父母/长辈", "孩子"]),
            ("已咨询过几位医生?", ["0-1 位", "2-3 位", "已有多位一致意见", "多位意见不一致"]),
            ("最关心的维度?", ["治愈概率最高", "生活质量/副作用最小", "费用可控", "恢复时间最短"]),
            ("是否在等紧急决定(如几天内要签字)?", ["紧急(<1 周)", "半紧急(1-4 周)", "可从容决策(>1 个月)"]),
        ],
    },
    "career": {
        "label": "职业/跳槽决策",
        "keywords": ["跳槽", "换工作", "offer", "离职", "职业", "career", "job change"],
        "questions": [
            ("当前情况 + 新机会方向?(自由回答)", []),
            ("最看重的维度?", ["薪资涨幅", "成长/技能", "行业赛道", "工作生活平衡", "稳定性"]),
            ("家庭财务压力?", ["无压力/有储备", "房贷+小孩", "房贷无小孩", "无房贷有小孩"]),
            ("年龄/职业阶段?", ["<30 初级", "30-35 中级", "35-40 资深", "40+"]),
            ("风险承受度?", ["高 / 愿试新东西", "中 / 有把握才动", "低 / 优先保稳"]),
        ],
    },
    "investment": {
        "label": "投资/建仓决策",
        "keywords": ["股票", "基金", "投资", "建仓", "建议持有", "仓位", "invest", "stock", "fund"],
        "questions": [
            ("具体标的 + 当前已持仓情况?(自由回答)", []),
            ("本次操作的目的?", ["新建仓", "加仓", "减仓/止盈", "止损/清仓", "只是研究"]),
            ("计划持仓周期?", ["<3 个月(短线)", "3-12 个月", "1-3 年", ">3 年(长线)"]),
            ("资金规模(占总投资比例)?", ["<5%", "5-15%", "15-30%", ">30%"]),
            ("风险承受度?", ["能接受 -30% 以上波动", "能接受 -15~30%", "只接受 <-15%"]),
        ],
    },
    "architecture": {
        "label": "架构/技术选型",
        "keywords": ["架构", "选型", "微服务", "单体", "架构设计", "技术选型", "architecture", "tech stack"],
        "questions": [
            ("当前系统规模?", ["内部工具(<10 QPS)", "小规模(<100 QPS)", "中等(100-1k QPS)", "大规模(>1k QPS)"]),
            ("团队规模?", ["1-3 人", "4-8 人", "9-20 人", ">20 人"]),
            ("最主要的痛点?(自由回答)", []),
            ("时间/资源约束?", ["需尽快落地(<1 月)", "有 1-3 月", "有 3-6 月", "长期项目"]),
            ("对变更的容忍度?", ["大改可接受", "中度重构", "只能增量改"]),
        ],
    },
    "debugging": {
        "label": "bug 根因排查",
        "keywords": ["bug", "排查", "故障", "报错", "异常", "线上问题", "P99", "延迟", "崩溃", "crash", "error", "debug"],
        "questions": [
            ("现象(越具体越好,含时间点/影响范围)?(自由回答)", []),
            ("最近变更?", ["刚发版(<24h)", "近 1 周内发过版", "近 1 月无变更", "不清楚"]),
            ("监控异常维度?", ["CPU/内存异常", "IO/网络异常", "全部正常但延迟飙升", "仅部分接口异常"]),
            ("是否可复现?", ["稳定复现", "偶发可复现", "生产环境独有", "还没尝试复现"]),
            ("已做过的排查?(自由回答)", []),
        ],
    },
}


def match_task(description: str) -> str | None:
    """Find the best matching task type via keyword frequency."""
    desc_lower = description.lower()
    best, best_score = None, 0
    for task, tpl in TEMPLATES.items():
        score = sum(1 for kw in tpl["keywords"] if kw.lower() in desc_lower)
        if score > best_score:
            best, best_score = task, score
    return best if best_score > 0 else None


def format_human(task: str) -> str:
    tpl = TEMPLATES[task]
    lines = [f"# Context starter questions: {tpl['label']}", ""]
    lines.append("在开始分析前,请先通过 AskUserQuestion 收集以下关键 context。")
    lines.append("如果用户的任务描述已经覆盖了某个问题,可以跳过该问题。")
    lines.append("")
    for i, (q, opts) in enumerate(tpl["questions"], 1):
        lines.append(f"**Q{i}**: {q}")
        if opts:
            lines.append("  Options: " + " / ".join(opts))
        else:
            lines.append("  (free-text answer expected)")
        lines.append("")
    lines.append("---")
    lines.append("提示:这是 starter 问题集,根据用户的具体情况可以增删或改写。")
    lines.append("context 不够时继续追问,不要仓促开工。")
    return "\n".join(lines)


def format_json(task: str) -> str:
    tpl = TEMPLATES[task]
    payload = {
        "task_type": task,
        "label": tpl["label"],
        "questions": [
            {"question": q, "options": opts, "free_text": len(opts) == 0}
            for q, opts in tpl["questions"]
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate starter context questions for common decision tasks."
    )
    parser.add_argument(
        "task_or_description",
        nargs="?",
        help="Task description or keyword (e.g. '我想买房' or 'housing')",
    )
    parser.add_argument("--task", help="Explicit task type (overrides auto-match)")
    parser.add_argument(
        "--format", choices=["human", "json"], default="human",
        help="Output format (default: human-readable)",
    )
    parser.add_argument("--list", action="store_true", help="List supported task types")
    args = parser.parse_args()

    if args.list:
        print("Supported task types:")
        for task, tpl in TEMPLATES.items():
            print(f"  {task:<15} {tpl['label']}")
        return 0

    task = args.task
    if not task and args.task_or_description:
        if args.task_or_description in TEMPLATES:
            task = args.task_or_description
        else:
            task = match_task(args.task_or_description)

    if not task:
        print("No matching task type. Run with --list to see supported types.", file=sys.stderr)
        print("Tip: for unsupported task types, generate your own context questions based on the skill's '开工前协议'.", file=sys.stderr)
        return 1

    if task not in TEMPLATES:
        print(f"Unknown task type: {task}. Run with --list to see supported types.", file=sys.stderr)
        return 1

    if args.format == "json":
        print(format_json(task))
    else:
        print(format_human(task))
    return 0


if __name__ == "__main__":
    sys.exit(main())
