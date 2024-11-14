import os
import django
import logging
from datetime import datetime
import requests
import json
from django.utils import timezone  # 导入 Django 时区模块

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'competition_platform.settings')  # 确保路径正确
django.setup()

from apps.competitions.models import Competition  # 正确导入 Competition 模型

# 配置日志
logging.basicConfig(
    filename='update_competitions.log',  # 日志文件
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)
logger = logging.getLogger(__name__)

# 数据源 URL
URL = 'https://gitee.com/Probius/Hello-CTFtime/raw/main/CN.json'

# 本地保存的 JSON 文件名
JSON_FILENAME = 'competitions.json'

# 定义状态映射
STATUS_MAPPING = {
    "报名未开始": 0,
    "报名进行中": 1,
    "报名已结束": 2,
    "比赛进行中": 3,
    "比赛已结束": 4,
    "已经结束": 4,
    3: 3,  # 数字格式直接使用
    # 根据需要添加其他状态映射
}

def fetch_data(url):
    """
    从指定 URL 获取 JSON 数据。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("成功获取 JSON 数据。")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"请求 JSON 数据失败: {e}")
        raise

def save_json(data, filename):
    """
    将 JSON 数据保存到本地文件。
    """
    try:
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logger.info(f"成功将 JSON 数据保存到 {filename}。")
    except IOError as e:
        logger.error(f"保存 JSON 数据失败: {e}")
        raise

def load_json(filename):
    """
    从本地文件加载 JSON 数据。
    """
    try:
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        logger.info(f"成功从 {filename} 加载 JSON 数据。")
        return data
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"加载 JSON 数据失败: {e}")
        raise

def parse_datetime(date_str):
    """
    将字符串日期转换为 aware datetime 对象。
    支持多种日期格式，可以根据需要扩展。
    """
    date_formats = [
        '%Y年%m月%d日 %H:%M',
        '%Y年%m月%d日 %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H:%M:%S',
        # 添加更多格式如果需要
    ]
    for fmt in date_formats:
        try:
            naive_dt = datetime.strptime(date_str, fmt)
            aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
            return aware_dt
        except (ValueError, TypeError, timezone.UnknownTimeZoneError):
            continue
    logger.warning(f"无法解析日期字符串: {date_str}")
    return None

def map_status(status):
    """
    将状态字符串或整数映射为预定义的整数状态。
    """
    return STATUS_MAPPING.get(status, 0)  # 默认使用 0

def process_competitions(data):
    """
    处理 JSON 数据中的每个比赛并存入数据库。
    """
    competitions = data.get('data', {}).get('result', [])
    if not competitions:
        logger.warning("没有找到任何比赛数据。")
        return

    for event in competitions:
        name = event.get('name')
        link = event.get('link')
        competition_type = event.get('type')
        readmore = event.get('readmore')  # 用于描述
        status_raw = event.get('status', 0)
        status = map_status(status_raw)

        # 解析时间
        reg_time_start = parse_datetime(event.get('reg_time_start'))
        reg_time_end = parse_datetime(event.get('reg_time_end'))
        comp_time_start = parse_datetime(event.get('comp_time_start'))
        comp_time_end = parse_datetime(event.get('comp_time_end'))

        # 检查必填字段
        if not all([name, link, competition_type, readmore, reg_time_start, reg_time_end, comp_time_start, comp_time_end]):
            logger.warning(f"缺少必要字段，跳过比赛: {name}")
            continue

        try:
            # 获取或创建比赛
            competition, created = Competition.objects.get_or_create(
                name=name,
                defaults={
                    'link': link,
                    'type': competition_type,
                    'reg_time_start': reg_time_start,
                    'reg_time_end': reg_time_end,
                    'comp_time_start': comp_time_start,
                    'comp_time_end': comp_time_end,
                    'description': readmore,  # 使用 readmore 作为描述
                    'status': status,
                }
            )

            if not created:
                # 更新已有比赛的信息
                competition.link = link
                competition.type = competition_type
                competition.reg_time_start = reg_time_start
                competition.reg_time_end = reg_time_end
                competition.comp_time_start = comp_time_start
                competition.comp_time_end = comp_time_end
                competition.description = readmore
                competition.status = status
                competition.save()
                logger.info(f"更新了已有的比赛信息: {name}")
            else:
                logger.info(f"添加了新的比赛: {name}")

        except Exception as e:
            logger.error(f"处理比赛 '{name}' 时出错: {e}")
            continue

def main():
    """
    主函数，执行数据获取、保存、加载和处理。
    """
    try:
        # 获取数据
        data = fetch_data(URL)

        # 保存到本地文件
        save_json(data, JSON_FILENAME)

        # 从本地文件加载数据
        loaded_data = load_json(JSON_FILENAME)

        # 处理并存储比赛数据
        process_competitions(loaded_data)

        logger.info("所有比赛数据已成功处理。")

    except Exception as e:
        logger.critical(f"脚本执行失败: {e}")

if __name__ == '__main__':
    main()
