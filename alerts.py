import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import pandas as pd
import os
import streamlit as st

buy_price_map = {
    "776879": 4300.0,
    "775988": 4500.0,
    "42530":  12000.0,
    "43389":  10000.0,
    "43052":  8000.0,
    "43774":  7000.0
}

sell_price_map = {
    "776879": 4800.0,
    "775988": 5000.0,
    "42530":  20000.0,
    "43389":  16000.0,
    "43052":  11000.0,
    "43774":  9000.0
}

# 邮件发送函数
def send_email(subject, content):
    smtp_server = 'smtp.126.com'
    smtp_port = 465
    smtp_user = 'yscandrew@126.com'
    smtp_password = 'CRFOTPAINUQBXFQK'  # 授权码
    receiver_email = 'yscandrew@163.com'

    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

# 价格提醒函数
def check_price_alert(data_file, buy_price, sell_price, item_name):

    if not os.path.exists(data_file):
        return False, "❌ 数据文件不存在"

    df = pd.read_csv(data_file, encoding="utf-8-sig")
    if df.empty or "均价" not in df.columns:
        return False, "❌ 数据无效"

    latest_price = df["均价"].iloc[-1]
    latest_date = df["日期"].iloc[-1]

    content = (
        f"📌 {item_name}价格提醒\n\n"
        f"📉 买入提醒阈值：{buy_price:.2f} 元\n"
        f"📈 卖出提醒阈值：{sell_price:.2f} 元\n"
        f"📊 当前均价：{latest_price:.2f} 元\n"
        f"📅 数据日期：{latest_date}\n\n"
        f"🔗 [查看 BUFF 链接](https://buff.163.com/goods/{os.path.basename(data_file).split('.')[0]})"
    )

    subject = f"CS2 饰品价格提醒"

    try:
        if latest_price < buy_price:
            send_email(subject, f"✅ 建议择时买入\n\n{content}")
            return True, f"📩 邮件提醒已发送：当前价格 {latest_price:.2f} 元，低于买入阈值 {buy_price:.2f} 元"
        elif latest_price > sell_price:
            send_email(subject, f"❗ 建议择时卖出\n\n{content}")
            return True, f"📩 邮件提醒已发送：当前价格 {latest_price:.2f} 元，高于卖出阈值 {sell_price:.2f} 元"
        else:
            return False, "✅ 当前价格在安全区间，无需提醒"
    except Exception as e:
        return False, f"⚠ 邮件发送失败: {e}"
