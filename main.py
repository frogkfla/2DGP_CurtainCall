
from pico2d import *
import os

from mouse import Mouse
from dialogue import Dialogue
from game_ui import GameUI
from tutorial import Tutorial, TUTORIAL_PERFORMANCE_NAME
from tutorial_prep import TutorialPrep


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 게임 상태
TITLE = 0
READY = 1
OPENING = 2
TUTORIAL = 3
PLAY = 4
TUTORIAL_PREP = 5
TUTORIAL_PLAY = 6
TUTORIAL_PLATFORM_SURFACE_OFFSET = 2

game_state = TITLE
running = True

# 이미지
title_image = None
ready_image = None
play_image = None

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
guide_font = None
control_hint_font = None
mouse_ui_image = None
control_dialogue_image = None

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

        # 단상 드래그 처리
        if game_state == TUTORIAL_PREP:
            tutorial_prep.handle_event(event)
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
        tutorial_prep.target_y + TUTORIAL_PLATFORM_SURFACE_OFFSET
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

    mouse.draw(
        tutorial_prep.target_x,
        tutorial_prep.target_y + TUTORIAL_PLATFORM_SURFACE_OFFSET
    )

    # 왼쪽 아래 조작 안내 UI
    control_dialogue_image.draw(252, 115, 300, 123)
    mouse_ui_image.draw(75, 72, 120, 80)
    control_hint_font.draw(
        143,
        123,
        'SPACE : 인사하기',
        (104, 58, 39)
    )


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

    update_canvas()


# --------------------------------------------------
# 메인 함수
# --------------------------------------------------

def main():
    global running, game_state
    global title_image, ready_image, play_image
    global curtain_left, curtain_right
    global button_normal, button_hover, button_pressed
    global mouse, dialogue, tutorial, tutorial_prep, game_ui
    global guide_font, control_hint_font
    global mouse_ui_image, control_dialogue_image
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
    control_hint_font = load_font(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'assets', 'fonts', 'Hakgyoansim Dunggeunmiso TTF B.ttf'
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
