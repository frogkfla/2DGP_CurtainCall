
from pico2d import *
import os


class GameUI:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        ui_dir = os.path.join(base, 'assets', 'ui')

        self.title_image = load_image(
            os.path.join(ui_dir, 'performance_title.png')
        )
        self.gauge_frame = load_image(
            os.path.join(ui_dir, 'boredom_gauge_frame.png')
        )
        self.gauge_fill = load_image(
            os.path.join(ui_dir, 'boredom_gauge_fill.png')
        )
        self.star_empty = load_image(
            os.path.join(ui_dir, 'star_empty.png')
        )
        self.star_fill = load_image(
            os.path.join(ui_dir, 'star_fill.png')
        )

        self.font = load_font('C:/Windows/Fonts/malgunbd.ttf', 15)
        self.small_font = load_font('C:/Windows/Fonts/malgun.ttf', 14)

        # 공연명: 기존에 줄인 크기 유지
        self.title_x = 160
        self.title_y = 670
        self.title_width = 240
        self.title_height = 80

        # 지루함 게이지
        self.gauge_x = 1055
        self.gauge_y = 653
        self.gauge_width = 390
        self.gauge_height = 130

        # 게이지 프레임 내부의 실제 막대 영역
        self.fill_left = 0.105
        self.fill_right = 0.93
        self.fill_height = 70

        # 만족도 별
        self.star_center_x = 640
        self.star_y = 340
        self.star_size = 100
        self.star_gap = 125

        self.performance_name = '강아지의 링 통과'
        self.boredom = 0.0
        self.stars = 0

    def reset(self):
        self.boredom = 0.0
        self.stars = 0

    def add_boredom(self, amount):
        self.boredom = min(100.0, max(0.0, self.boredom + amount))

    def reward_success(self, stars):
        self.stars = max(0, min(3, stars))
        self.add_boredom(-self.stars * 5)

    def is_failed(self):
        return self.boredom >= 100.0

    def draw_title(self, name=None):
        if name is None:
            name = self.performance_name

        self.title_image.draw(
            self.title_x,
            self.title_y,
            self.title_width,
            self.title_height
        )

        text_x = self.title_x - 68
        text_y = self.title_y - 5

        self.font.draw(
            text_x, text_y, name, (104, 58, 39)
        )

    def draw_gauge(self, value=None):
        if value is None:
            value = self.boredom

        value = max(0.0, min(100.0, value))

        # 1. 프레임을 먼저 그리기
        self.gauge_frame.draw(
            self.gauge_x,
            self.gauge_y,
            self.gauge_width,
            self.gauge_height
        )

        # 2. 빨간 막대를 프레임 위에 그리기
        if value > 0:
            frame_left = self.gauge_x - self.gauge_width / 2

            bar_left = frame_left + self.gauge_width * self.fill_left
            bar_max_width = self.gauge_width * (
                self.fill_right - self.fill_left
            )

            bar_width = bar_max_width * value / 100.0
            bar_x = bar_left + bar_width / 2

            # 원본 이미지 전체를 사용해 가로로 늘려 그리기
            self.gauge_fill.draw(
                bar_x,
                self.gauge_y,
                bar_width,
                self.fill_height
            )

        # 3. 퍼센트 글자는 가장 위에 표시
        self.small_font.draw(
            self.gauge_x - 75,
            self.gauge_y - 7,
            f'지루함 {int(value)}%',
            (105, 57, 37)
        )

    def draw_stars(self, count=None):
        if count is None:
            count = self.stars

        count = max(0, min(3, count))

        for i in range(3):
            x = self.star_center_x + (i - 1) * self.star_gap

            image = self.star_fill if i < count else self.star_empty

            image.draw(
                x,
                self.star_y,
                self.star_size,
                self.star_size
            )

    def draw(self, name=None, boredom=None):
        self.draw_title(name)
        self.draw_gauge(boredom)
