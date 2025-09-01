import os
import time

from skidl import KICAD5, set_default_tool
from skidl.netlist_to_skidl import netlist_to_skidl

from ...renderer import Renderer
from ...utils import remove_files

set_default_tool(KICAD5)


# Renderer for KiCad V5 netlists
@Renderer.register("circuit_kicad")
class RendererCircuitKicad(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "skidl": {},
    }

    def preprocess_code(self):
        self._clean_code_lines("(")
        self._code = self._code.strip()

    def _render_skidl(self):
        # gets KiCad Netlist and creates Skidl Python representation and then generates svg using netlistsvg with custom skin templates and KiCad v5 schematic file

        skidl_code = netlist_to_skidl(self._code)
        skidl_code += f"\n    generate_svg(file_='{self.filepath_image}')"
        skidl_code += f"\n    generate_schematic(filepath='{os.path.dirname(self.filepath_image)}', top_name='{self.filepath_image.split('/')[-1]}', title='{self.filepath_image.split('/')[-1]}', flatness=0.0, retries=5)"

        # command that can be executed within the generated Python script:
        # generate_netlist(file_=f'{self.filepath_image}', tool=KICAD8)
        # generate_svg(file_=f'{self.filepath_image}') # layout_options for netlistsvg
        # generate_schematic(
        #     filepath=".",
        #     top_name="skidl_circuit_options",
        #     title="Titel",
        #     flatness=0.0,
        #     retries=1,
        #     options={
        #         "compress_before_place": True,
        #         "normalize": True,
        #         "fanout_attenuation": True,
        #         "draw_placement": True,
        #     }
        # )

        lines = skidl_code.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == "from skidl import *":
                insert_index = i + 1
                break
        new_text = "set_default_tool(KICAD5)"
        lines.insert(insert_index, new_text)
        skidl_code = "\n".join(lines)

        open(f"{self.filepath_image}.py", "w").write(skidl_code)

        self._execute_process(["python", f"{self.filepath_image}.py"])
        time.sleep(0.5)
        self._svg_save(self.filepath_image)

        remove_files(self.filepath_image, ["json"])
        remove_files(f"{self.filepath_image}_skin", ["svg"])
        remove_files(os.path.join(os.getcwd(), f'{self.filepath_image.split("/")[-1]}'), ["erc", "log", "net"])
        remove_files(os.path.join(os.getcwd(), f'{self.filepath_image.split("/")[-1]}_lib_sklib'), ["py"])
