
from pico2d import *
import os

from mouse import Mouse
from dialogue import Dialogue


# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 게임 상태
TITLE = 0
READY = 1
OPENING = 2
PLAY = 3

game_state = TITLE
running = True

# 배경 이미지
title_image = None
ready_image = None
play_image = None

# 버튼 이미지
button_normal = None
button_hover = None
button_pressed = None

# 캐릭터 및 대사
mouse = None
dialogue = None
guide_font = None

# 시작 버튼
BUTTON_X = 640
BUTTON_Y = 140
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 133

is_hover = False
is_pressed = False

# 커튼 전환 시간
opening_time = 0.0
OPENING_DURATION = 1.4


# 이미지 경로
def asset_path(*parts):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'assets',
        *parts
    )


# 버튼 영역 판정
def is_mouse_on_button(x, y):
    left = BUTTON_X - BUTTON_WIDTH / 2
    right = BUTTON_X + BUTTON_WIDTH / 2
    bottom = BUTTON_Y - BUTTON_HEIGHT / 2
    top = BUTTON_Y + BUTTON_HEIGHT / 2

    return left <= x <= right and bottom <= y <= top


# 이벤트 처리
def handle_events():
    global running, game_state
    global is_hover, is_pressed, opening_time

    for event in get_events():

        # 창 닫기
        if event.type == SDL_QUIT:
            running = False
            continue

        # 키보드 입력
        if event.type == SDL_KEYDOWN:

            if event.key == SDLK_ESCAPE:
                running = False
                continue

            if game_state == READY:

                # Space: 대사 진행
                if event.key == SDLK_SPACE:
                    dialogue.next()

                # Enter: 커튼 열기
                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):

                    if dialogue.finished:
                        opening_time = 0.0
                        game_state = OPENING

        # TITLE 상태에서만 버튼 처리
        if game_state != TITLE:
            continue

        # 마우스 이동
        if event.type == SDL_MOUSEMOTION:
            is_hover = is_mouse_on_button(
                event.x,
                SCREEN_HEIGHT - event.y
            )

        # 마우스 왼쪽 버튼 누르기
        elif event.type == SDL_MOUSEBUTTONDOWN:

            if event.button == SDL_BUTTON_LEFT:
                is_hover = is_mouse_on_button(
                    event.x,
                    SCREEN_HEIGHT - event.y
                )

                is_pressed = is_hover

        # 마우스 왼쪽 버튼 놓기
        elif event.type == SDL_MOUSEBUTTONUP:

            if event.button == SDL_BUTTON_LEFT:
                is_hover = is_mouse_on_button(
                    event.x,
                    SCREEN_HEIGHT - event.y
                )

                if is_pressed and is_hover:
                    game_state = READY

                is_pressed = False


# 게임 업데이트
def update(dt):
    global game_state, opening_time

    if game_state == READY:
        mouse.update()
        dialogue.update(dt)

    elif game_state == OPENING:
        opening_time += dt

        if opening_time >= OPENING_DURATION:
            opening_time = OPENING_DURATION
            play_image.opacify(1.0)
            game_state = PLAY


# 배경 출력
def draw_background(image):
    image.draw(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )


# 시작 버튼 출력
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


# 타이틀 화면
def draw_title():
    draw_background(title_image)
    draw_start_button()


# 공연 준비 화면
def draw_ready():
    draw_background(ready_image)
    mouse.draw()
    dialogue.draw()


# 커튼 전환 효과
def draw_opening():
    # 닫힌 커튼 배경
    draw_background(ready_image)

    # 진행률 0.0 ~ 1.0
    progress = min(
        opening_time / OPENING_DURATION,
        1.0
    )

    # 열린 무대를 점점 선명하게 표시
    play_image.opacify(progress)
    draw_background(play_image)


# 공연 진행 화면
def draw_play():
    play_image.opacify(1.0)
    draw_background(play_image)

    guide_font.draw(
        30,
        660,
        'PLAY - PERFORMANCE STARTED',
        (255, 245, 210)
    )


# 화면 출력
def draw():
    clear_canvas()

    if game_state == TITLE:
        draw_title()

    elif game_state == READY:
        draw_ready()

    elif game_state == OPENING:
        draw_opening()

    elif game_state == PLAY:
        draw_play()

    update_canvas()


# 메인 함수
def main():
    global running, game_state
    global title_image, ready_image, play_image
    global button_normal, button_hover, button_pressed
    global mouse, dialogue, guide_font
    global is_hover, is_pressed

    # 게임 창 생성
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

    # 폰트
    guide_font = load_font(
        'C:/Windows/Fonts/arialbd.ttf',
        28
    )

    # 캐릭터 및 대사
    mouse = Mouse()
    dialogue = Dialogue()

    # 초기 상태
    running = True
    game_state = TITLE
    is_hover = False
    is_pressed = False

    # 게임 시간
    last_time = get_time()

    # 게임 루프
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
