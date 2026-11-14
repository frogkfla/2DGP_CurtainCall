
from pico2d import *

# 게임 화면 크기
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

running = True


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

    # 추후 배경, 캐릭터, UI 등을 그릴 위치

    update_canvas()


# 메인 함수
def main():
    global running

    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)

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
