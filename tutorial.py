
from dialogue import Dialogue


TUTORIAL_PERFORMANCE_NAME = '생쥐 단장의 첫인사'


class Tutorial:
    def __init__(self):
        self.dialogue = Dialogue()

        self.dialogue.lines = [
            "먼저 공연 화면에 어떤 정보가 있는지 살펴보자!",
            "왼쪽 위에는 지금 진행하는 공연 이름이 표시될 거야!",
            "오른쪽 위는 관객의 지루함 게이지야! 실수하거나 공연이 지연되면 올라가지!",
            "공연을 잘하면 별을 받을 수 있어! 별이 많을수록 지루함이 더 줄어들지!",
            "이제 직접 공연을 준비해 보자! 먼저 발판을 무대 중앙에 놓아 줄래?"
        ]
        self.dialogue.finished_hint = 'ENTER : 발판 놓기'

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
            game_ui.draw_title(TUTORIAL_PERFORMANCE_NAME)

        elif self.step == 2:
            demo_boredom = min(70.0, self.demo_time * 8.0)

            game_ui.draw(
                TUTORIAL_PERFORMANCE_NAME,
                demo_boredom
            )

        elif self.step == 3:
            game_ui.draw(
                TUTORIAL_PERFORMANCE_NAME,
                35
            )

            demo_stars = min(3, int(self.demo_time) % 5)
            game_ui.draw_stars(demo_stars)

        else:
            game_ui.draw(
                TUTORIAL_PERFORMANCE_NAME,
                0
            )
            game_ui.draw_stars(3)

        self.dialogue.draw()
