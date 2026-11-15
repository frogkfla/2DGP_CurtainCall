
from pico2d import *
import os
import textwrap


class Dialogue:
    def __init__(self):
        self.lines = [
            "어서 와! 드디어 공연을 시작할 시간이군!",
            "나는 이 서커스의 단장이야.",
            "오늘은 네가 무대 뒤에서 공연을 도와줘야 해!",
            "동물 친구들이 멋진 공연을 할 수 있도록 부탁할게.",
            "좋아! 공연을 시작하기 전에 무대 준비부터 해 보자."
        ]

        self.line_index = 0
        self.visible_count = 0
        self.finished = False

        self.char_interval = 0.045
        self.char_timer = 0.0

        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'assets', 'ui', 'dialogue.png'
        )

        self.image = load_image(image_path)

        self.font = load_font('C:/Windows/Fonts/gulim.ttc', 19)
        self.name_font = load_font('C:/Windows/Fonts/malgunbd.ttf', 18)
        self.hint_font = load_font('C:/Windows/Fonts/malgun.ttf', 13)

        # 기존 말풍선 위치와 크기 유지
        self.x = 870
        self.y = 500
        self.width = 608
        self.height = 232

        self.name_offset_y = 15
        self.dialogue_offset_y = 20
        self.hint_offset_y = 25

        # 줄바꿈 설정
        self.line_spacing = 27

    def get_wrapped_text(self):
        line = self.lines[self.line_index]

        # 말풍선에서 대사가 사용할 수 있는 가로 너비
        max_width = self.width * 0.76

        wrapped_lines = []
        current_line = ""

        # 기존 수동 줄바꿈은 제거하고 띄어쓰기 기준으로 분리
        words = line.replace('\n', ' ').split()

        for word in words:
            test_line = current_line + " " + word if current_line else word

            # pico2d Font는 get_text_width()를 지원하지 않으므로
            # 한글과 영문에 가중치를 적용해 너비 추정
            estimated_width = 0

            for char in test_line:
                if ord(char) > 127:
                    estimated_width += 19
                elif char == ' ':
                    estimated_width += 6
                else:
                    estimated_width += 10

            if estimated_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    wrapped_lines.append(current_line)

                current_line = word

        if current_line:
            wrapped_lines.append(current_line)

        return '\n'.join(wrapped_lines)


    def update(self, dt):
        if self.finished:
            return

        text = self.get_wrapped_text()

        if self.visible_count >= len(text):
            return

        self.char_timer += dt

        while self.char_timer >= self.char_interval:
            self.char_timer -= self.char_interval
            self.visible_count += 1

            if self.visible_count >= len(text):
                self.visible_count = len(text)
                break

    def next(self):
        if self.finished:
            return

        text = self.get_wrapped_text()

        if self.visible_count < len(text):
            self.visible_count = len(text)
            self.char_timer = 0.0
            return

        if self.line_index < len(self.lines) - 1:
            self.line_index += 1
            self.visible_count = 0
            self.char_timer = 0.0
        else:
            self.finished = True

    def draw(self):
        self.image.draw(
            self.x,
            self.y,
            self.width,
            self.height
        )

        left = self.x - self.width / 2
        bottom = self.y - self.height / 2

        text_x = left + self.width * 0.13

        name_y = (
            bottom
            + self.height * 0.68
            + self.name_offset_y
        )

        dialogue_y = (
            bottom
            + self.height * 0.47
            + self.dialogue_offset_y
        )

        hint_x = left + self.width * 0.64

        hint_y = (
            bottom
            + self.height * 0.20
            + self.hint_offset_y
        )

        self.name_font.draw(
            text_x,
            name_y,
            "생쥐 단장",
            (105, 57, 37)
        )

        # 줄바꿈된 대사를 한 글자씩 표시
        full_text = self.get_wrapped_text()
        visible_text = full_text[:self.visible_count]

        for i, text_line in enumerate(visible_text.split('\n')):
            if text_line:
                self.font.draw(
                    text_x,
                    dialogue_y - i * self.line_spacing,
                    text_line,
                    (75, 48, 35)
                )

        hint_text = (
            "ENTER : 커튼 열기"
            if self.finished
            else "SPACE : 계속하기"
        )

        self.hint_font.draw(
            hint_x,
            hint_y,
            hint_text,
            (125, 85, 60)
        )
