# Codex Handoff: CurtainCall

Read this file, then inspect the current source before making changes. The live code is authoritative; `PROJECT_CONTEXT.md` is an older summary and may not reflect the current `TUTORIAL_PLAY` state.

## Project

- Game: `무사히, 커튼콜!`, a vintage paper-doll-style circus game.
- Python 3.11, pico2d 1.5.1, 1280x720.
- Main modules: `main.py` (states/events/rendering), `mouse.py` (mouse character), `dialogue.py` (dialogue/typewriter/input hints), `tutorial.py` (UI tutorial), `tutorial_prep.py` (platform placement), `game_ui.py` (title/gauge/stars).

## Current Flow

`TITLE -> READY -> TUTORIAL -> TUTORIAL_PREP -> OPENING -> TUTORIAL_PLAY`

`PLAY` remains a separate placeholder/formal-performance state. `TUTORIAL_PLAY` currently draws the front-stage background, platform, mouse standing on it, and tutorial UI. It is not yet a playable greeting scene.

A previous attempt added a one-shot SPACE greeting animation by editing `main.py` and `mouse.py`; the user later undid those edits. The current source has no SPACE greeting handler or greeting animation. Do not restore that attempt unless requested.

## Current Tutorial Dialogue

The live `tutorial.py` includes the user-edited star explanation:

`별은 지루함 게이지 위쪽에 있어. 별을 많이 받으면 지루함이 줄어들어!`

Keep this wording unless the user asks to change it. Other tutorial messages explain the performance title, boredom gauge, and platform placement.

## UI And State

- `game_ui.py` loads `star2_empty.png` and `star2_fill.png`.
- Star placement is user-adjusted. Current values: center X is based on the gauge left edge plus 25% of its width plus 8px; Y is `gauge_y + gauge_height / 2 - 30`; size is 40px high; gap is 33px.
- The star source images are 1536x1024. `draw_stars` computes width from the source aspect ratio, so each 40px-high star is drawn 60x40. Preserve the aspect ratio and user-adjusted centers/size/gap.
- Gauge geometry: center `(1055, 653)`, `390x130`; fill fractions `0.105` to `0.93`, fill height 70. Do not change without asking.
- Star state starts at `stars = 0`, representing 3 empty slots. `GameUI.draw()` now draws stored stars along with the title and gauge so they persist across UI screens.
- `GameUI.reward_success()` takes no arguments; each call fills one slot, caps at 3, and reduces boredom by 5. There are currently no mission-completion call sites. When missions are implemented, call it once per completed mission and prevent repeat rewards for the same mission.
- `Tutorial.draw()` has temporary star-count demos using `draw_stars(count)`; these are visual demonstrations and do not update persistent `self.stars`.

## Fonts

Project fonts are in `assets/fonts/` and are loaded from there:

- Dialogue body: `Griun_Fromsol-Rg.ttf`
- Character name and boredom label: `Hakgyoansim Dunggeunmiso TTF B.ttf`
- SPACE/ENTER hints: `Hakgyoansim Dunggeunmiso TTF R.ttf`
- Performance title: `[KIM]WILDgag-BOLD.ttf`

The requested title font `[KIMJW] Dgag-BOLD.ttf` was not present; `[KIM]WILDgag-BOLD.ttf` is the available substitute. The Dunggeunmiso filenames use this spelling in the assets folder. Existing font sizes and UI positions were retained. A Windows-rendered Korean sample and game initialization were previously checked.

## Fixed Layout Values

Preserve these hand-tuned values unless the user asks to change them:

- Backstage mouse: `(1175, 285)`, rendered `82x105`.
- Platform: start `(250, 260)`, target `(640, 260)`, rendered `300x200`, snap tolerance 80.
- Platform-standing mouse foot Y: target platform center Y plus 2.
- Curtain right-side Y offset: +20; opening duration: 2 seconds.
- Dialogue panel: center `(870, 500)`, `608x232`; current text placement/line spacing is hand-tuned.
- Performance title UI: center `(160, 670)`, `240x80`.

## Working Rules

- Implement one requested feature at a time; inspect actual files before editing.
- Preserve user-tuned coordinates, dimensions, dialogue, and existing behavior.
- Do not undo user changes. The user sometimes reverts specific edits; check current files before relying on conversation history.
- Do not implement later roadmap items without request.
- Validate after each edit. The game has been launched successfully with the active Python 3.13 environment; `python main.py` should reach `Pico2d is prepared.` and continue running.
- Do not create commits. Provide a suggested Git commit message after a completed step; only commit if the user explicitly asks.
