from typing import Type
from manimlib import Window, Scene
from manimlib.config import manim_config

def run(cls: Type[Scene], *args, skip_animations=False, **kwargs):
    d = {
        "show_animation_progress": False,
        "leave_progress_bars": False,
        "preview_while_skipping": True,
        "default_wait_time": 1.0,
        "camera_config": {},
        "file_writer_config": {},
        "skip_animations": skip_animations,
        "start_at_animation_number": None,
        "end_at_animation_number": None,
        "presenter_mode": False,
        "window": Window(**manim_config.window),
    }

    scene: Scene = cls(*args, **kwargs, **d)

    scene.run()