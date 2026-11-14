
from pico2d import *

# 게임 화면 크기 (16:9)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 게임 실행 여부
running = True

# 배경 이미지
background = None


# 키보드 및 창 종료 이벤트 처리
def handle_events():
    global running

    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            running = False

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False


# 게임 상태 업데이트
def update():
    pass


# 게임 화면 그리기
def draw():
    clear_canvas()

    # 원본 이미지 비율을 유지하며 화면에 출력
    image_ratio = background.w / background.h
    screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT

    if image_ratio > screen_ratio:
        draw_height = SCREEN_HEIGHT
        draw_width = int(draw_height * image_ratio)
    else:
        draw_width = SCREEN_WIDTH
        draw_height = int(draw_width / image_ratio)

    background.draw(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        draw_width,
        draw_height
    )

    update_canvas()


# 메인 함수
def main():
    global running, background

    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)

    # 서커스 무대 이미지 불러오기
    background = load_image(
        'assets/circus_stage_front.png'
    )

    running = True

    # 게임 루프
    while running:
        handle_events()
        update()
        draw()

        delay(0.01)

    close_canvas()


if __name__ == '__main__':
    main()
