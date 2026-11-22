# -*- coding: utf-8 -*-
"""
服装利润汇算命令行入口

用法示例：
    # 拉昨天订单，打印各店铺利润
    python profit_counting.py

    # 指定时间范围和店铺
    python profit_counting.py --start 2026-11-21 --end 2026-11-22 --shops 联球制衣厂,朝雄制衣厂

    # 推送到企业微信
    python profit_counting.py --send

    # 导出每单利润明细 Excel
    python profit_counting.py --export-profit

    # 导出总账 Excel（按支付日汇总）
    python profit_counting.py --export-summary
"""
import argparse
import json
import os
import sys
from datetime import datetime, date, timedelta

import requests

# 让脚本可从任意目录运行（AliData 目录加入 sys.path）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import global_params
from manager.cloth_trade_manager import ClothTradeManager

# 服装利润汇算默认店铺
CLOTH_SHOPS = ["万盈饰品厂", "联球制衣厂", "朝雄制衣厂"]
# 饰品店成本核算方式与服装不同，暂未接入，成本按 0 计
ACCESSORY_SHOPS = {"万盈饰品厂"}
# 企业微信群机器人（服装利润群）
WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c8732431-40a3-4915-b117-76940eacca18"

PROFIT_KEYS = (
    "total_amount",
    "shipping_fee",
    "refund",
    "cost",
    "shipping_cost",
    "commission",
    "profit",
)


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")


def send_md(webhook, message):
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    data = {"msgtype": "markdown", "markdown": {"content": message}}
    requests.post(url=webhook, data=json.dumps(data), headers=header)


def aggregate_profits(m, start_time, end_time):
    """汇总各店铺利润（按支付时间过滤）"""
    pay_start = start_time.strftime("%Y-%m-%d %H:%M:%S")
    pay_end = end_time.strftime("%Y-%m-%d %H:%M:%S")
    shop_profits = {}
    for shop_name, orders in m.origin_orders.items():
        with_cost = shop_name not in ACCESSORY_SHOPS
        p = dict.fromkeys(PROFIT_KEYS, 0.0)
        p["order_count"] = 0
        for order in orders:
            info = m.get_single_order_profit(order, with_cost=with_cost)
            if not (pay_start <= info["pay_time"] < pay_end):
                continue
            p["order_count"] += 1
            for k in PROFIT_KEYS:
                p[k] += info[k]
        shop_profits[shop_name] = p
    return shop_profits


def formate_profit_message(shop_profits, start_time, end_time):
    header = (
        "# **利润汇算**\n"
        + "#### **1688平台**\n "
        + '**<font color="warning">'
        + start_time.strftime("%Y-%m-%d")
        + " 到 "
        + end_time.strftime("%Y-%m-%d")
        + "</font>**\n"
    )
    total_message = ""
    total = None
    for shop_name in shop_profits:
        total_message += _formate_single(shop_name, shop_profits[shop_name])
        if total is None:
            total = dict(shop_profits[shop_name])
        else:
            for k in total:
                total[k] += shop_profits[shop_name][k]
    if total is not None and len(shop_profits) > 1:
        total_message += _formate_single("合计", total)
    return header + total_message


def _formate_single(shop_name, p):
    income = p["total_amount"] + p["shipping_fee"]
    rate = p["profit"] / income * 100 if income else 0
    return (
        "> **------%s------**\n"
        + '> **商品总收款：**<font color="info">%.2f 元</font>\n'
        + '> **运　费　　：**<font color="info">%.2f 元</font>\n'
        + '> **总退款　　：**<font color="info">%.2f 元</font>\n'
        + '> **成　本　　：**<font color="info">%.2f 元</font>\n'
        + '> **运费成本　：**<font color="info">%.2f 元</font>\n'
        + '> **平台抽佣　：**<font color="info">%.2f 元</font>\n'
        + '> **利　润　　：**<font color="warning">%.2f 元</font>\n'
        + '> **利 润 率　：**<font color="warning">%.2f%%</font>\n'
        + '> **订 单 数　：**<font color="info">%d 单</font>\n'
    ) % (
        shop_name,
        p["total_amount"],
        p["shipping_fee"],
        p["refund"],
        p["cost"],
        p["shipping_cost"],
        p["commission"],
        p["profit"],
        rate,
        p["order_count"],
    )


def print_profits(shop_profits):
    print("\n" + "=" * 56)
    print("服装利润汇算结果")
    print("=" * 56)
    for shop_name, p in shop_profits.items():
        income = p["total_amount"] + p["shipping_fee"]
        rate = p["profit"] / income * 100 if income else 0
        print(f"\n【{shop_name}】")
        print(f"  商品总收款: {p['total_amount']:.2f} 元")
        print(f"  运费:       {p['shipping_fee']:.2f} 元")
        print(f"  总退款:     {p['refund']:.2f} 元")
        print(f"  成本:       {p['cost']:.2f} 元")
        print(f"  运费成本:   {p['shipping_cost']:.2f} 元")
        print(f"  平台抽佣:   {p['commission']:.2f} 元")
        print(f"  利润:       {p['profit']:.2f} 元")
        print(f"  利润率:     {rate:.2f}%")
        print(f"  订单数:     {p['order_count']} 单")


def main():
    parser = argparse.ArgumentParser(description="服装利润汇算命令行入口")
    parser.add_argument("--start", default=None, help="开始日期 YYYY-MM-DD（默认昨天）")
    parser.add_argument("--end", default=None, help="结束日期 YYYY-MM-DD（默认今天）")
    parser.add_argument(
        "--shops",
        default=",".join(CLOTH_SHOPS),
        help="店铺列表，逗号分隔（默认服装店）",
    )
    parser.add_argument("--send", action="store_true", help="推送企业微信利润汇算")
    parser.add_argument("--export-profit", action="store_true", help="导出每单利润 Excel")
    parser.add_argument("--export-summary", action="store_true", help="导出总账 Excel")
    args = parser.parse_args()

    today = datetime.strptime(str(date.today()), "%Y-%m-%d")
    start_time = parse_date(args.start) if args.start else today + timedelta(days=-1)
    end_time = parse_date(args.end) if args.end else today + timedelta(days=0)
    shop_names = [s.strip() for s in args.shops.split(",") if s.strip()]

    print(f"拉取店铺: {shop_names}")
    print(f"时间范围: {start_time.strftime('%Y-%m-%d')} ~ {end_time.strftime('%Y-%m-%d')}")

    m = ClothTradeManager()
    m.set_params(
        shop_names=shop_names,
        start_time=start_time,
        end_time=end_time,
        order_status={global_params.OrderStatus.ALL.value},
        filter_tags=[
            global_params.OrderTags.BLUE.value,
            global_params.OrderTags.GREEN.value,
        ],
    )
    m.get_all_origin_order_list()

    shop_profits = aggregate_profits(m, start_time, end_time)
    print_profits(shop_profits)

    if args.send:
        message = formate_profit_message(shop_profits, start_time, end_time)
        send_md(WEBHOOK, message)
        print("\n已推送企业微信利润汇算")

    if args.export_profit:
        path = m.export_profit_to_excel()
        print(f"已导出每单利润: {path}")

    if args.export_summary:
        path = m.export_daily_summary_to_excel(
            start_time.strftime("%Y-%m-%d"), end_time.strftime("%Y-%m-%d")
        )
        print(f"已导出总账: {path}")


if __name__ == "__main__":
    main()
