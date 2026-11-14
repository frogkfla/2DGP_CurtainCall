from pico2d import *

# 게임 화면 크기
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def main():
    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True

    # 게임 루프
    while running:
        # 키보드 및 창 종료 이벤트 처리
        for event in get_events():
            if event.type == SDL_QUIT:
                running = False

            elif event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    running = False

        # 화면 갱신
        clear_canvas()
        update_canvas()

        # CPU 과도 사용 방지
        delay(0.01)

    close_canvas()


if __name__ == '__main__':
    main()
