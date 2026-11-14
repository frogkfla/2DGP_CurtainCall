
from pico2d import *
import os

# 게임 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 게임 상태
TITLE = 0
READY = 1
PLAY = 2

game_state = TITLE
running = True

# 이미지 및 폰트
title_image = None
stage_image = None

button_normal = None
button_hover = None
button_pressed = None

guide_font = None

# 버튼 위치 및 크기
BUTTON_X = 640
BUTTON_Y = 140
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 133

# 버튼 상태
is_hover = False
is_pressed = False


# 이미지 파일 경로
def asset_path(*parts):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'assets',
        *parts
    )


# 마우스가 버튼 안에 있는지 확인
def is_mouse_on_button(x, y):
    left = BUTTON_X - BUTTON_WIDTH // 2
    right = BUTTON_X + BUTTON_WIDTH // 2
    bottom = BUTTON_Y - BUTTON_HEIGHT // 2
    top = BUTTON_Y + BUTTON_HEIGHT // 2

    return left <= x <= right and bottom <= y <= top


# 키보드 및 마우스 이벤트 처리
def handle_events():
    global running, game_state
    global is_hover, is_pressed

    events = get_events()

    for event in events:
        # 창 닫기
        if event.type == SDL_QUIT:
            running = False

        # 키보드 입력
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False

            elif event.key == SDLK_SPACE:
                if game_state == READY:
                    game_state = PLAY

        # 타이틀 화면에서만 마우스 버튼 처리
        if game_state != TITLE:
            continue

        # 마우스 이동
        if event.type == SDL_MOUSEMOTION:
            mouse_x = event.x
            mouse_y = SCREEN_HEIGHT - event.y

            is_hover = is_mouse_on_button(mouse_x, mouse_y)

        # 마우스 왼쪽 버튼 누르기
        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                mouse_x = event.x
                mouse_y = SCREEN_HEIGHT - event.y

                is_hover = is_mouse_on_button(mouse_x, mouse_y)

                if is_hover:
                    is_pressed = True

        # 마우스 왼쪽 버튼 놓기
        elif event.type == SDL_MOUSEBUTTONUP:
            if event.button == SDL_BUTTON_LEFT:
                mouse_x = event.x
                mouse_y = SCREEN_HEIGHT - event.y

                is_hover = is_mouse_on_button(mouse_x, mouse_y)

                if is_pressed and is_hover:
                    game_state = READY

                is_pressed = False


# 게임 상태 업데이트
def update():
    pass


# 배경 이미지 출력
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
    draw_background(stage_image)

    guide_font.draw(
        30, 660,
        'READY - PRESS SPACE TO START',
        (255, 245, 210)
    )


# 공연 진행 화면
def draw_play():
    draw_background(stage_image)

    guide_font.draw(
        30, 660,
        'PLAY - PERFORMANCE STARTED',
        (255, 245, 210)
    )


# 게임 화면 그리기
def draw():
    clear_canvas()

    if game_state == TITLE:
        draw_title()

    elif game_state == READY:
        draw_ready()

    elif game_state == PLAY:
        draw_play()

    update_canvas()


# 메인 함수
def main():
    global running, game_state
    global title_image, stage_image
    global button_normal, button_hover, button_pressed
    global guide_font
    global is_hover, is_pressed

    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)

    # 배경 이미지 로딩
    title_image = load_image(
        asset_path('background', 'title.png')
    )

    stage_image = load_image(
        asset_path('background', 'circus_stage_front.png')
    )

    # 버튼 이미지 로딩
    button_normal = load_image(
        asset_path('ui', 'start_button_normal.png')
    )

    button_hover = load_image(
        asset_path('ui', 'start_button_hover.png')
    )

    button_pressed = load_image(
        asset_path('ui', 'start_button_pressed.png')
    )

    # 안내 문구 폰트
    guide_font = load_font(
        'C:/Windows/Fonts/arialbd.ttf', 28
    )

    # 초기 상태
    running = True
    game_state = TITLE
    is_hover = False
    is_pressed = False

    # 게임 루프
    while running:
        handle_events()
        update()
        draw()

        delay(0.01)

    close_canvas()


if __name__ == '__main__':
    main()
