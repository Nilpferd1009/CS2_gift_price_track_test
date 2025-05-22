# Student homework for deploy, do not change anything!!
# 🎁 CS2 Gift Price Tracker

Track and visualize historical prices of CS2 skins from Buff.163, with alerts and interactive charts.

## 🔧 Features
- Daily price fetching from Buff
- Streamlit-based UI with line/box plot
- Email alerts for buy/sell thresholds
- Skins currently supported: 6 knives
- Auto updated data by GitHub Actions

## 📦 How to run
```yaml
on:
  schedule:
    - cron: '0 16 * * *'  # 每天 UTC 16:00（对应北京时间 00:00）
