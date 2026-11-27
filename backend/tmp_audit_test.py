import asyncio

from dotenv import load_dotenv

load_dotenv()

from services.content_audit import audit_content

CASES = [
    ("正常岗位", "仓库管理员", "负责货物进出库登记、盘点，每月15号发薪。"),
    ("语义风险-跑分", "网络兼职", "协助代收货款并转入指定账户，日结佣金，无需经验。"),
    ("语义风险-仅限女性", "行政助理", "要求形象气质佳，仅限女性，能接受商务宴请应酬。"),
]


async def main():
    for name, title, desc in CASES:
        r = await audit_content(title, desc, "", "")
        print(f"{name}: decision={r['decision']} source={r['source']} model={r.get('model')} reason={r['reason'][:70]}")


asyncio.run(main())
