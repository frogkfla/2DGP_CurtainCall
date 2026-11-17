
from pico2d import *
import os
import math

from mouse import Mouse
from dialogue import Dialogue
from game_ui import GameUI
from tutorial import Tutorial, TUTORIAL_PERFORMANCE_NAME
from tutorial_prep import TutorialPrep
from dog import DogPerformance
from seal_performance import SealPerformance


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CHAPTER1_PERFORMANCE_NAME = '강아지의 후프 점프'
CHAPTER2_PERFORMANCE_NAME = '물개의 공 받기'
CONTROL_HINT_X = 290
CONTROL_HINT_Y = 96

# 게임 상태
TITLE = 0
READY = 1
OPENING = 2
TUTORIAL = 3
PLAY = 4
TUTORIAL_PREP = 5
TUTORIAL_PLAY = 6
CHAPTER1_INTRO = 7
CHAPTER1_PREP = 8
DOG_OPENING = 9
DOG_PLAY = 10
DOG_READY = 11
SEAL_PREP = 12
SEAL_OPENING = 13
SEAL_PLAY = 14
TUTORIAL_PLATFORM_SURFACE_OFFSET = 2
GREETING_DURATION = 0.9

game_state = TITLE
running = True

# 이미지
title_image = None
ready_image = None
play_image = None
play_open_image = None

curtain_left = None
curtain_right = None

button_normal = None
button_hover = None
button_pressed = None

# 게임 객체
mouse = None
dialogue = None
tutorial = None
tutorial_prep = None
game_ui = None
dog_performance = None
seal_performance = None
guide_font = None
control_dialogue_font = None
mouse_ui_image = None
control_dialogue_image = None
tutorial_end_dialogue = None
dog_prep_dialogue = None
seal_prep_dialogue = None
greeting_active = False
greeting_time = 0.0
greeting_completed = False

# 시작 버튼
BUTTON_X = 640
BUTTON_Y = 140
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 133

is_hover = False
is_pressed = False

# 커튼 애니메이션
opening_time = 0.0
OPENING_DURATION = 2.0
CURTAIN_MOVE_DISTANCE = SCREEN_WIDTH / 2
RIGHT_CURTAIN_Y_OFFSET = 20


def asset_path(*parts):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'assets',
        *parts
    )


def is_mouse_on_button(x, y):
    left = BUTTON_X - BUTTON_WIDTH / 2
    right = BUTTON_X + BUTTON_WIDTH / 2
    bottom = BUTTON_Y - BUTTON_HEIGHT / 2
    top = BUTTON_Y + BUTTON_HEIGHT / 2

    return left <= x <= right and bottom <= y <= top


# --------------------------------------------------
# 이벤트 처리
# --------------------------------------------------

