from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import datetime
import json
import os

# 签到数据文件路径
SIGN_DATA_FILE = "sign_data.json"

def load_sign_data():
    """加载签到数据"""
    if os.path.exists(SIGN_DATA_FILE):
        with open(SIGN_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_sign_data(sign_data):
    """保存签到数据"""
    with open(SIGN_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sign_data, f, ensure_ascii=False, indent=4)

@register("sign_in_plugin", "Your Name", "每日签到插件", "1.0.0")
class SignInPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.sign_data = load_sign_data()

    @filter.command("qd")
    async def sign_in(self, event: AstrMessageEvent):
        """处理签到指令"""
        user_id = event.get_sender_id()
        today = datetime.date.today()
        current_year = today.year
        current_month = today.month

        if user_id not in self.sign_data:
            self.sign_data[user_id] = {
                "yearly_signs": {current_year: 0},
                "monthly_signs": {f"{current_year}-{current_month}": 0},
                "last_sign_date": None
            }

        yearly_signs = self.sign_data[user_id]["yearly_signs"]
        monthly_signs = self.sign_data[user_id]["monthly_signs"]
        last_sign_date = self.sign_data[user_id]["last_sign_date"]

        if last_sign_date == str(today):
            message = "你今天已经签到过了，明天再来吧。"
        else:
            if current_year not in yearly_signs:
                yearly_signs[current_year] = 0
            if f"{current_year}-{current_month}" not in monthly_signs:
                monthly_signs[f"{current_year}-{current_month}"] = 0

            yearly_signs[current_year] += 1
            monthly_signs[f"{current_year}-{current_month}"] += 1
            self.sign_data[user_id]["last_sign_date"] = str(today)
            save_sign_data(self.sign_data)

            message = f"签到成功！你本月已经签到 {monthly_signs[f'{current_year}-{current_month}']} 次，本年已经签到 {yearly_signs[current_year]} 次。"

        yield event.plain_result(message)
