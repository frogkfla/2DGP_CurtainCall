from pico2d import *
import math
import os


class DogPerformance:
    MAX_HOOPS = 5
    HOOP_WIDTH = 72
    PALETTE_HOOP_WIDTH = 42
    DOG_WIDTH = 112
    DOG_HEIGHT = 100
    DOG_FLOOR_Y = 260
    HOOP_FLOOR_Y = 260
    DOG_START_X = 110
    DOG_END_X = 1160
    RUN_SPEED = 180
    TARGET_JUMP_DISTANCE = 133
    EARLY_PRESS_DISTANCE = 155
    LATE_PRESS_DISTANCE = 20
    TIMING_TOLERANCE = 50
    HOOP_VERTICAL_TOLERANCE = 68
    JUMP_DURATION = 0.9
    JUMP_HEIGHT = 105

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        asset_dir = os.path.join(base, 'assets')

        # 이 파일들은 프로젝트 폴더에 사용자가 추가한 에셋이다.
        self.dog_image = load_image(
            os.path.join(asset_dir, 'characters', 'dog.png')
        )
        self.hoop_image = load_image(
            os.path.join(asset_dir, 'props', 'hoop.png')
        )

        # 강아지 시트는 8열 x 3행이다. 1행은 달리기, 2행은 점프,
        # 3행은 도착 후 마무리 포즈로 사용한다.
        self.frame_columns = 8
        self.frame_width = self.dog_image.w / self.frame_columns
        # 등간격 3등분 대신, 실제 투명 여백을 확인한 행별 픽셀 범위를 쓴다.
        # 이렇게 해야 달리기 행의 꼬리/발이 점프 행에 섞이지 않는다.
        self.sprite_row_top = (64, 263, 460)
        self.sprite_row_bottom = (261, 459, 663)  # 끝 좌표는 미포함
        self.frame_interval = 0.09
        self.finish_frame_interval = 0.18
        self.frame_timer = 0.0
        self.frame_index = 0
        self.run_time = 0.0

        # 스프라이트 오른쪽의 측면 후프만 사용한다.
        self.hoop_source_x = int(self.hoop_image.w * 0.735)
        self.hoop_source_width = int(self.hoop_image.w * 0.225)
        self.hoop_source_y = int(self.hoop_image.h * 0.015)
        self.hoop_source_height = int(self.hoop_image.h * 0.97)
        self.hoop_height = (
            self.HOOP_WIDTH
            * self.hoop_source_height
            / self.hoop_source_width
        )
        # 후프 하단을 무대 바닥(강아지 발 위치)에 놓는다.
        self.HOOP_CENTER_Y = self.HOOP_FLOOR_Y + self.hoop_height / 2
        self.palette_height = (
            self.PALETTE_HOOP_WIDTH
            * self.hoop_source_height
            / self.hoop_source_width
        )

        self.hoops = []
        self.phase = 'placing'

        # 준비 화면에서도 후프는 강아지 달리기 선에 놓인다.
        self.palette_x = 125
        self.palette_width = self.PALETTE_HOOP_WIDTH
        self.palette_y = self.HOOP_FLOOR_Y + self.palette_height / 2
        self.stage_left = 160
        self.stage_right = 1120

        self.drag_kind = None
        self.drag_index = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_origin = None
        self.candidate_x = self.palette_x
        self.candidate_y = self.palette_y

        self.dog_x = self.DOG_START_X
        self.dog_y = self.DOG_FLOOR_Y
        self.arrived = False
        self.jump_active = False
        self.jump_start_x = None
        self.jump_elapsed = 0.0
        self.jump_offset = 0.0
        self.success_count = 0
        self.star_rating = 0
        self.recent_message = ''
        self.recent_message_time = 0.0
        self.rewarded = False

        # 사용자가 추가한 PERFECT / GOOD / MISS 세로 스프라이트 시트.
        ui_dir = os.path.join(asset_dir, 'ui')
        self.accuracy_image = load_image(
            os.path.join(ui_dir, 'accuracy.png')
        )
        self.accuracy_sprites = {
            'perfect': (521, 254),
            'good': (252, 234),
            'miss': (0, 226),
        }

    @property
    def remaining_hoops(self):
        return self.MAX_HOOPS - len(self.hoops)

    def _draw_hoop(self, x, y, width, height):
        self.hoop_image.clip_composite_draw(
            self.hoop_source_x,
            self.hoop_source_y,
            self.hoop_source_width,
            self.hoop_source_height,
            0,
            'h',
            x,
            y,
            width,
            height
        )

    def _in_play_area(self, x):
        return self.stage_left <= x <= self.stage_right

    def _hoop_at(self, x, y):
        for index in range(len(self.hoops) - 1, -1, -1):
            hoop = self.hoops[index]
            if (
                abs(x - hoop['x']) <= self.HOOP_WIDTH / 2
                and abs(y - hoop['y']) <= self.hoop_height / 2
            ):
                return index
        return None

    def handle_preparation_event(self, event):
        if self.phase != 'placing':
            return False

        if event.type == SDL_KEYDOWN:
            if event.key in (SDLK_RETURN, SDLK_KP_ENTER) and self.hoops:
                self.phase = 'opening'
                return True
            return False

        if event.type == SDL_MOUSEBUTTONDOWN:
            if event.button != SDL_BUTTON_LEFT:
                return False

            x = event.x
            y = 720 - event.y
            hoop_index = self._hoop_at(x, y)

            if hoop_index is not None:
                hoop = self.hoops[hoop_index]
                self.drag_kind = 'placed'
                self.drag_index = hoop_index
                self.drag_origin = (hoop['x'], hoop['y'])
                self.drag_offset_x = hoop['x'] - x
                self.drag_offset_y = 0
            elif (
                self.remaining_hoops > 0
                and abs(x - self.palette_x) <= self.palette_width / 2
                and abs(y - self.palette_y) <= self.palette_height / 2
            ):
                self.drag_kind = 'new'
                self.drag_index = None
                self.drag_offset_x = self.palette_x - x
                self.drag_offset_y = 0
                self.candidate_x = self.palette_x
                self.candidate_y = self.HOOP_CENTER_Y

        elif event.type == SDL_MOUSEMOTION and self.drag_kind:
            x = event.x + self.drag_offset_x
            if self.drag_kind == 'placed':
                hoop = self.hoops[self.drag_index]
                hoop['x'] = x
                hoop['y'] = self.HOOP_CENTER_Y
            else:
                self.candidate_x = x
                self.candidate_y = self.HOOP_CENTER_Y

        elif event.type == SDL_MOUSEBUTTONUP:
            if event.button != SDL_BUTTON_LEFT or not self.drag_kind:
                return False

            if self.drag_kind == 'new':
                if self._in_play_area(self.candidate_x):
                    self.hoops.append({
                        'x': self.candidate_x,
                        'y': self.candidate_y,
                        'state': 'pending',
                        'attempt_x': None,
                        'grade': None,
                    })
            else:
                hoop = self.hoops[self.drag_index]
                if self._in_play_area(hoop['x']):
                    hoop['x'] = min(
                        self.stage_right,
                        max(self.stage_left, hoop['x'])
                    )
                    hoop['y'] = self.HOOP_CENTER_Y
                else:
                    hoop['x'], hoop['y'] = self.drag_origin

            self.drag_kind = None
            self.drag_index = None
            self.drag_origin = None

        return False

    def draw_preparation(self):
        for hoop in self.hoops:
            self._draw_hoop(
                hoop['x'], hoop['y'], self.HOOP_WIDTH, self.hoop_height
            )

        if self.drag_kind == 'new':
            self._draw_hoop(
                self.candidate_x,
                self.candidate_y,
                self.HOOP_WIDTH,
                self.hoop_height
            )

        if self.remaining_hoops > 0:
            self._draw_hoop(
                self.palette_x,
                self.palette_y,
                self.palette_width,
                self.palette_height
            )

    def start_performance(self):
        self.phase = 'playing'
        self.hoops.sort(key=lambda hoop: hoop['x'])
        for hoop in self.hoops:
            hoop['state'] = 'pending'
            hoop['attempt_x'] = None
            hoop['grade'] = None

        self.dog_x = self.DOG_START_X
        self.dog_y = self.DOG_FLOOR_Y
        self.arrived = False
        self.jump_active = False
        self.jump_start_x = None
        self.jump_elapsed = 0.0
        self.jump_offset = 0.0
        self.frame_timer = 0.0
        self.frame_index = 0
        self.run_time = 0.0
        self.success_count = 0
        self.star_rating = 0
        self.rewarded = False
        self.recent_message = ''
        self.recent_message_time = 0.0

    def handle_performance_event(self, event):
        if self.phase != 'playing' or event.type != SDL_KEYDOWN:
            return
        if event.key != SDLK_SPACE:
            return

        pending = [
            hoop for hoop in self.hoops
            if hoop['state'] == 'pending'
        ]
        if not pending:
            return

        hoop = pending[0]
        if hoop['attempt_x'] is not None:
            return

        distance = hoop['x'] - self.dog_x
        if distance > self.EARLY_PRESS_DISTANCE:
            self._resolve_hoop(hoop, 'early')
            return
        if distance < self.LATE_PRESS_DISTANCE:
            self._resolve_hoop(hoop, 'late')
            return

        hoop['attempt_x'] = self.dog_x
        self.jump_active = True
        self.jump_start_x = self.dog_x
        self.jump_elapsed = 0.0

    def _resolve_hoop(self, hoop, grade):
        if hoop['state'] != 'pending':
            return

        hoop['grade'] = grade
        hoop['state'] = 'success' if grade in ('perfect', 'good') else 'failed'
        if hoop['state'] == 'success':
            self.success_count += 1

        messages = {
            'perfect': '완벽한 타이밍!',
            'good': '후프 통과 성공!',
            'early': '너무 일렀어!',
            'late': '너무 늦었어!',
            'missed': '점프를 놓쳤어!',
            'height': '후프 높이가 안 맞아!',
        }
        self.recent_message = messages[grade]
        self.recent_message_time = 1.4

    def _check_crossing(self, hoop):
        attempt_x = hoop['attempt_x']
        if attempt_x is None:
            self._resolve_hoop(hoop, 'missed')
            return

        distance = hoop['x'] - attempt_x
        timing_error = abs(distance - self.TARGET_JUMP_DISTANCE)
        if timing_error > self.TIMING_TOLERANCE:
            self._resolve_hoop(
                hoop,
                'early' if distance > self.TARGET_JUMP_DISTANCE else 'late'
            )
            return

        progress = (distance / self.RUN_SPEED) / self.JUMP_DURATION
        if not 0 <= progress <= 1:
            self._resolve_hoop(hoop, 'late' if progress > 1 else 'early')
            return

        dog_center_y = (
            self.DOG_FLOOR_Y
            + self.DOG_HEIGHT / 2
            - 2
            + math.sin(progress * math.pi) * self.JUMP_HEIGHT
        )
        if abs(dog_center_y - hoop['y']) > self.HOOP_VERTICAL_TOLERANCE:
            self._resolve_hoop(hoop, 'height')
            return

        self._resolve_hoop(
            hoop,
            'perfect' if timing_error <= 18 else 'good'
        )

    def update_performance(self, dt, game_ui):
        if self.phase == 'result':
            # 도착 후에는 3행의 마무리 동작만 이어서 재생한다.
            self.frame_timer += dt
            while self.frame_timer >= self.finish_frame_interval:
                self.frame_timer -= self.finish_frame_interval
                self.frame_index = (self.frame_index + 1) % self.frame_columns
            return

        if self.phase != 'playing':
            return

        self.run_time += dt
        self.frame_timer += dt
        while self.frame_timer >= self.frame_interval:
            self.frame_timer -= self.frame_interval
            self.frame_index = (self.frame_index + 1) % 8

        if self.jump_active:
            self.jump_elapsed += dt
            progress = min(1.0, self.jump_elapsed / self.JUMP_DURATION)
            self.jump_offset = math.sin(progress * math.pi) * self.JUMP_HEIGHT
            if self.jump_elapsed >= self.JUMP_DURATION:
                self.jump_active = False
                self.jump_offset = 0.0
        else:
            self.jump_offset = 0.0

        previous_x = self.dog_x
        self.dog_x += self.RUN_SPEED * dt

        for hoop in self.hoops:
            if (
                hoop['state'] == 'pending'
                and previous_x <= hoop['x'] <= self.dog_x
            ):
                self._check_crossing(hoop)

        if self.recent_message_time > 0:
            self.recent_message_time = max(0.0, self.recent_message_time - dt)
            if self.recent_message_time == 0:
                self.recent_message = ''

        if self.dog_x >= self.DOG_END_X:
            for hoop in self.hoops:
                if hoop['state'] == 'pending':
                    self._resolve_hoop(hoop, 'missed')
            self.dog_x = self.DOG_END_X
            self.arrived = True
            self.frame_index = 0
            self.frame_timer = 0.0
            self._finish_performance(game_ui)

    def _finish_performance(self, game_ui):
        self.phase = 'result'
        if self.success_count == 0:
            self.star_rating = 0
        elif self.success_count <= 2:
            self.star_rating = 1
        elif self.success_count <= 4:
            self.star_rating = 2
        else:
            self.star_rating = 3

        if self.success_count > 0 and not self.rewarded:
            game_ui.reward_success()
            self.rewarded = True

    def _draw_feedback(self, hoop):
        grade = hoop['grade']
        sprite_grade = grade if grade in ('perfect', 'good') else 'miss'
        source_y, source_height = self.accuracy_sprites[sprite_grade]
        source_width = self.accuracy_image.w
        draw_width = 100
        draw_height = draw_width * source_height / source_width

        self.accuracy_image.clip_draw(
            0,
            source_y,
            source_width,
            source_height,
            hoop['x'] + 12,
            hoop['y'] + self.hoop_height * 0.65,
            draw_width,
            draw_height
        )

    def _draw_dog(self):
        # clip_draw 원점은 이미지 하단이므로 실제 행 범위를 아래쪽 좌표로 바꾼다.
        visual_row = 2 if self.arrived else (1 if self.jump_active else 0)
        source_x0 = round(self.frame_index * self.frame_width)
        source_x1 = round((self.frame_index + 1) * self.frame_width)
        row_top = self.sprite_row_top[visual_row]
        row_bottom = self.sprite_row_bottom[visual_row]
        source_y0 = self.dog_image.h - row_bottom
        source_height = row_bottom - row_top

        self.dog_image.clip_draw(
            source_x0,
            source_y0,
            source_x1 - source_x0,
            source_height,
            self.dog_x,
            self.DOG_FLOOR_Y + self.jump_offset + self.DOG_HEIGHT / 2 - 2,
            self.DOG_WIDTH,
            self.DOG_HEIGHT
        )

    def draw_opening(self):
        self._draw_dog()
        for hoop in self.hoops:
            self._draw_hoop(
                hoop['x'], hoop['y'], self.HOOP_WIDTH, self.hoop_height
            )

    def draw_performance(self):
        # 강아지를 먼저 그려 후프 뒤쪽에 두고, 판정 표시는 가장 위에 그린다.
        self._draw_dog()
        for hoop in self.hoops:
            self._draw_hoop(
                hoop['x'], hoop['y'], self.HOOP_WIDTH, self.hoop_height
            )
            if hoop['state'] in ('success', 'failed'):
                self._draw_feedback(hoop)