def handle_events():
    global running, game_state
    global is_hover, is_pressed, opening_time
    global greeting_active, greeting_time, greeting_completed
    global dog_performance

    for event in get_events():

        if event.type == SDL_QUIT:
            running = False
            continue

        if event.type == SDL_KEYDOWN:

            if event.key == SDLK_ESCAPE:
                running = False
                continue

            # 무대 뒤 게임 설명
            if game_state == READY:

                if event.key == SDLK_SPACE:
                    dialogue.next()

                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    if dialogue.finished:
                        game_state = TUTORIAL

            # 무대 뒤 UI 설명
            elif game_state == TUTORIAL:

                if event.key == SDLK_SPACE:
                    tutorial.next()

                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    if tutorial.finished:
                        game_state = TUTORIAL_PREP

            # 튜토리얼 공연 준비
            elif game_state == TUTORIAL_PREP:

                if tutorial_prep.completed:

                    if event.key == SDLK_SPACE:
                        tutorial_prep.complete_dialogue.next()

                    elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                        if tutorial_prep.complete_dialogue.finished:
                            opening_time = 0.0
                            game_state = OPENING

            # 튜토리얼 공연 조작
            elif game_state == TUTORIAL_PLAY:
                if greeting_completed:
                    if event.key == SDLK_SPACE:
                        tutorial_end_dialogue.next()
                    elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                        if tutorial_end_dialogue.finished:
                            tutorial_end_dialogue.lines = [
                                '튜토리얼 공연을 멋지게 마쳤어!',
                                '이제부터는 정식 공연을 준비해야 해.',
                                '무대가 어떻게 진행되는지 알았으니 잘 할 수 있겠지?',
                                '좋아, 이제 첫 무대를 장식하러 가보자고!'
                            ]
                            tutorial_end_dialogue.line_index = 0
                            tutorial_end_dialogue.visible_count = 0
                            tutorial_end_dialogue.finished = False
                            tutorial_end_dialogue.char_timer = 0.0
                            tutorial_end_dialogue.finished_hint = 'ENTER : 1장 준비 시작'
                            game_state = CHAPTER1_INTRO
                elif event.key == SDLK_SPACE and not greeting_active:
                    greeting_active = True
                    greeting_time = 0.0

            elif game_state == CHAPTER1_INTRO:
                if event.key == SDLK_SPACE:
                    tutorial_end_dialogue.next()
                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    if tutorial_end_dialogue.finished:
                        game_state = CHAPTER1_PREP

            elif game_state == CHAPTER1_PREP:
                if event.key == SDLK_SPACE:
                    dog_prep_dialogue.next()
                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    if dog_prep_dialogue.finished:
                        if dog_performance.handle_preparation_event(event):
                            opening_time = 0.0
                            game_state = DOG_OPENING

            elif game_state == DOG_READY:
                if event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    dog_performance.start_performance()
                    game_state = DOG_PLAY

            elif game_state == SEAL_PREP:
                if event.key == SDLK_SPACE:
                    seal_prep_dialogue.next()
                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    if seal_prep_dialogue.finished:
                        if seal_performance.handle_preparation_event(event):
                            opening_time = 0.0
                            game_state = SEAL_OPENING

        # 단상 드래그 처리
        if game_state == TUTORIAL_PREP:
            tutorial_prep.handle_event(event)
            continue

        if game_state == CHAPTER1_PREP and dog_performance is not None:
            if event.type != SDL_KEYDOWN:
                dog_performance.handle_preparation_event(event)
            continue

        if game_state == DOG_PLAY and dog_performance is not None:
            if (
                dog_performance.phase == 'result'
                and event.type == SDL_KEYDOWN
                and event.key in (SDLK_RETURN, SDLK_KP_ENTER)
            ):
                game_state = SEAL_PREP
            else:
                dog_performance.handle_performance_event(event)
            continue

        if game_state == SEAL_PREP and seal_performance is not None:
            if event.type != SDL_KEYDOWN:
                seal_performance.handle_preparation_event(event)
            continue

        if game_state == SEAL_PLAY and seal_performance is not None:
            seal_performance.handle_performance_event(event)
            continue

        # 타이틀 화면 이외에는 시작 버튼 이벤트 무시
        if game_state != TITLE:
            continue

        if event.type == SDL_MOUSEMOTION:
            is_hover = is_mouse_on_button(
                event.x,
                SCREEN_HEIGHT - event.y
            )

        elif event.type == SDL_MOUSEBUTTONDOWN:

            if event.button == SDL_BUTTON_LEFT:
                is_hover = is_mouse_on_button(
                    event.x,
                    SCREEN_HEIGHT - event.y
                )
                is_pressed = is_hover

        elif event.type == SDL_MOUSEBUTTONUP:

            if event.button == SDL_BUTTON_LEFT:
                is_hover = is_mouse_on_button(
                    event.x,
                    SCREEN_HEIGHT - event.y
                )

                if is_pressed and is_hover:
                    game_state = READY

                is_pressed = False


# --------------------------------------------------
# 게임 업데이트
# --------------------------------------------------

