
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

# 커튼 이미지
curtain_left = None
curtain_right = None

# 시작 버튼 이미지
button_normal = None
button_hover = None
button_pressed = None

# 캐릭터 및 대사
mouse = None
dialogue = None
guide_font = None

# 시작 버튼 위치 및 크기
BUTTON_X = 640
BUTTON_Y = 140
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 133

is_hover = False
is_pressed = False

# 커튼 애니메이션
opening_time = 0.0
OPENING_DURATION = 2.0

# 커튼이 좌우로 이동하는 거리
CURTAIN_MOVE_DISTANCE = SCREEN_WIDTH / 2


# 이미지 경로
def asset_path(*parts):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'assets',
        *parts
    )


# 시작 버튼 영역 판정
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

            # ESC: 종료
            if event.key == SDLK_ESCAPE:
                running = False
                continue

            # READY 상태에서만 대사 및 Enter 처리
            if game_state == READY:

                # Space: 대사 진행
                if event.key == SDLK_SPACE:
                    dialogue.next()

                # Enter: 대사가 끝난 후 커튼 열기
                elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):

                    if dialogue.finished:
                        opening_time = 0.0
                        game_state = OPENING

        # 타이틀 화면에서만 마우스 처리
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

    # 생쥐 단장 대사 화면
    if game_state == READY:
        mouse.update()
        dialogue.update(dt)

    # 커튼 열림 애니메이션
    elif game_state == OPENING:
        opening_time += dt

        if opening_time >= OPENING_DURATION:
            opening_time = OPENING_DURATION
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

    # 기존 무대 뒤 배경만 출력
    draw_background(ready_image)

    # 생쥐 단장
    mouse.draw()

    # 말풍선 및 대사
    dialogue.draw()


# 부드러운 움직임 계산
def smooth_step(progress):
    return progress * progress * (3.0 - 2.0 * progress)


# 커튼 열림 애니메이션
def draw_opening():

    # 무대 앞 배경
    draw_background(play_image)

    # 애니메이션 진행률
    progress = min(
        opening_time / OPENING_DURATION,
        1.0
    )

    # 부드러운 가속 및 감속
    smooth = smooth_step(progress)

    # 커튼 이동 거리
    move_distance = CURTAIN_MOVE_DISTANCE * smooth

    # 왼쪽 커튼 위치
    left_x = SCREEN_WIDTH / 2 - move_distance

    # 오른쪽 커튼 위치
    right_x = SCREEN_WIDTH / 2 + move_distance

    # 왼쪽 커튼 출력
    curtain_left.draw(
        left_x,
        SCREEN_HEIGHT / 2,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )

    # 오른쪽 커튼 출력
    curtain_right.draw(
        right_x,
        SCREEN_HEIGHT / 2 + 20,
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )


# 공연 진행 화면
def draw_play():

    # 커튼 없이 무대 앞 배경만 출력
    draw_background(play_image)

    guide_font.draw(
        30,
        660,
        'PLAY - PERFORMANCE STARTED',
        (255, 245, 210)
    )


# 전체 화면 출력
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
    global curtain_left, curtain_right
    global button_normal, button_hover, button_pressed
    global mouse, dialogue, guide_font
    global is_hover, is_pressed, opening_time

    # 게임 창 생성
    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)

    # 타이틀 배경
    title_image = load_image(
        asset_path('background', 'title.png')
    )

    # 무대 뒤 배경
    ready_image = load_image(
        asset_path('background', 'circus_stage_back.png')
    )

    # 무대 앞 배경
    play_image = load_image(
        asset_path('background', 'circus_stage_front.png')
    )

    # 왼쪽 커튼
    curtain_left = load_image(
        asset_path('curtains', 'curtain_left_closed.png')
    )

    # 오른쪽 커튼
    curtain_right = load_image(
        asset_path('curtains', 'curtain_right_closed.png')
    )

    # 시작 버튼
    button_normal = load_image(
        asset_path('ui', 'start_button_normal.png')
    )

    button_hover = load_image(
        asset_path('ui', 'start_button_hover.png')
    )

    button_pressed = load_image(
        asset_path('ui', 'start_button_pressed.png')
    )

    # 안내 폰트
    guide_font = load_font(
        'C:/Windows/Fonts/arialbd.ttf',
        28
    )

    # 생쥐 단장
    mouse = Mouse()

    # 대사
    dialogue = Dialogue()

    # 초기화
    running = True
    game_state = TITLE
    is_hover = False
    is_pressed = False
    opening_time = 0.0

    # 게임 시간
    last_time = get_time()

    # 메인 루프
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
