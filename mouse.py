
from pico2d import *
import os


class Mouse:
    def __init__(self):
        # 생쥐 단장 위치
        self.x = 1175
        self.feet_y = 285

        # 캐릭터 출력 크기
        self.width = 82
        self.height = 105

        # 윗줄 8프레임만 사용
        self.frame = 0
        self.frame_count = 8

        # 애니메이션 속도
        self.frame_time = 0.0
        self.frame_speed = 0.15

        # 이미지 경로
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'assets',
            'characters',
            'mouse.png'
        )

        self.image = load_image(image_path)

        # 스프라이트 시트 정보
        self.cell_width = self.image.w / 8

        # 캐릭터 영역 자르기
        self.crop_left = 12
        self.crop_top = 155
        self.crop_width = 190
        self.crop_height = 255

    # 생쥐 단장 애니메이션
    def update(self):
        self.frame_time += 0.01

        if self.frame_time >= self.frame_speed:
            self.frame = (self.frame + 1) % self.frame_count
            self.frame_time = 0.0

    # 생쥐 단장 출력
    def draw(self, x=None, feet_y=None, row=0):
        if x is None:
            x = self.x

        if feet_y is None:
            feet_y = self.feet_y

        # 현재 프레임 위치
        frame_x = round(
            self.frame * self.cell_width
        )

        # 이미지 자르기 좌표
        clip_x = frame_x + self.crop_left

        row_crop_top = self.crop_top
        if row == 1:
            row_crop_top = 565

        clip_y = self.image.h - row_crop_top - self.crop_height

        # 발 위치 기준으로 배치
        draw_y = feet_y + self.height / 2

        # 좌우 반전하여 출력
        self.image.clip_composite_draw(
            clip_x,
            clip_y,
            self.crop_width,
            self.crop_height,
            0,
            'h',
            x,
            draw_y,
            self.width,
            self.height
        )