def update(dt):
    global game_state, opening_time
    global greeting_active, greeting_time, greeting_completed

    if game_state == READY:
        mouse.update()
        dialogue.update(dt)

    elif game_state == TUTORIAL:
        mouse.update()
        tutorial.update(dt)

    elif game_state == TUTORIAL_PREP:
        mouse.update()
        tutorial_prep.update(dt)

    elif game_state == OPENING:
        mouse.update()
        opening_time += dt

        if opening_time >= OPENING_DURATION:
            opening_time = OPENING_DURATION
            game_state = TUTORIAL_PLAY

    elif game_state == PLAY:
        pass

    elif game_state == TUTORIAL_PLAY:
        mouse.update()

        if greeting_active:
            greeting_time += dt
            if greeting_time >= GREETING_DURATION:
                greeting_time = GREETING_DURATION
                greeting_active = False
                greeting_completed = True
                game_ui.reward_success()

        if greeting_completed:
            tutorial_end_dialogue.update(dt)

    elif game_state == CHAPTER1_INTRO:
        mouse.update()
        tutorial_end_dialogue.update(dt)

    elif game_state == CHAPTER1_PREP:
        dog_prep_dialogue.update(dt)
        dog_performance.update_waiting(dt)

    elif game_state == SEAL_PREP:
        seal_prep_dialogue.update(dt)
        seal_performance.update_preparation(dt)

    elif game_state == DOG_OPENING:
        opening_time += dt
        if opening_time >= OPENING_DURATION:
            opening_time = OPENING_DURATION
            dog_performance.wait_for_start()
            game_state = DOG_READY

    elif game_state == DOG_PLAY:
        dog_performance.update_performance(dt, game_ui)

    elif game_state == DOG_READY:
        dog_performance.update_waiting(dt)

    elif game_state == SEAL_OPENING:
        opening_time += dt
        if opening_time >= OPENING_DURATION:
            opening_time = OPENING_DURATION
            seal_performance.begin_aiming()
            game_state = SEAL_PLAY

    elif game_state == SEAL_PLAY:
        seal_performance.update(dt, game_ui)


# --------------------------------------------------
# 화면 그리기
# --------------------------------------------------

def draw_background(image):
    image.draw(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )


def draw_start_button():
    if is_pressed and is_hover:
        image = button_pressed
    elif is_hover:
        image = button_hover
    else:
        image = button_normal

    image.draw(
        BUTTON_X,
        BUTTON_Y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )


def draw_title():
    draw_background(title_image)
    draw_start_button()


def draw_ready():
    draw_background(ready_image)
    mouse.draw()
    dialogue.draw()


def draw_tutorial():
    draw_background(ready_image)
    mouse.draw()
    tutorial.draw(game_ui)


def draw_tutorial_prep():
    draw_background(ready_image)
    game_ui.draw(TUTORIAL_PERFORMANCE_NAME)
    tutorial_prep.draw()
    mouse.draw()
    tutorial_prep.draw_dialogue()


# --------------------------------------------------
# 커튼 애니메이션
# --------------------------------------------------

def smooth_step(progress):
    return progress * progress * (3.0 - 2.0 * progress)


def draw_opening():
    draw_background(play_image)
    game_ui.draw(TUTORIAL_PERFORMANCE_NAME)

    tutorial_prep.image.draw(
        tutorial_prep.target_x,
        tutorial_prep.target_y,
        tutorial_prep.prop_width,
        tutorial_prep.prop_height
    )

    mouse.draw(
        tutorial_prep.target_x,
        tutorial_prep.target_y + TUTORIAL_PLATFORM_SURFACE_OFFSET,
        row=1
    )

    progress = min(opening_time / OPENING_DURATION, 1.0)
    smooth = smooth_step(progress)
    move_distance = CURTAIN_MOVE_DISTANCE * smooth

    left_x = SCREEN_WIDTH / 2 - move_distance
    right_x = SCREEN_WIDTH / 2 + move_distance

    curtain_left.draw(
        left_x,
        SCREEN_HEIGHT / 2,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )

    curtain_right.draw(
        right_x,
        SCREEN_HEIGHT / 2 + RIGHT_CURTAIN_Y_OFFSET,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )


