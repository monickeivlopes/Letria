import os
import glob
import time
import uuid
from random import randint

from PIL import Image, ImageFilter, ImageDraw, ImageFont


class CodePic:
    SIZE = (300, 150)  # 图片大小
    SLIDER_SIZE = (50, 50)  # 滑块大小
    CODE_PIC_PATH = '../assets/code_pic'
    CACHE_PATH = '../assets/cache'
    BORDER_PATH = '../assets/border.png'

    def __init__(self, redis):
        self.redis = redis

    def create_code_pic(self, code_pic_path=CODE_PIC_PATH, cache_path=CACHE_PATH, border_path=BORDER_PATH):
        """
        生成验证码图片与滑块
        """
        _uuid = uuid.uuid4()
        # 滑块随机区域
        slider_x_box = (int(self.SLIDER_SIZE[0] * 0.1), int(self.SIZE[0] - self.SLIDER_SIZE[0] * 1.1))
        slider_y_box = (int(self.SLIDER_SIZE[1] * 0.1), int(self.SIZE[1] - self.SLIDER_SIZE[1] * 1.1))
        # 随机出需要在图片上挖块的位置 预留边缘需要比滑块大一点
        slider_x = randint(*slider_x_box)
        slider_y = randint(*slider_y_box)
        # 随机选择一张图片
        jpg_list = glob.glob(f'./{code_pic_path}/*.jpg')

        if len(jpg_list) == 0:
            raise '没有找到验证码图片'
        __code_pic = Image.open(jpg_list[randint(0, len(jpg_list) - 1)])
        # 从图片中裁剪出滑块
        __slider_pic = __code_pic.crop((slider_x, slider_y, slider_x + 50, slider_y + 50))
        # 将滑块缩放到指定位置
        slider_pic = Image.new('RGBA', (self.SLIDER_SIZE[0], self.SIZE[1]), (255, 255, 255, 0))
        slider_pic.paste(__slider_pic, (0, slider_y))
        slider_pic.save(f'./{cache_path}/{_uuid}.png', 'png')
        mask = Image.new('RGBA', self.SLIDER_SIZE, (255, 255, 255, 160))

        def __mask_pic(x, y):
            # 把滑块区域粘透明贴色块上去
            __code_pic.paste(mask, (x, y), mask)
            border = Image.open(border_path)
            __code_pic.paste(border, (x - 2, y - 2), border)

        __mask_pic(slider_x, slider_y)
        # 再挖一个块 用来迷惑机器人 并设置防止两个区域重叠
        slider_x_range = range(slider_x - 50, slider_x + 50)
        robot_x_range = list(set(range(*slider_x_box)) - set(slider_x_range))
        slider_y_range = range(slider_y - 50, slider_y + 50)
        robot_slider_y = randint(*slider_y_box)
        if robot_slider_y in slider_y_range:
            robot_slider_x = robot_x_range[randint(0, len(robot_x_range) - 1)]
        else:
            robot_slider_x = randint(*slider_x_box)
        __mask_pic(robot_slider_x, robot_slider_y)
        __code_pic.save(f'./{cache_path}/{_uuid}.jpg', 'jpeg')
        # self.redis.set(uuid, slider_x, ex=120)
        return {'code_id': uuid}

    @staticmethod
    def remove_cache(path):
        """
        删除缓存文件
        """
        jpg_list = glob.glob(f'./{path}/*.jpg')
        jpg_list.extend(glob.glob(f'./{path}/*.png'))
        for jpg in jpg_list:
            file_time = os.path.getctime(jpg)
            if time.time() - file_time > 200:
                os.remove(jpg)

    @staticmethod
    def compress_pic(path, save_path):
        """
        压缩图片
        将文件夹里的图片压缩为验证码图片规格大小 300x150
        """
        jpg_list = glob.glob(f'../{path}/*.jpg')
        for i, jpg in enumerate(jpg_list):
            jpg_path = os.path.join('.', jpg)
            im = Image.open(jpg_path)
            # 如果宽度小于高度 旋转270度
            if im.size[0] < im.size[1]:
                im = im.transpose(Image.Transpose.ROTATE_270)

            # 如果宽度不是高度的刚好两倍 则进行相应裁剪
            if im.size[0] / im.size[1] != 2:
                # 高度大于宽度的1/2 就裁剪高度
                if im.size[1] > im.size[0] / 2:
                    im = im.crop((0, 0, im.size[0], im.size[0] // 2))
                else:
                    # 高度小于宽度的1/2 且宽度高度都大于规格 就裁剪宽度到高度的两倍大小
                    if im.size[0] >= CodePic.SIZE[0] and im.size[1] >= CodePic.SIZE[1]:
                        im = im.crop((0, 0, im.size[1] * 2, im.size[1]))

            # 其余情况就直接压缩直指定大小了
            im.resize((CodePic.SIZE[0], CodePic.SIZE[1]), Image.Resampling.BICUBIC).save(
                f'../{save_path}/{uuid.uuid4()}.jpg', 'jpeg')

            os.remove(jpg_path)



