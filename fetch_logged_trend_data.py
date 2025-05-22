#!/usr/bin/env python
# coding: utf-8

# In[1]:

import requests
import pandas as pd
import os
from datetime import datetime

item_name_map = {
    "776879": '原皮骷髅匕首(★ StatTrak™)',
    "775988": '原皮骷髅匕首',
    "42530": '原皮蝴蝶刀',
    "43389": '原皮蝴蝶刀(★ StatTrak™)',
    "43052": '原皮 M9 刺刀',
    "43774": '原皮 M9 刺刀(★ StatTrak™)'
}

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Cookie': 'nts_mail_user=yscandrew@163.com:-1:1; NTES_CMT_USER_INFO=468391534%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B0rWNpK%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CeXNjYW5kcmV3QDE2My5jb20%3D; NTES_P_UTID=zl7C2LSsN1Z47z5gSrEIwtpxkb2ZQkgC|1725360101; P_INFO=yscandrew@163.com|1725360101|1|mail163|00&99|AU&1723610954&mail163#AU&null#10#0#0|&0||yscandrew@163.com; Device-Id=cQENlylF5nfhmj8XLAlN; game=csgo; Locale-Supported=zh-Hans; qr_code_verify_ticket=26fhoYmd1ba4ad1b294fdd7a2041806fea6b; session=1-rlcsWM7ck_sfQfQKtRMbM8_ii3IuWJ_b3WU_7M9-kctl2038289274; csrf_token=ImI2YjY5NjIwZmM2YWVjMzRjYWM5ZGRlMzJkYTgwOWE3MDMyMzFkYTUi.aC11mA.FzylYviv1MSEh9dVD8YifQ3FqaM'  # 请用你自己的cookie
}

all_data = []

for goods_id, item_name in item_name_map.items():
    try:
        # === 第一次抓取：180天（3天一个点）
        url_180 = f"https://buff.163.com/api/market/goods/price_history/buff?game=csgo&goods_id={goods_id}&currency=CNY&days=180&buff_price_type=1&with_sell_num=false"
        response_180 = requests.get(url_180, headers=headers)
        data_180 = response_180.json()
        price_data_180 = data_180['data']['price_history']

        df_180 = pd.DataFrame(price_data_180, columns=['日期', '均价'])
        df_180['日期'] = df_180['日期'].apply(lambda x: datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d'))
        df_180['饰品ID'] = goods_id
        df_180['饰品名称'] = item_name

        # === 第二次抓取：30天（每天一个点）
        url_30 = f"https://buff.163.com/api/market/goods/price_history/buff?game=csgo&goods_id={goods_id}&currency=CNY&days=30&buff_price_type=1&with_sell_num=false"
        response_30 = requests.get(url_30, headers=headers)
        data_30 = response_30.json()
        price_data_30 = data_30['data']['price_history']

        df_30 = pd.DataFrame(price_data_30, columns=['日期', '均价'])
        df_30['日期'] = df_30['日期'].apply(lambda x: datetime.fromtimestamp(x / 1000).strftime('%Y-%m-%d'))
        df_30['饰品ID'] = goods_id
        df_30['饰品名称'] = item_name

        # 合并后去重（以 30 天数据为主）
        df_combined = pd.concat([df_180, df_30], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=["日期", "饰品ID"], keep="last")

        all_data.append(df_combined)
        print(f"✅ 成功获取 {item_name}（共 {len(df_combined)} 条）")

    except Exception as e:
        print(f"❌ 获取失败：{item_name}，原因：{e}")


# 合并为总表
merged_df = pd.concat(all_data, ignore_index=True)

# 尝试读取已有历史数据并合并
final_path = os.path.join("data", "all_items.csv")
if os.path.exists(final_path):
    try:
        old_df = pd.read_csv(final_path, encoding='utf-8-sig')
        merged_df = pd.concat([old_df, merged_df], ignore_index=True)
        merged_df = merged_df.drop_duplicates(subset=["日期", "饰品ID"], keep="last")
        print("📦 已加载历史数据并合并成功")
    except Exception as e:
        print(f"⚠️ 加载历史数据失败：{e}，将仅使用本次抓取数据")

# 保存最终数据
os.makedirs("data", exist_ok=True)
merged_df.to_csv(final_path, index=False, encoding="utf-8-sig")
print(f"✅ 全部完成，共计 {len(merged_df)} 条记录，已保存至 {final_path}")