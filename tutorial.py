
from dialogue import Dialogue


class Tutorial:
    def __init__(self):
        self.dialogue = Dialogue()

        self.dialogue.lines = [
            "이제 공연 규칙을 알려주지! 동물 친구들을 도와 멋진 공연을 완성해 봐!",
            "왼쪽 위에는 지금 진행하는 공연 이름이 표시될 거야!",
            "오른쪽 위는 관객의 지루함 게이지야! 실수하거나 지연되면 올라가지!",
            "공연을 잘하면 별을 받을 수 있어! 별이 많을수록 지루함도 더 줄어들지!",
            "이제 직접 공연을 준비해 보자! 먼저 발판을 무대 중앙에 놓아 줄래?"
        ]

        self.dialogue.line_index = 0
        self.dialogue.visible_count = 0
        self.dialogue.finished = False
        self.dialogue.char_timer = 0.0

        self.demo_time = 0.0

    @property
    def finished(self):
        return self.dialogue.finished

    @property
    def step(self):
        return self.dialogue.line_index

    def next(self):
        previous_step = self.step
        self.dialogue.next()

        if self.step != previous_step:
            self.demo_time = 0.0

    def update(self, dt):
        self.dialogue.update(dt)
        self.demo_time += dt

    def draw(self, game_ui):
        if self.step == 0:
            pass

        elif self.step == 1:
            game_ui.draw_title('강아지의 링 통과')

        elif self.step == 2:
            demo_boredom = min(70.0, self.demo_time * 8.0)

            game_ui.draw(
                '강아지의 링 통과',
                demo_boredom
            )

        elif self.step == 3:
            game_ui.draw(
                '강아지의 링 통과',
                35
            )

            demo_stars = min(3, int(self.demo_time) % 5)
            game_ui.draw_stars(demo_stars)

        else:
            game_ui.draw(
                '강아지의 링 통과',
                0
            )
            game_ui.draw_stars(3)

        self.dialogue.draw()
