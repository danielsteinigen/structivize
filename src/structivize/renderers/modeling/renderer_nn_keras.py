import json
from collections import defaultdict

import keras
from keras.utils import plot_model

from ...renderer import Renderer, StatisticResponse
from ...utils import load_json


@Renderer.register("nn_keras")
class RendererNnKeras(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netron": {},
        "keras": {},
    }
    FILE_EXT = "json"

    def preprocess_code(self):
        self._clean_code_lines("{")
        self._code = self._code.strip()

    def _render_netron(self):
        self._execute_process(commands=["netron_export", "--output", f"{self.filepath_image}.svg", self._filepath_code])
        self._svg_save(self.filepath_image)

    def _render_keras(self):
        try:
            json_config = load_json(self._filepath_code)
            if "module" not in json_config:
                json_config["module"] = "keras.src"
            model = keras.models.model_from_json(json.dumps(json_config))
            plot_model(
                model,
                to_file=f"{self.filepath_image}.png",
                show_shapes=True,
                show_layer_names=True,
                show_dtype=True,
                expand_nested=True,
                show_layer_activations=True,
                show_trainable=True,
                dpi=200,
            )
        except Exception as e:
            print("model_from_json failed, trying from_config")
            json_config = load_json(self._filepath_code)
            model = keras.Model.from_config(json_config)
            plot_model(
                model,
                to_file=f"{self.filepath_image}.png",
                show_shapes=True,
                show_layer_names=True,
                show_dtype=True,
                expand_nested=True,
                show_layer_activations=True,
                show_trainable=True,
                dpi=200,
            )

    def statistics(self) -> StatisticResponse:
        counts = defaultdict(int)
        try:
            model = json.loads(self._code)
            config = model.get("config", {})
            layers = config.get("layers", []) if isinstance(config, dict) else config
            for layer in layers:
                layer_type = layer.get("class_name", "Unknown")
                counts[layer_type] += 1
        except Exception as e:
            return StatisticResponse()
        return StatisticResponse(node_types={k: v for k, v in dict(counts).items() if "input" not in k.lower()})