def draw_dog_opening():
    draw_background(play_image)
    game_ui.draw(
        CHAPTER1_PERFORMANCE_NAME,
        chapter='1장',
        subtitle='실전'
    )
    dog_performance.draw_opening()

    progress = min(opening_time / OPENING_DURATION, 1.0)
    smooth = smooth_step(progress)
    move_distance = CURTAIN_MOVE_DISTANCE * smooth
    curtain_left.draw(
        SCREEN_WIDTH / 2 - move_distance,
        SCREEN_HEIGHT / 2,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
    curtain_right.draw(
        SCREEN_WIDTH / 2 + move_distance,
        SCREEN_HEIGHT / 2 + RIGHT_CURTAIN_Y_OFFSET,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )


# --------------------------------------------------
# 무대 앞 공연
# --------------------------------------------------

def draw_play():
    draw_background(play_image)

    tutorial_prep.image.draw(
        tutorial_prep.target_x,
        tutorial_prep.target_y,
        tutorial_prep.prop_width,
        tutorial_prep.prop_height
    )

    game_ui.draw()

    guide_font.draw(
        30,
        500,
        'TUTORIAL PERFORMANCE',
        (255, 245, 210)
    )


def draw_tutorial_play():
    draw_background(play_image)
    game_ui.draw(TUTORIAL_PERFORMANCE_NAME)

    tutorial_prep.image.draw(
        tutorial_prep.target_x,
        tutorial_prep.target_y,
        tutorial_prep.prop_width,
        tutorial_prep.prop_height
    )

    greeting_bob = 0
    if greeting_active:
        progress = greeting_time / GREETING_DURATION
        greeting_bob = math.sin(progress * math.pi) * 18

    mouse.draw(
        tutorial_prep.target_x,
        tutorial_prep.target_y + TUTORIAL_PLATFORM_SURFACE_OFFSET + greeting_bob,
        row=1
    )

    if greeting_completed:
        draw_tutorial_control_bubble(tutorial_end_dialogue)
    else:
        draw_tutorial_control_bubble()


def wrap_control_prompt(text, max_width=170):
    wrapped = []
    for paragraph in text.split('\n'):
        line = ''
        line_width = 0
        for char in paragraph:
            if char == ' ':
                char_width = 5
            elif ord(char) > 127:
                char_width = 16
            else:
                char_width = 9

            if line and line_width + char_width > max_width:
                wrapped.append(line.rstrip())
                line = ''
                line_width = 0

            line += char
            line_width += char_width

        if line:
            wrapped.append(line.rstrip())

    if len(wrapped) > 2:
        wrapped = wrapped[:2]
        second_line = wrapped[1].rstrip()
        while second_line and sum(
            5 if char == ' ' else (16 if ord(char) > 127 else 9)
            for char in second_line
        ) > max_width - 16:
            second_line = second_line[:-1].rstrip()
        wrapped[1] = second_line + '…'

    return wrapped


def draw_tutorial_control_bubble(dialogue_to_show=None, prompt=None, hint=None):
    # 왼쪽 아래 조작 안내 UI
    control_dialogue_image.draw(252, 115, 300, 123)
    mouse_ui_image.draw(75, 72, 120, 80)

    if dialogue_to_show is None:
        prompt_lines = wrap_control_prompt(
            prompt or 'SPACE를 눌러 인사해 봐!'
        )
        first_line_y = 123 + (len(prompt_lines) - 1) * 9
        for i, text_line in enumerate(prompt_lines):
            control_dialogue_font.draw(
                135,
                first_line_y - i * 18,
                text_line,
                (104, 58, 39)
            )
        if hint:
            tutorial_end_dialogue.hint_font.draw(
                CONTROL_HINT_X,
                CONTROL_HINT_Y,
                hint,
                (125, 85, 60)
            )
        return

    visible_text = dialogue_to_show.get_wrapped_text()[:dialogue_to_show.visible_count]
    prompt_lines = wrap_control_prompt(visible_text)
    first_line_y = 123 + (len(prompt_lines) - 1) * 9
    for i, text_line in enumerate(prompt_lines):
        if text_line:
            dialogue_to_show.font.draw(
                135,
                first_line_y - i * 18,
                text_line,
                (104, 58, 39)
            )

    hint = (
        'ENTER : 완료'
        if dialogue_to_show.finished
        else 'SPACE : 계속'
    )
    tutorial_end_dialogue.hint_font.draw(
        CONTROL_HINT_X,
        CONTROL_HINT_Y,
        hint,
        (125, 85, 60)
    )


def draw_chapter1_intro():
    draw_background(ready_image)
    mouse.draw()
    tutorial_end_dialogue.draw()


def draw_chapter1_prep():
    draw_background(ready_image)
    game_ui.draw(
        CHAPTER1_PERFORMANCE_NAME,
        chapter='1장',
        subtitle='실전'
    )
    dog_performance.draw_preparation()
    dog_prep_dialogue.draw()


def draw_dog_play():
    draw_background(play_image)
    game_ui.draw(
        CHAPTER1_PERFORMANCE_NAME,
        chapter='1장',
        subtitle='실전'
    )
    dog_performance.draw_performance()

    if dog_performance.phase == 'result':
        game_ui.draw_stars(dog_performance.star_rating)
        draw_tutorial_control_bubble(
            prompt=f'통과한 후프: {dog_performance.success_count}/{len(dog_performance.hoops)}',
            hint='ENTER : 다음 공연'
        )
    else:
        draw_tutorial_control_bubble(
            prompt='후프 가까이에서 SPACE로 점프!'
        )


def draw_dog_ready():
    draw_background(play_image)
    game_ui.draw(
        CHAPTER1_PERFORMANCE_NAME,
        chapter='1장',
        subtitle='실전'
    )
    dog_performance.draw_performance()
    draw_tutorial_control_bubble(
        prompt='후프 가까이에서 SPACE로 점프!',
        hint='ENTER : 공연 시작'
    )


def draw_seal_prep():
    draw_background(ready_image)
    game_ui.draw(
        CHAPTER2_PERFORMANCE_NAME,
        chapter='2장',
        subtitle='실전'
    )
    seal_performance.draw_preparation()
    seal_prep_dialogue.draw()


def draw_seal_opening():
    draw_background(play_open_image)
    game_ui.draw(
        CHAPTER2_PERFORMANCE_NAME,
        chapter='2장',
        subtitle='실전'
    )
    seal_performance.draw_opening()

    progress = min(opening_time / OPENING_DURATION, 1.0)
    move_distance = CURTAIN_MOVE_DISTANCE * smooth_step(progress)
    curtain_left.draw(
        SCREEN_WIDTH / 2 - move_distance,
        SCREEN_HEIGHT / 2,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
    curtain_right.draw(
        SCREEN_WIDTH / 2 + move_distance,
        SCREEN_HEIGHT / 2 + RIGHT_CURTAIN_Y_OFFSET,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )


def draw_seal_play():
    draw_background(play_open_image)
    game_ui.draw(
        CHAPTER2_PERFORMANCE_NAME,
        chapter='2장',
        subtitle='실전'
    )
    seal_performance.draw_performance()

    if seal_performance.phase == 'aiming':
        draw_tutorial_control_bubble(
            prompt='↑/↓ 각도 조절, SPACE 발사',
            hint=f'{round(seal_performance.launcher_angle)}°'
        )
    elif seal_performance.phase == 'flying':
        draw_tutorial_control_bubble(
            prompt='공이 포물선을 따라 날아가고 있어!'
        )
    elif seal_performance.phase == 'balancing':
        remaining = max(
            0.0,
            seal_performance.BALANCE_DURATION
            - seal_performance.balance_elapsed
        )
        draw_tutorial_control_bubble(
            prompt='←/→를 눌러 공의 균형을 잡아!',
            hint=f'{remaining:.1f}초 버티기'
        )
    elif seal_performance.phase == 'caught':
        draw_tutorial_control_bubble(
            prompt='공을 떨어뜨리지 않고 균형을 잡았어!',
            hint='공연 성공!'
        )
    elif seal_performance.phase == 'falling':
        draw_tutorial_control_bubble(
            prompt='앗, 공이 굴러 떨어지고 있어!'
        )
    elif seal_performance.phase == 'miss':
        prompt = (
            '공이 떨어졌어. 다시 균형을 잡아보자!'
            if seal_performance.miss_reason == 'balance'
            else '빗나갔어. 각도를 바꿔 다시 해보자!'
        )
        draw_tutorial_control_bubble(prompt=prompt, hint='R : 재장전')


# --------------------------------------------------
# 전체 화면 그리기
# --------------------------------------------------

def draw():
    clear_canvas()

    if game_state == TITLE:
        draw_title()

    elif game_state == READY:
        draw_ready()

    elif game_state == TUTORIAL:
        draw_tutorial()

    elif game_state == TUTORIAL_PREP:
        draw_tutorial_prep()

    elif game_state == OPENING:
        draw_opening()

    elif game_state == PLAY:
        draw_play()

    elif game_state == TUTORIAL_PLAY:
        draw_tutorial_play()

    elif game_state == CHAPTER1_INTRO:
        draw_chapter1_intro()

    elif game_state == CHAPTER1_PREP:
        draw_chapter1_prep()

    elif game_state == DOG_OPENING:
        draw_dog_opening()

    elif game_state == DOG_PLAY:
        draw_dog_play()

    elif game_state == DOG_READY:
        draw_dog_ready()

    elif game_state == SEAL_PREP:
        draw_seal_prep()

    elif game_state == SEAL_OPENING:
        draw_seal_opening()

    elif game_state == SEAL_PLAY:
        draw_seal_play()

    update_canvas()


# --------------------------------------------------
# 메인 함수
# --------------------------------------------------

def main():
    global running, game_state
    global title_image, ready_image, play_image, play_open_image
    global curtain_left, curtain_right
    global button_normal, button_hover, button_pressed
    global mouse, dialogue, tutorial, tutorial_prep, game_ui
    global dog_performance, seal_performance
    global guide_font
    global control_dialogue_font
    global mouse_ui_image, control_dialogue_image
    global tutorial_end_dialogue, dog_prep_dialogue, seal_prep_dialogue
    global is_hover, is_pressed, opening_time

    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)

    # 배경 이미지
    title_image = load_image(
        asset_path('background', 'title.png')
    )

    ready_image = load_image(
        asset_path('background', 'circus_stage_back.png')
    )

    play_image = load_image(
        asset_path('background', 'circus_stage_front.png')
    )

    play_open_image = load_image(
        asset_path('background', 'circus_stage_front_open.png')
    )

    # 커튼 이미지
    curtain_left = load_image(
        asset_path('curtains', 'curtain_left_closed.png')
    )

    curtain_right = load_image(
        asset_path('curtains', 'curtain_right_closed.png')
    )

    # 시작 버튼 이미지
    button_normal = load_image(
        asset_path('ui', 'start_button_normal.png')
    )

    button_hover = load_image(
        asset_path('ui', 'start_button_hover.png')
    )

    button_pressed = load_image(
        asset_path('ui', 'start_button_pressed.png')
    )

    mouse_ui_image = load_image(
        asset_path('ui', 'mouse_ui.png')
    )
    control_dialogue_image = load_image(
        asset_path('ui', 'dialogue_flipped.png')
    )

    # 안내 폰트
    guide_font = load_font(
        'C:/Windows/Fonts/arialbd.ttf',
        28
    )
    control_dialogue_font = load_font(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'assets', 'fonts', 'Griun_Fromsol-Rg.ttf'
        ),
        16
    )

    # 게임 객체 생성
    mouse = Mouse()
    dialogue = Dialogue()
    dialogue.finished_hint = 'ENTER : 튜토리얼 시작'
    tutorial = Tutorial()
    tutorial_prep = TutorialPrep()
    game_ui = GameUI()
    dog_performance = DogPerformance()
    seal_performance = SealPerformance()
    tutorial_end_dialogue = Dialogue()
    tutorial_end_dialogue.lines = [
        '멋진 인사였어!',
        '오! 관객이 별 하나를 줬어!',
        '튜토리얼 공연은 여기서 끝이야.',
        '다시 무대 뒤로 돌아가자!'
    ]
    tutorial_end_dialogue.finished_hint = 'ENTER : 튜토리얼 완료'

    dog_prep_dialogue = Dialogue()
    dog_prep_dialogue.lines = [
        '다음 순서인 강아지 공연을 준비해줘!',
        '강아지는 저쪽에서부터 달릴 거야.',
        '강아지가 뛰어넘을 후프를 드래그해 배치해줘.',
        '후프는 최대 5개까지 배치할 수 있어. ',
        '더 많이 성공할수록 좋은 점수를 받을 수 있어. 실패하지 않게 적당히 배치해봐!',
        '배치가 끝나면 ENTER를 눌러 공연을 시작하자!'
    ]
    dog_prep_dialogue.finished_hint = 'ENTER : 공연 시작'

    seal_prep_dialogue = Dialogue()
    seal_prep_dialogue.lines = [
        '다음 공연은 물개가 받기 쉽게 공을 던져주는 거야!',
        '왼쪽 아래 발사대를 무대 위에 놓고, 공을 발사대 입구에 끌어 장전해.',
        '준비가 끝나면 ENTER를 눌러 커튼을 열자!'
    ]
    seal_prep_dialogue.finished_hint = 'ENTER : 공연 준비 완료'

    # 초기 상태
    running = True
    game_state = TITLE

    is_hover = False
    is_pressed = False
    opening_time = 0.0

    # 메인 루프
    last_time = get_time()

    while running:
        current_time = get_time()
        dt = current_time - last_time
        last_time = current_time

        handle_events()
        update(dt)
        draw()

        delay(0.01)

    close_canvas()


if __name__ == '__main__':
    main()
