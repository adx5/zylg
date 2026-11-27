"""内容审核：DeepSeek 语义模型 + 规则兜底

设计：
  1. 先用确定性规则（敏感词/联系方式/薪资异常）做硬拦截——命中即 blocked，不依赖模型
  2. 规则通过后调用 DeepSeek 语义审核：判断招工骗局、违规引流、歧视、违法内容等
  3. 模型不可用（未配置 Key / 超时 / 解析失败）→ 回落到规则结果，不阻塞业务
"""
import json
import os
from typing import Optional

import httpx

from services.risk_rules import evaluate_job

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
AUDIT_TIMEOUT = float(os.environ.get("CONTENT_AUDIT_TIMEOUT", "15"))
AUDIT_ENABLED = os.environ.get("ENABLE_AI_AUDIT", "true").lower() != "false"

SYSTEM_PROMPT = """你是政务背书的同城零工平台的内容审核员，负责判断商家提交的岗位/服务能否公开展示。

【必须拦截】
- 色情低俗、陪酒陪侍、夜场娱乐类岗位
- 赌博、博彩、代练刷单、银行卡/电话卡买卖
- 招工骗局：收取押金/服装费/培训费/体检费返佣、扣押证件
- 违规引流：要求加微信/QQ/私聊、给出站外联系方式
- 虚假高薪（明显偏离当地同岗位市场价）、承诺日入过万
- 性别/年龄/地域/民族歧视，要求"仅限男性""不招某某省"
- 违法内容：涉政、涉恐、传销、代孕、代考

【允许】
正常家政、维修、搬运、餐饮服务、普工技工、物流仓管、销售客服等合规岗位。

只输出一个 JSON 对象，不要解释、不要代码块：
{"decision":"pass","reason":"内容合规"}
或
{"decision":"blocked","reason":"命中原因，30字以内"}"""


def _rule_fallback(rule) -> dict:
    return {
        "decision": "blocked" if rule.decision == "blocked" else (
            "pass" if rule.decision == "pass" else "review"),
        "reason": rule.as_text() or "规则校验通过",
        "source": "rule",
        "model": "",
    }


def _build_user_prompt(title: str, description: str, requirement: str, salary: str) -> str:
    return (
        f"标题：{title or ''}\n"
        f"薪资：{salary or ''}\n"
        f"岗位介绍：{description or ''}\n"
        f"人员要求：{requirement or ''}\n\n"
        "请判断是否允许发布。"
    )


def _parse_ai_content(content: str) -> Optional[dict]:
    """从模型返回里抠出 JSON（兼容 ```json 包裹和多余文本）"""
    text = (content or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        obj = json.loads(text[start:end + 1])
    except Exception:
        return None
    decision = str(obj.get("decision", "")).lower()
    if decision not in ("pass", "blocked"):
        return None
    return {"decision": decision, "reason": str(obj.get("reason", ""))[:120]}


async def audit_content(title: str, description: str = "", requirement: str = "", salary: str = "") -> dict:
    """返回 {decision: pass|blocked|review, reason, source: rule|ai, model}"""
    rule = evaluate_job(title, description, requirement, salary, None, None)

    # 规则命中硬拦截：直接拦，不调模型（省时省钱且不会被模型绕过）
    if rule.decision == "blocked":
        return _rule_fallback(rule)

    if not AUDIT_ENABLED or not DEEPSEEK_KEY:
        return _rule_fallback(rule)

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(title, description, requirement, salary)},
        ],
        "temperature": 0,
        "max_tokens": 200,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=AUDIT_TIMEOUT) as client:
            resp = await client.post(
                f"{DEEPSEEK_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            parsed = _parse_ai_content(content)
            if not parsed:
                return _rule_fallback(rule)
            parsed.update({"source": "ai", "model": DEEPSEEK_MODEL})
            return parsed
    except Exception:
        # 模型不可用不阻塞业务，回落到规则结果
        return _rule_fallback(rule)
