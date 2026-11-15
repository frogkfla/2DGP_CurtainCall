
from pico2d import *
import os

from dialogue import Dialogue


class TutorialPrep:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base, 'assets', 'props', 'platform.png')

        self.image = load_image(image_path)

        # 단상 시작 위치
        self.prop_x = 250
        self.prop_y = 260

        # 단상 크기
        self.prop_width = 300
        self.prop_height = 200

        # 단상 목표 위치
        self.target_x = 640
        self.target_y = 260

        # 드래그 관련 변수
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # 배치 완료 여부
        self.completed = False

        # 배치 완료 후 생쥐 단장의 대화
        self.complete_dialogue = Dialogue()
        self.complete_dialogue.lines = [
            "좋아! 단상이 제자리에 놓였군!",
            "이제 정말 준비가 끝났어! ENTER를 눌러 공연을 시작하자!"
        ]
        self.complete_dialogue.finished_hint = 'ENTER : 커튼 열기'

    def is_on_prop(self, x, y):
        return (
            self.prop_x - self.prop_width / 2 <= x <= self.prop_x + self.prop_width / 2
            and self.prop_y - self.prop_height / 2 <= y <= self.prop_y + self.prop_height / 2
        )

    def handle_event(self, event):
        if self.completed:
            return

        if event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                x = event.x
                y = 720 - event.y

                if self.is_on_prop(x, y):
                    self.dragging = True
                    self.drag_offset_x = self.prop_x - x
                    self.drag_offset_y = self.prop_y - y

        elif event.type == SDL_MOUSEMOTION:
            if self.dragging:
                self.prop_x = event.x + self.drag_offset_x
                self.prop_y = 720 - event.y + self.drag_offset_y

        elif event.type == SDL_MOUSEBUTTONUP:
            if event.button == SDL_BUTTON_LEFT and self.dragging:
                self.dragging = False

                distance = (
                    (self.prop_x - self.target_x) ** 2
                    + (self.prop_y - self.target_y) ** 2
                ) ** 0.5

                if distance < 80:
                    self.prop_x = self.target_x
                    self.prop_y = self.target_y
                    self.completed = True

    def update(self, dt):
        if self.completed:
            self.complete_dialogue.update(dt)

    def draw(self):
        self.image.draw(
            self.prop_x,
            self.prop_y,
            self.prop_width,
            self.prop_height
        )

        if not self.completed:
            draw_rectangle(
                self.target_x - self.prop_width / 2,
                self.target_y - self.prop_height / 2,
                self.target_x + self.prop_width / 2,
                self.target_y + self.prop_height / 2
            )

    def draw_dialogue(self):
        if self.completed:
            self.complete_dialogue.draw()
