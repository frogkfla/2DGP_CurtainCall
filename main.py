
from pico2d import *
import os

from mouse import Mouse
from dialogue import Dialogue
from game_ui import GameUI
from tutorial import Tutorial


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

TITLE = 0
READY = 1
OPENING = 2
TUTORIAL = 3
PLAY = 4

game_state = TITLE
running = True

title_image = None
ready_image = None
play_image = None

curtain_left = None
curtain_right = None

button_normal = None
button_hover = None
button_pressed = None

mouse = None
dialogue = None
tutorial = None
game_ui = None
guide_font = None

BUTTON_X = 640
BUTTON_Y = 140
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 133

is_hover = False
is_pressed = False

opening_time = 0.0
OPENING_DURATION = 2.0
CURTAIN_MOVE_DISTANCE = SCREEN_WIDTH / 2

# 오른쪽 커튼만 조금 위로 조정
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

            if game_state == READY:

                if event.key == SDLK_SPACE:
                    dialogue.next()

                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    if dialogue.finished:
                        opening_time = 0.0
                        game_state = OPENING

            elif game_state == TUTORIAL:

                if event.key == SDLK_SPACE:
                    tutorial.next()

                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                    if tutorial.finished:
                        game_state = PLAY

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


def update(dt):
    global game_state, opening_time

    if game_state == READY:
        mouse.update()
        dialogue.update(dt)

    elif game_state == OPENING:
        opening_time += dt

        if opening_time >= OPENING_DURATION:
            opening_time = OPENING_DURATION
            game_state = TUTORIAL

    elif game_state == TUTORIAL:
        mouse.update()
        tutorial.update(dt)

    elif game_state == PLAY:
        # 실제 공연 시스템은 2주차에 구현
        pass


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
    # 기존 무대 뒤 화면 유지
    draw_background(ready_image)
    mouse.draw()
    dialogue.draw()


def smooth_step(progress):
    return progress * progress * (3.0 - 2.0 * progress)


def draw_opening():
    # 기존 무대 앞 배경 및 커튼 열림 유지
    draw_background(play_image)

    progress = min(
        opening_time / OPENING_DURATION,
        1.0
    )

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


def draw_tutorial():
    # 커튼이 열린 무대 앞에서 튜토리얼 진행
    draw_background(play_image)

    # 생쥐 단장과 기존 말풍선 활용
    mouse.draw()
    tutorial.draw(game_ui)


def draw_play():
    draw_background(play_image)

    # 공연명 및 누적 지루함 게이지
    game_ui.draw()

    # 2주차 공연 구현 전 임시 안내
    guide_font.draw(
        30,
        500,
        'PLAY - PERFORMANCE STARTED',
        (255, 245, 210)
    )


def draw():
    clear_canvas()

    if game_state == TITLE:
        draw_title()

    elif game_state == READY:
        draw_ready()

    elif game_state == OPENING:
        draw_opening()

    elif game_state == TUTORIAL:
        draw_tutorial()

    elif game_state == PLAY:
        draw_play()

    update_canvas()


def main():
    global running, game_state
    global title_image, ready_image, play_image
    global curtain_left, curtain_right
    global button_normal, button_hover, button_pressed
    global mouse, dialogue, tutorial, game_ui
    global guide_font, is_hover, is_pressed, opening_time

    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)

    title_image = load_image(
        asset_path('background', 'title.png')
    )

    ready_image = load_image(
        asset_path('background', 'circus_stage_back.png')
    )

    play_image = load_image(
        asset_path('background', 'circus_stage_front.png')
    )

    curtain_left = load_image(
        asset_path('curtains', 'curtain_left_closed.png')
    )

    curtain_right = load_image(
        asset_path('curtains', 'curtain_right_closed.png')
    )

    button_normal = load_image(
        asset_path('ui', 'start_button_normal.png')
    )

    button_hover = load_image(
        asset_path('ui', 'start_button_hover.png')
    )

    button_pressed = load_image(
        asset_path('ui', 'start_button_pressed.png')
    )

    guide_font = load_font(
        'C:/Windows/Fonts/arialbd.ttf',
        28
    )

    mouse = Mouse()
    dialogue = Dialogue()
    tutorial = Tutorial()
    game_ui = GameUI()

    running = True
    game_state = TITLE

    is_hover = False
    is_pressed = False
    opening_time = 0.0

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
