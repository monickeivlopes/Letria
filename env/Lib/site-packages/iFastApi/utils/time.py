# Author: IFCZT
# Email: ifczt@qq.com
import datetime
import pytz
from .singleton import Singleton


@Singleton
class Time:
    TIME_ZONE = {
        'UTC': 'UTC',
        'ch': 'Asia/Shanghai',
        'en': 'Europe/London',
        'brazil': 'Brazil/East',
    }

    def __init__(self):
        self._time_zone = pytz.timezone(self.TIME_ZONE['ch'])

    @property
    def time_zone(self):
        return self._time_zone

    @time_zone.setter
    def time_zone(self, value):
        self._time_zone = pytz.timezone(value)

    def transform_datetime(self, date):
        """
        将日期字符串转换为日期对象
        :param date: str 日期字符串
        :return datetime.datetime
        """
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
        elif isinstance(date, int):
            date = datetime.datetime.fromtimestamp(date, self.time_zone)
        return date

    def get_start_end_timestamp(self, date, timezone=None):
        # 创建时区对象
        tz = pytz.timezone(timezone) if timezone else self.time_zone
        # 将日期字符串转换为日期对象
        date = self.transform_datetime(date)

        # 获取当天最开始的时间戳
        start_dt = tz.localize(datetime.datetime.combine(date, datetime.time.min))
        start_timestamp = int(start_dt.timestamp())

        # 获取当天最后的时间戳
        end_dt = tz.localize(datetime.datetime.combine(date, datetime.time.max))
        end_timestamp = int(end_dt.timestamp())

        return start_timestamp, end_timestamp

    @property
    def now(self):
        """
        获取当前时间
        :return datetime.datetime 2023-04-24 17:34:00.758249
        """

        return datetime.datetime.now(self.time_zone)

    def get_time_after_days(self, n):
        """
        获取 N 天后的时间
        :param n: int 天数
        :return datetime.datetime
        """
        return self.now + datetime.timedelta(days=n)

    def get_time_before_days(self, n):
        """
        获取 N 天前的时间
        :param n: int 天数
        :return datetime.datetime
        """
        return self.now - datetime.timedelta(days=n)

    def format_time(self, default_datetime: datetime.datetime = None, time_format="%Y-%m-%d %H:%M:%S"):
        """
        获取格式化时间 默认时间为当前时间
        :param default_datetime: datetime.datetime 转换datetime时间对象
        :param time_format: str 时间格式
        :return 2023-04-24 17:34:00
        """
        if not default_datetime:
            default_datetime = self.now
        elif not isinstance(default_datetime, datetime.datetime):
            default_datetime = self.transform_datetime(default_datetime)
        return default_datetime.strftime(time_format)

    def get_time_start(self, default_datetime: datetime.datetime = None):
        """
        获取指定时间的当天开始时间
        :param default_datetime: datetime.datetime 转换datetime时间对象
        :return 2023-04-24 00:00:00
        """
        if not default_datetime:
            default_datetime = self.now
        return default_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    def get_time_end(self, default_datetime: datetime.datetime = None):
        """
        获取指定时间的当天结束时间
        :param default_datetime: datetime.datetime 转换datetime时间对象
        :return 2023-04-24 23:59:59
        """
        if not default_datetime:
            default_datetime = self.now
        return default_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)

    def int_time(self, modes='s'):
        """
        获取当前时间戳
        :param modes: str 时间戳模式 s / ms / us
        :return:  s 10位 精确到秒 ms 13位 精确到毫秒 us 16位 精确到微秒
        """
        _multiple = {'s': 1, 'ms': 1000, 'us': 1000000}

        if modes not in _multiple:
            raise Exception('时间戳模式错误')

        return int(self.now.timestamp() * _multiple[modes])

    @property
    def n_year(self):
        return self.now.year

    @property
    def n_month(self):
        return self.now.month

    @property
    def n_day(self):
        return self.now.day

    @property
    def n_hour(self):
        return self.now.hour

    @property
    def n_minute(self):
        return self.now.minute

    @property
    def n_second(self):
        return self.now.second

    def to_timezone(self, default_datetime: datetime.datetime = None, timezone: str = 'UTC', time_format="%Y-%m-%d %H:%M:%S"):
        """
        将时间对象转换为指定时区的时间
        :param default_datetime: datetime.datetime 转换datetime时间对象
        :param timezone: str 时区，默认为 'UTC'
        :param time_format: str 时间格式
        :return 2023-04-24 17:34:00
        """
        if not default_datetime:
            default_datetime = self.now
        tz = pytz.timezone(timezone)
        return default_datetime.astimezone(tz).strftime(time_format)

    def time_diff(self, start_time: datetime.datetime, end_time: datetime.datetime):
        """
        计算两个时间之间的时间差
        :param start_time: datetime.datetime 开始时间
        :param end_time: datetime.datetime 结束时间
        :return datetime.timedelta 时间差
        """
        return end_time - start_time

    def countdown(self, end_time: datetime.datetime, time_format="%Y-%m-%d %H:%M:%S"):
        """
        计算从当前时间到指定时间的倒计时
        :param end_time: datetime.datetime 结束时间
        :param time_format: str 时间格式
        :return str 倒计时时间
        """
        delta = end_time - self.now
        if delta.total_seconds() < 0:
            return "已结束"
        else:
            return str(delta).split(".")[0]

    def date_range(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        获取某个日期范围内的所有日期
        :param start_date: datetime.datetime 开始日期
        :param end_date: datetime.datetime 结束日期
        :return list 所有日期列表
        """
        delta = end_date - start_date
        dates = []
        for i in range(delta.days + 1):
            date = start_date + datetime.timedelta(days=i)
            dates.append(date)
        return dates

    @property
    def today(self):
        """
        获取今天的日期
        :return datetime.datetime
        """
        return self.now.date()


time = Time()
