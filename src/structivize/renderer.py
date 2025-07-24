import os
import subprocess
from abc import ABC
from pathlib import Path
from typing import List, Literal

import cairosvg
import matplotlib.pyplot as plt
import PyPDF2
from pydantic import BaseModel

from .image_utils import is_image_mainly_black, is_image_single_color, is_image_valid, resize_png_preserve_aspect
from .utils import check_dirs, load_text, remove_files, save_text


class RenderResponse(BaseModel):
    tool: str
    success: bool
    debug_message: str
    path_code: str
    path_image: str
    path_log: str


class Renderer(ABC):
    registry = {}
    DEFAULT_TOOL_CONFIGS = {}

    @classmethod
    def register(cls, name):
        def decorator(subclass):
            cls.registry[name] = subclass
            return subclass

        return decorator

    @classmethod
    def from_dict(cls, renderer: str, code: str, filepath_code: str, filepath_image: str):
        renderer_cls = cls.registry.get(renderer)
        if renderer_cls is None:
            raise ValueError(f"Unknown renderer: {renderer}")
        return renderer_cls(code=code, filepath_code=filepath_code, filepath_image=filepath_image)

    def __init__(
        self,
        code: str = None,
        code_path: str = None,
        output_base_path: str = None,
        output_format: Literal["svg", "pdf", "png", "jpg"] = "png",
        max_width: int = 1024,
        max_height: int = 768,
        tool_configs: dict = None,
    ):
        self._tool_path = os.getenv("TOOL_PATH", ".")

        if output_base_path is None:
            output_base_path = Path.cwd() / "output"
        elif len(str(output_base_path).split(".")) > 1:
            output_base_path = Path(str(output_base_path).split(".")[0])
        else:
            output_base_path = Path(output_base_path)
        check_dirs(output_base_path)

        if code is None:
            if code_path is None or not os.path.isfile(code_path):
                raise ValueError("Either 'code' or valid 'code_path' must be provided.")
            else:
                self._code = load_text(code_path)
        else:
            self._code = code

        self._filepath_code = f"{output_base_path}_code.txt"
        check_dirs(self._filepath_code)
        self.preprocess_code()
        save_text(filename=self._filepath_code, data=self._code)

        self.output_format = output_format
        self._max_width = max_width  # 1024 # 2048
        self._max_height = max_height  # 768 # 1536
        self.__save_svg = False
        self.__save_pdf = False
        self._image_transparent = False

        self.tools = list(self.DEFAULT_TOOL_CONFIGS.keys())

        self._filepath_images = {tool: f"{output_base_path}_{tool}" for tool in self.tools}
        self._log_files = {tool: f"{output_base_path}_{tool}.log" for tool in self.tools}
        self._logs = {tool: {"log": ""} for tool in self.tools}
        self._tool_handlers = {tool: getattr(self, f"_render_{tool}") for tool in self.tools}
        for tool in self.tools:
            if not hasattr(self, f"_render_{tool}"):
                raise NotImplementedError(f"{self.__class__.__name__} must define _render_{tool}()")

        # Merge default configs with provided tool_configs
        self.tool_configs = self._merge_tool_configs(tool_configs or {})

    def _merge_tool_configs(self, custom_configs):
        merged_configs = {}
        for tool, default_config in self.DEFAULT_TOOL_CONFIGS.items():
            # Start with default config, update with any overrides from user
            merged_configs[tool] = {**default_config, **custom_configs.get(tool, {})}
        return merged_configs

    def __write_log(self, command, status, stdout, stderr):
        if self.log is not None:
            self.log["log"] += "\n<<<<<< RENDERING STEP START >>>>>>\n"
            self.log["log"] += f"$ {' '.join(command)}\n"
            self.log["log"] += f"------ EXIT CODE: {status} ------\n"
            self.log["log"] += "---- STDOUT ----\n"
            self.log["log"] += stdout if stdout.strip() else "(no output)\n"
            self.log["log"] += "---- STDERR ----\n"
            self.log["log"] += stderr if stderr.strip() else "(no errors)\n"
            self.log["log"] += "<<<<<< RENDERING STEP END >>>>>>\n"

    def _execute_process(self, commands: list):
        prog = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = prog.communicate()
        status = prog.wait()
        self.__write_log(commands, status, out, err)
        return status, out, err

    def _pdf_save(self, path: str):
        pdf_path = f"{path}.pdf"
        if path is None or not os.path.isfile(pdf_path):
            self.__write_log(["converting PDF"], "failed", "", "PDF was not generated")
        else:
            with open(pdf_path, "rb") as file:
                pdfReader = PyPDF2.PdfReader(file)
                if len(pdfReader.pages) == 1:
                    self._execute_process(commands=["pdfcrop", "-margin", "10", pdf_path, f"{path}-tmp.pdf"])
                    os.rename(f"{path}-tmp.pdf", pdf_path)

                    self._execute_process(commands=["convert", "-density", "500", "-alpha", "off", pdf_path, f"PNG24:{path}.png"])
                    # -alpha set/on/tansparent/off/remove
                    if self.__save_svg:
                        self._execute_process(commands=["pdf2svg", pdf_path, f"{path}.svg"])
                    if not self.__save_pdf:
                        remove_files(path, ["pdf"])

    def _svg_save(self, path: str, svg_code: str = None, scale: float = 2.0):
        svg_path = f"{path}.svg"
        if svg_code is not None:
            open(svg_path, "w").write(svg_code)
            cairosvg.svg2png(bytestring=svg_code, write_to=f"{path}.png", scale=scale, dpi=300)
            if self.__save_pdf:
                cairosvg.svg2pdf(bytestring=svg_code, write_to=f"{path}.pdf")
            if not self.__save_svg:
                remove_files(path, ["svg"])
        else:
            if path is None or not os.path.isfile(svg_path):
                self.__write_log(["converting SVG"], "failed", "", "SVG was not generated")
            else:
                # self._execute_process(commands=["convert", "-density", "500", "-alpha", "off", svg_path, f"PNG24:{path}.png"])
                cairosvg.svg2png(url=svg_path, write_to=f"{path}.png", scale=scale, dpi=300)
                if self.__save_pdf:
                    # self._execute_process(commands=["convert", "-density", "500", svg_path, f"{path}.pdf"])
                    cairosvg.svg2pdf(url=svg_path, write_to=f"{path}.pdf")
                if not self.__save_svg:
                    remove_files(svg_path)

    def _validate_image(self, path_img):
        if not os.path.isfile(path_img):
            return ""
        elif not is_image_valid(path_img) or is_image_single_color(path_img):
            os.remove(path_img)
            return ""
        elif type(self).__name__ == "RendererModelingPlantuml" and is_image_mainly_black(path_img):
            os.remove(path_img)
            return ""
        resize_png_preserve_aspect(path_img, self._max_width, self._max_height, keep_transparency=self._image_transparent)
        return path_img

    def _write_response(self, success: bool = True, message: str = "") -> RenderResponse:
        if self._logs[self._current_tool]["log"] != "":
            save_text(filename=f"{self._filepath_images[self._current_tool]}.log", data=self._logs[self._current_tool]["log"])

        path_img = self._validate_image(f"{self._filepath_images[self._current_tool]}.png")
        print(f"{self._filepath_images[self._current_tool]} - {'success' if path_img != '' else 'fail'}")
        return RenderResponse(
            tool=self._current_tool,
            success=success,
            debug_message=message,
            path_code=f"{self._filepath_code}",
            path_image=f"{path_img}",
            path_log=f"{self._filepath_images[self._current_tool]}.log",
        )

    def preprocess_code(self):
        self._code = self._code.strip()

    def verify_code(self):
        return self._code.strip() != ""

    def render_all(self) -> List[RenderResponse]:
        response = []
        for tool in self.tools:
            if tool not in self._tool_handlers:
                raise ValueError(f"Tool '{tool}' not supported by {type(self).__name__}")
            response.append(self._execute_tool(tool))
        return response

    def render(self, tool: str = None) -> RenderResponse:
        if not tool:
            tool = self.tools[0]

        if tool not in self._tool_handlers:
            raise ValueError(f"Tool '{tool}' not supported by {type(self).__name__}")
        return self._execute_tool(tool)

    def _execute_tool(self, tool: str) -> RenderResponse:
        self._current_tool = tool

        try:
            if self._code.strip() == "":
                return self._write_response(success=False, message="No Code provided.")
            elif not self.verify_code:
                return self._write_response(success=False, message="Provided code is not valid.")
            else:
                self._tool_handlers[tool]()
                return self._write_response()

        except Exception as e:
            message = f"An exception occurred for {type(self).__name__} with tool {tool}:\n{e}"

        print(f"\n{message}")
        plt.close()
        return self._write_response(success=False, message=message)

    # def statistics(self) -> StatisticResponse:
    #     return "Entropy"

    @property
    def filepath_image(self) -> str:
        return self._filepath_images[self._current_tool]

    @property
    def log(self) -> str:
        return self._logs[self._current_tool]

    @property
    def tool_config(self) -> str:
        return self.tool_configs[self._current_tool]

    # Code processing and checks

    def _is_single_line(self):
        return "\n" not in self._code and "\r" not in self._code

    def _clean_code_lines(self, char: str):
        lines = self._code.splitlines()
        max_checks = 10

        for _ in range(max_checks):
            if not lines:
                break
            if char in lines[0]:
                break
            else:
                lines.pop(0)

        self._code = "\n".join(lines)
