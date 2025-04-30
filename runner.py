from typing import Type
from manimlib import Window, Scene
from manimlib.config import manim_config
import copy


def run(cls: Type[Scene], *args, skip_animations=False, render_to_file=False, **kwargs):

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
    }

    if render_to_file:

        pre_config = copy.deepcopy(d)
        pre_config["file_writer_config"]["write_to_movie"] = False
        pre_config["file_writer_config"]["save_last_frame"] = False
        pre_config["file_writer_config"]["quiet"] = True
        pre_config["skip_animations"] = True
        pre_scene = cls(*args, **kwargs, **pre_config)
        pre_scene.run()
        total_time = pre_scene.time - pre_scene.skip_time

        d["file_writer_config"]["total_frames"] = int(
            total_time * manim_config.camera.fps
        )
        d["file_writer_config"]["write_to_movie"] = True
    else:
        window = Window(**manim_config.window)
        d["window"] = window

    scene: Scene = cls(*args, **kwargs, **d)

    try:
        scene.run()
    except Exception as e:
        print("[ERROR]", e)
        raise e
    finally:
        if "window" in d and (window := d["window"]):
            window.close()
