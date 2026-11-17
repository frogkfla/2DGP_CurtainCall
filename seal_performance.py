from pico2d import *
import math
import os


class SealPerformance:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

    STAGE_LEFT = 150
    STAGE_RIGHT = 1130
    STAGE_GROUND_Y = 85

    LAUNCHER_FLOOR_Y = 175
    LAUNCHER_WIDTH = 165
    LAUNCHER_PALETTE_WIDTH = 78
    LAUNCHER_PALETTE_FLOOR = 75
    LAUNCHER_PALETTE_X = 125

    BALL_PALETTE_X = 260
    BALL_PALETTE_Y = 118
    BALL_SIZE = 40

    SEAL_LEFT_X = 420
    SEAL_RIGHT_X = 930
    SEAL_FLOOR_Y = 185
    SEAL_WIDTH = 160

    MIN_ANGLE = 10
    MAX_ANGLE = 70
    ANGLE_STEP = 2
    START_ANGLE = 30
    LAUNCH_SPEED = 620.0
    GRAVITY = 450.0
    # 발사대 그림의 받침 회전축에서 각 프레임의 주둥이 중앙까지의 거리.
    # 기존 공통 길이는 각도가 큰 프레임에서 주둥이를 지나쳐 공이 뜨는 문제가 있었다.
    BARREL_LENGTH = 79.0
    PIVOT_OFFSET_X = 22.0
    PIVOT_HEIGHT = 104.0
    NOSE_HIT_RADIUS = 38.0
    LAUNCHER_FRAME_PADDING = 3
    SEAL_FRAME_LEFT_PADDING = 10
    BALANCE_DURATION = 6.0
    BALANCE_MAX_TILT = 0.78
    BALANCE_CONTROL_ACCEL = 5.5
    BALANCE_DAMPING = 1.8
    BALANCE_VISUAL_SHIFT = 34
    PERFECT_HIT_DISTANCE = 12.0
    ACCURACY_DRAW_WIDTH = 90

    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        assets = os.path.join(base, 'assets')

        # 이 스프라이트들은 프로젝트에 추가된 사용자 에셋이다.
        self.seal_image = load_image(
            os.path.join(assets, 'characters', 'seal.png')
        )
        self.launcher_image = load_image(
            os.path.join(assets, 'props', 'launcher.png')
        )
        self.ball_image = load_image(
            os.path.join(assets, 'props', 'ball.png')
        )
        self.accuracy_image = load_image(
            os.path.join(assets, 'ui', 'accuracy.png')
        )
        self.accuracy_sprites = {
            'perfect': (521, 254),
            'good': (252, 234),
            'miss': (0, 226),
        }

        self.launcher_columns = 8
        self.launcher_frame_width = self.launcher_image.w / self.launcher_columns
        self.launcher_source_top = 160
        self.launcher_source_bottom = 568
        self.launcher_source_height = (
            self.launcher_source_bottom - self.launcher_source_top
        )
        self.launcher_source_y = (
            self.launcher_image.h - self.launcher_source_bottom
        )
        self.launcher_draw_height = (
            self.LAUNCHER_WIDTH
            * self.launcher_source_height
            / self.launcher_frame_width
        )

        self.ball_columns = 8
        self.ball_frame_width = self.ball_image.w / self.ball_columns
        self.ball_source_top = 233
        self.ball_source_bottom = 493
        self.ball_source_height = self.ball_source_bottom - self.ball_source_top
        self.ball_source_y = self.ball_image.h - self.ball_source_bottom

        self.seal_columns = 8
        self.seal_frame_width = self.seal_image.w / self.seal_columns
        self.seal_rows = {
            'idle': (31, 327),
            'caught': (395, 690),
        }
        self.seal_floor_y = self.SEAL_FLOOR_Y
        idle_top, idle_bottom = self.seal_rows['idle']
        self.seal_source_height = idle_bottom - idle_top
        self.seal_draw_height = (
            self.SEAL_WIDTH
            * self.seal_source_height
            / self.seal_frame_width
        )
        self._set_seal_position(self.SEAL_RIGHT_X)

        self.phase = 'placing'
        self.launcher_back_x = None
        self.launcher_front_x = None
        self.launcher_direction = 1
        self.launcher_angle = self.START_ANGLE
        self.ball_loaded = False

        self.drag_kind = None
        self.drag_offset_x = 0.0
        self.candidate_x = self.LAUNCHER_PALETTE_X
        self.candidate_ball_x = self.BALL_PALETTE_X
        self.candidate_ball_y = self.BALL_PALETTE_Y

        self.ball_x = 0.0
        self.ball_y = 0.0
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.ball_rotation = 0.0
        self.flight_time = 0.0
        self.ball_frame = 0
        self.ball_frame_timer = 0.0
        self.seal_frame = 0
        self.seal_frame_timer = 0.0
        self.caught = False
        self.rewarded = False
        self.balance_elapsed = 0.0
        self.balance_angle = 0.0
        self.balance_angular_velocity = 0.0
        self.balance_left = False
        self.balance_right = False
        self.miss_reason = 'shot'
        self.accuracy_grade = None

    def _angle_frame(self, angle=None):
        if angle is None:
            angle = self.launcher_angle
        progress = (angle - self.MIN_ANGLE) / (self.MAX_ANGLE - self.MIN_ANGLE)
        return max(0, min(7, round(progress * 7)))

    def _set_seal_position(self, x):
        self.seal_x = x
        # 물개 스프라이트 첫 프레임의 콧잔등 위치를 기준으로 착지점을 갱신한다.
        self.nose_x = self.seal_x - self.SEAL_WIDTH * 0.335
        self.nose_y = self.seal_floor_y + self.seal_draw_height * 0.93

    def _launcher_muzzle(self, x, floor_y, direction=1):
        radians = math.radians(self.launcher_angle)
        return (
            x - direction * self.PIVOT_OFFSET_X
            + direction * self.BARREL_LENGTH * math.cos(radians),
            floor_y
            + self.PIVOT_HEIGHT
            + self.BARREL_LENGTH * math.sin(radians)
        )

    def _draw_launcher(self, x, floor_y, width, direction=1):
        frame = self._angle_frame()
        # 인접 프레임이 섞이는 왼쪽 경계만 안쪽으로 자른다.
        # 오른쪽은 주둥이 테두리가 놓이는 쪽이므로 원본 끝까지 보존한다.
        source_x0 = round(frame * self.launcher_frame_width) + self.LAUNCHER_FRAME_PADDING
        source_x1 = round((frame + 1) * self.launcher_frame_width)
        height = width * self.launcher_source_height / self.launcher_frame_width
        flip = 'h' if direction < 0 else ''

        self.launcher_image.clip_composite_draw(
            source_x0,
            self.launcher_source_y,
            source_x1 - source_x0,
            self.launcher_source_height,
            0,
            flip,
            x,
            floor_y + height / 2,
            width,
            height
        )

    def _draw_ball(self, x, y, size=None, rotation=0):
        if size is None:
            size = self.BALL_SIZE

        frame = self.ball_frame
        source_x0 = round(frame * self.ball_frame_width)
        source_x1 = round((frame + 1) * self.ball_frame_width)
        self.ball_image.clip_composite_draw(
            source_x0,
            self.ball_source_y,
            source_x1 - source_x0,
            self.ball_source_height,
            rotation,
            '',
            x,
            y,
            size,
            size
        )

    def _draw_seal(self, x=None, backstage=False):
        row_name = 'idle'
        row_top, row_bottom = self.seal_rows[row_name]
        source_y = self.seal_image.h - row_bottom
        source_height = row_bottom - row_top
        frame = self.seal_frame
        source_x0 = (
            round(frame * self.seal_frame_width)
            + self.SEAL_FRAME_LEFT_PADDING
        )
        # 좌우 반전 시 원본 왼쪽 경계가 화면 오른쪽이 된다.
        # 이 경계만 안쪽으로 옮겨 이웃 프레임을 제외하고 반대쪽 끝은 보존한다.
        source_x1 = round((frame + 1) * self.seal_frame_width)
        draw_height = self.SEAL_WIDTH * source_height / self.seal_frame_width
        if x is None:
            x = self.seal_x
        flip = '' if backstage else 'h'

        self.seal_image.clip_composite_draw(
            source_x0,
            source_y,
            source_x1 - source_x0,
            source_height,
            0,
            flip,
            x,
            self.seal_floor_y + draw_height / 2,
            self.SEAL_WIDTH,
            draw_height
        )

    def _draw_launcher_scene(self):
        self._draw_launcher(
            self.launcher_front_x,
            self.LAUNCHER_FLOOR_Y,
            self.LAUNCHER_WIDTH,
            self.launcher_direction
        )

    def _preparation_launcher_x(self):
        if self.drag_kind == 'new_launcher':
            return self.candidate_x
        return self.launcher_back_x

    def _launcher_hit(self, x, y):
        if self.launcher_back_x is None:
            return False
        top = self.LAUNCHER_FLOOR_Y + self.launcher_draw_height
        return (
            abs(x - self.launcher_back_x) <= self.LAUNCHER_WIDTH / 2
            and self.LAUNCHER_FLOOR_Y - 10 <= y <= top
        )

    def _in_play_area(self, x):
        return self.STAGE_LEFT <= x <= self.STAGE_RIGHT

    def handle_preparation_event(self, event):
        if self.phase != 'placing':
            return False

        if event.type == SDL_KEYDOWN:
            if (
                event.key in (SDLK_RETURN, SDLK_KP_ENTER)
                and self.launcher_back_x is not None
                and self.ball_loaded
            ):
                # 무대 뒤와 관객석은 좌우가 반대인 시점이다.
                self.launcher_front_x = self.SCREEN_WIDTH - self.launcher_back_x
                seal_x = (
                    self.SEAL_LEFT_X
                    if self.launcher_front_x >= self.SCREEN_WIDTH / 2
                    else self.SEAL_RIGHT_X
                )
                self._set_seal_position(seal_x)
                self.launcher_direction = (
                    1 if self.nose_x >= self.launcher_front_x else -1
                )
                self.phase = 'opening'
                return True
            return False

        if event.type == SDL_MOUSEBUTTONDOWN:
            if event.button != SDL_BUTTON_LEFT:
                return False

            x = event.x
            y = self.SCREEN_HEIGHT - event.y

            if self._launcher_hit(x, y):
                self.drag_kind = 'placed_launcher'
                self.drag_offset_x = self.launcher_back_x - x
            elif (
                self.launcher_back_x is None
                and abs(x - self.LAUNCHER_PALETTE_X)
                <= self.LAUNCHER_PALETTE_WIDTH / 2
                and self.LAUNCHER_PALETTE_FLOOR
                <= y
                <= self.LAUNCHER_PALETTE_FLOOR
                + self.LAUNCHER_PALETTE_WIDTH
                * self.launcher_source_height
                / self.launcher_frame_width
            ):
                self.drag_kind = 'new_launcher'
                self.drag_offset_x = self.LAUNCHER_PALETTE_X - x
                self.candidate_x = self.LAUNCHER_PALETTE_X
            elif (
                not self.ball_loaded
                and abs(x - self.BALL_PALETTE_X) <= self.BALL_SIZE / 2 + 8
                and abs(y - self.BALL_PALETTE_Y) <= self.BALL_SIZE / 2 + 8
            ):
                self.drag_kind = 'ball'
                self.candidate_ball_x = x
                self.candidate_ball_y = y

        elif event.type == SDL_MOUSEMOTION and self.drag_kind:
            if self.drag_kind in ('new_launcher', 'placed_launcher'):
                self.candidate_x = event.x + self.drag_offset_x
            else:
                self.candidate_ball_x = event.x
                self.candidate_ball_y = self.SCREEN_HEIGHT - event.y

        elif event.type == SDL_MOUSEBUTTONUP and self.drag_kind:
            x = event.x
            y = self.SCREEN_HEIGHT - event.y

            if self.drag_kind in ('new_launcher', 'placed_launcher'):
                if self._in_play_area(self.candidate_x):
                    self.launcher_back_x = max(
                        self.STAGE_LEFT,
                        min(self.STAGE_RIGHT, self.candidate_x)
                    )
                elif self.drag_kind == 'placed_launcher':
                    self.candidate_x = self.launcher_back_x
            elif self.drag_kind == 'ball' and self.launcher_back_x is not None:
                muzzle_x, muzzle_y = self._launcher_muzzle(
                    self.launcher_back_x,
                    self.LAUNCHER_FLOOR_Y,
                    direction=1
                )
                if abs(x - muzzle_x) <= 48 and abs(y - muzzle_y) <= 48:
                    self.ball_loaded = True

            self.drag_kind = None

        return False

    def begin_aiming(self):
        if self.phase == 'opening':
            self.phase = 'aiming'

    def handle_performance_event(self, event):
        if event.type == SDL_KEYUP:
            if self.phase == 'balancing':
                if event.key == SDLK_LEFT:
                    self.balance_left = False
                elif event.key == SDLK_RIGHT:
                    self.balance_right = False
            return

        if event.type != SDL_KEYDOWN:
            return

        if self.phase == 'balancing':
            if event.key == SDLK_LEFT:
                self.balance_left = True
            elif event.key == SDLK_RIGHT:
                self.balance_right = True
        elif self.phase == 'aiming':
            if event.key == SDLK_UP:
                self.launcher_angle = min(
                    self.MAX_ANGLE,
                    self.launcher_angle + self.ANGLE_STEP
                )
            elif event.key == SDLK_DOWN:
                self.launcher_angle = max(
                    self.MIN_ANGLE,
                    self.launcher_angle - self.ANGLE_STEP
                )
            elif event.key == SDLK_SPACE and self.ball_loaded:
                self._launch()
        elif self.phase == 'miss' and event.key == SDLK_r:
            self.ball_loaded = True
            self.ball_frame = 0
            self.miss_reason = 'shot'
            self.accuracy_grade = None
            self.phase = 'aiming'

    def _launch(self):
        muzzle_x, muzzle_y = self._launcher_muzzle(
            self.launcher_front_x,
            self.LAUNCHER_FLOOR_Y,
            self.launcher_direction
        )
        radians = math.radians(self.launcher_angle)
        self.ball_x = muzzle_x
        self.ball_y = muzzle_y
        self.ball_vx = self.launcher_direction * self.LAUNCH_SPEED * math.cos(radians)
        self.ball_vy = self.LAUNCH_SPEED * math.sin(radians)
        self.ball_rotation = 0.0
        self.flight_time = 0.0
        self.miss_reason = 'shot'
        self.accuracy_grade = None
        self.ball_loaded = False
        self.phase = 'flying'

    def _trajectory_position(self, time):
        muzzle_x, muzzle_y = self._launcher_muzzle(
            self.launcher_front_x,
            self.LAUNCHER_FLOOR_Y,
            self.launcher_direction
        )
        radians = math.radians(self.launcher_angle)
        vx = self.launcher_direction * self.LAUNCH_SPEED * math.cos(radians)
        vy = self.LAUNCH_SPEED * math.sin(radians)
        return (
            muzzle_x + vx * time,
            muzzle_y + vy * time - 0.5 * self.GRAVITY * time * time
        )

    def _draw_trajectory(self):
        time = 0.0
        while time <= 3.0:
            x, y = self._trajectory_position(time)
            if (
                x < 0 or x > self.SCREEN_WIDTH
                or y < self.STAGE_GROUND_Y
            ):
                break
            draw_circle(
                int(x), int(y), 3,
                247, 205, 117, 190,
                filled=True
            )
            time += 0.075

    def update(self, dt, game_ui):
        if self.phase == 'flying':
            previous_x, previous_y = self.ball_x, self.ball_y
            self.flight_time += dt
            self.ball_x += self.ball_vx * dt
            self.ball_vy -= self.GRAVITY * dt
            self.ball_y += self.ball_vy * dt
            self.ball_rotation -= math.degrees(
                self.ball_vx / self.BALL_SIZE
            ) * dt

            # 빠른 프레임에서도 콧잔등을 통과해 놓치지 않도록 선분 간격을 검사한다.
            impact_distance = self._segment_target_distance(
                previous_x, previous_y, self.ball_x, self.ball_y
            )
            if impact_distance <= self.NOSE_HIT_RADIUS:
                self.ball_x = self.nose_x
                self.ball_y = self.nose_y
                self.accuracy_grade = (
                    'perfect'
                    if impact_distance <= self.PERFECT_HIT_DISTANCE
                    else 'good'
                )
                self.phase = 'balancing'
                self.caught = True
                self.balance_elapsed = 0.0
                self.balance_angle = 0.12 * self.launcher_direction
                self.balance_angular_velocity = (
                    0.45 * self.launcher_direction
                )
                self.balance_left = False
                self.balance_right = False
            elif (
                self.ball_y <= self.STAGE_GROUND_Y
                or self.ball_x < 0
                or self.ball_x > self.SCREEN_WIDTH
                or self.flight_time >= 4.0
            ):
                self.phase = 'miss'
                self.accuracy_grade = 'miss'

        if self.phase == 'balancing':
            self._update_balance(dt, game_ui)
        elif self.phase == 'falling':
            self._update_falling_ball(dt)

        if self.phase in ('flying', 'balancing', 'caught', 'falling'):
            self.ball_frame_timer += dt
            while self.ball_frame_timer >= 0.07:
                self.ball_frame_timer -= 0.07
                self.ball_frame = (self.ball_frame + 1) % self.ball_columns

        if self.phase in ('aiming', 'balancing', 'caught'):
            self._update_seal_animation(dt)

    def _update_balance(self, dt, game_ui):
        self.balance_elapsed += dt
        control = int(self.balance_right) - int(self.balance_left)
        wobble = (
            1.45 * math.sin(self.balance_elapsed * 2.6)
            + 0.55 * math.sin(self.balance_elapsed * 4.7)
        )
        angular_acceleration = (
            3.6 * math.sin(self.balance_angle)
            + wobble
            + control * self.BALANCE_CONTROL_ACCEL
            - self.BALANCE_DAMPING * self.balance_angular_velocity
        )
        self.balance_angular_velocity += angular_acceleration * dt
        self.balance_angle += self.balance_angular_velocity * dt

        if abs(self.balance_angle) >= self.BALANCE_MAX_TILT:
            self._start_falling_ball()
        elif self.balance_elapsed >= self.BALANCE_DURATION:
            self.phase = 'caught'
            self.balance_left = False
            self.balance_right = False
            if not self.rewarded:
                game_ui.reward_success()
                self.rewarded = True

    def _start_falling_ball(self):
        direction = 1 if self.balance_angle >= 0 else -1
        self.ball_x = (
            self.nose_x
            + math.sin(self.balance_angle) * self.BALANCE_VISUAL_SHIFT
        )
        self.ball_y = self.nose_y
        self.ball_vx = (
            direction * 95
            + self.balance_angular_velocity * 24
        )
        self.ball_vy = -45
        self.ball_rotation = -math.degrees(self.balance_angle)
        self.miss_reason = 'balance'
        self.accuracy_grade = 'miss'
        self.balance_left = False
        self.balance_right = False
        self.phase = 'falling'

    def _update_falling_ball(self, dt):
        self.ball_vy -= self.GRAVITY * dt
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt
        self.ball_rotation -= math.degrees(
            self.ball_vx / self.BALL_SIZE
        ) * dt
        if self.ball_y <= self.STAGE_GROUND_Y:
            self.ball_y = self.STAGE_GROUND_Y
            self.phase = 'miss'

    def _update_seal_animation(self, dt):
        self.seal_frame_timer += dt
        while self.seal_frame_timer >= 0.18:
            self.seal_frame_timer -= 0.18
            self.seal_frame = (self.seal_frame + 1) % self.seal_columns

    def _draw_accuracy(self):
        if self.accuracy_grade is None:
            return
        source_y, source_height = self.accuracy_sprites[self.accuracy_grade]
        draw_height = (
            self.ACCURACY_DRAW_WIDTH
            * source_height
            / self.accuracy_image.w
        )
        self.accuracy_image.clip_draw(
            0,
            source_y,
            self.accuracy_image.w,
            source_height,
            self.nose_x,
            self.nose_y + 72,
            self.ACCURACY_DRAW_WIDTH,
            draw_height
        )

    def balance_fall_direction(self):
        predicted_tilt = (
            self.balance_angle
            + self.balance_angular_velocity * 0.25
        )
        if abs(predicted_tilt) < 0.035:
            predicted_tilt = self.balance_angular_velocity
        return 1 if predicted_tilt >= 0 else -1

    def _draw_balance_direction(self, x, y, direction):
        start_x = x + direction * 12
        end_x = x + direction * 50
        arrow_y = y + self.BALL_SIZE * 0.72
        color = (255, 133, 48, 255)
        draw_line(start_x, arrow_y, end_x, arrow_y, *color)
        draw_line(start_x, arrow_y + 2, end_x, arrow_y + 2, *color)
        draw_line(
            end_x,
            arrow_y,
            end_x - direction * 11,
            arrow_y + 9,
            *color
        )
        draw_line(
            end_x,
            arrow_y,
            end_x - direction * 11,
            arrow_y - 9,
            *color
        )

    def update_preparation(self, dt):
        if self.phase == 'placing':
            self._update_seal_animation(dt)

    def _segment_target_distance(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            closest_x, closest_y = x1, y1
        else:
            t = (
                (self.nose_x - x1) * dx
                + (self.nose_y - y1) * dy
            ) / length_sq
            t = max(0.0, min(1.0, t))
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy

        distance_sq = (
            (self.nose_x - closest_x) ** 2
            + (self.nose_y - closest_y) ** 2
        )
        return math.sqrt(distance_sq)

    def draw_preparation(self):
        launcher_x = self._preparation_launcher_x()
        preview_launcher_x = (
            self.LAUNCHER_PALETTE_X if launcher_x is None else launcher_x
        )
        seal_front_x = (
            self.SEAL_LEFT_X
            if preview_launcher_x <= self.SCREEN_WIDTH / 2
            else self.SEAL_RIGHT_X
        )
        backstage_seal_x = self.SCREEN_WIDTH - seal_front_x
        self._draw_seal(x=backstage_seal_x, backstage=True)

        if launcher_x is not None:
            self._draw_launcher(
                launcher_x,
                self.LAUNCHER_FLOOR_Y,
                self.LAUNCHER_WIDTH,
                direction=1
            )
        elif self.drag_kind != 'new_launcher':
            self._draw_launcher(
                self.LAUNCHER_PALETTE_X,
                self.LAUNCHER_PALETTE_FLOOR,
                self.LAUNCHER_PALETTE_WIDTH,
                direction=1
            )

        if not self.ball_loaded:
            if self.drag_kind == 'ball':
                self._draw_ball(self.candidate_ball_x, self.candidate_ball_y)
            else:
                self._draw_ball(self.BALL_PALETTE_X, self.BALL_PALETTE_Y, 42)

    def draw_opening(self):
        self._draw_seal()
        self._draw_launcher_scene()

    def draw_performance(self):
        if self.phase == 'aiming':
            self._draw_trajectory()

        self._draw_seal()
        self._draw_launcher_scene()

        if self.phase in ('flying', 'falling', 'miss'):
            self._draw_ball(
                self.ball_x,
                self.ball_y,
                rotation=self.ball_rotation
            )
        elif self.phase in ('balancing', 'caught'):
            tilt = self.balance_angle
            ball_x = self.nose_x + math.sin(tilt) * self.BALANCE_VISUAL_SHIFT
            ball_y = self.nose_y + (math.cos(tilt) - 1) * 8
            self._draw_ball(
                ball_x,
                ball_y,
                rotation=-math.degrees(tilt)
            )
            if self.phase == 'balancing':
                self._draw_balance_direction(
                    ball_x,
                    ball_y,
                    self.balance_fall_direction()
                )
        self._draw_accuracy()
