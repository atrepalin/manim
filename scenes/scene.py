from manimlib import *


class InteractiveScene(Scene):
    def __init__(self, pausable=False, show_close=False, **kwargs):
        super().__init__(**kwargs)

        self.pausable = pausable
        self.show_close = show_close
        self.paused = False

    def interact(self):
        if self.show_close:
            text = (
                Text("Нажмите Esc чтобы завершить сцену")
                .scale(0.5)
                .to_corner(DOWN + LEFT)
            )
            self.play(Write(text), run_time=0.2)

        super().interact()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == PygletWindowKeys.ENTER:
            self.paused = False
        else:
            super().on_key_press(symbol, modifiers)

    def pause(self):
        if self.pausable:
            self.paused = True

            text = (
                Text("Нажмите Enter чтобы продолжить").scale(0.5).to_corner(DOWN + LEFT)
            )
            self.play(Write(text), run_time=0.2)

            while self.paused:
                self.update_frame(1 / self.camera.fps)

            self.play(FadeOut(text), run_time=0.2)
