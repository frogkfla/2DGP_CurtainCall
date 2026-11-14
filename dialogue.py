
from pico2d import *
import os


class Dialogue:
    def __init__(self):
        # 생쥐 단장 대사
        self.lines = [
            "어서 와! 드디어 공연을 시작할 시간이군!",
            "나는 이 서커스의 단장이야.",
            "오늘은 네가 무대 뒤에서 공연을 도와줘야 해!",
            "동물 친구들이 멋진 공연을 할 수 있도록 부탁할게.",
            "자, 그럼 커튼을 열어 볼까?"
        ]

        # 대사 진행 상태
        self.line_index = 0
        self.visible_count = 0
        self.finished = False

        # 타이핑 효과
        self.char_interval = 0.045
        self.char_timer = 0.0

        # 말풍선 이미지
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'assets', 'ui', 'dialogue.png'
        )
        self.image = load_image(image_path)

        # 한글 폰트
        self.font = load_font(
            'C:/Windows/Fonts/malgun.ttf', 19
        )
        self.name_font = load_font(
            'C:/Windows/Fonts/malgunbd.ttf', 18
        )
        self.hint_font = load_font(
            'C:/Windows/Fonts/malgun.ttf', 13
        )

        # 말풍선 위치 및 크기
        self.x = 870
        self.y = 500
        self.width = 608
        self.height = 232

        # 글자 위치 조정
        self.name_offset_y = 15
        self.dialogue_offset_y = 20
        self.hint_offset_y = 25

    def update(self, dt):
        if self.finished:
            return

        line = self.lines[self.line_index]

        if self.visible_count >= len(line):
            return

        self.char_timer += dt

        while self.char_timer >= self.char_interval:
            self.char_timer -= self.char_interval
            self.visible_count += 1

            if self.visible_count >= len(line):
                self.visible_count = len(line)
                break

    def next(self):
        if self.finished:
            return

        line = self.lines[self.line_index]

        if self.visible_count < len(line):
            self.visible_count = len(line)
            self.char_timer = 0.0
            return

        if self.line_index < len(self.lines) - 1:
            self.line_index += 1
            self.visible_count = 0
            self.char_timer = 0.0
        else:
            self.finished = True

    def draw(self):
        # 말풍선
        self.image.draw(
            self.x, self.y,
            self.width, self.height
        )

        # 말풍선 기준 좌표
        left = self.x - self.width / 2
        bottom = self.y - self.height / 2

        text_x = left + self.width * 0.13
        name_y = bottom + self.height * 0.68 + self.name_offset_y
        dialogue_y = bottom + self.height * 0.47 + self.dialogue_offset_y

        hint_x = left + self.width * 0.64
        hint_y = bottom + self.height * 0.30 + self.hint_offset_y

        # 이름
        self.name_font.draw(
            text_x, name_y,
            "생쥐 단장",
            (105, 57, 37)
        )

        # 대사
        line = self.lines[self.line_index]
        visible_text = line[:self.visible_count]

        self.font.draw(
            text_x, dialogue_y,
            visible_text,
            (75, 48, 35)
        )

        # 대사 완료 여부에 따라 안내 변경
        if self.finished:
            hint_text = "ENTER : 커튼 열기"
        else:
            hint_text = "SPACE : 계속하기"

        self.hint_font.draw(
            hint_x, hint_y,
            hint_text,
            (125, 85, 60)
        )
