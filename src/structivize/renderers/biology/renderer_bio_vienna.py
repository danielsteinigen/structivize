import glob
import os
import re
import shutil
from collections import defaultdict

import forgi
import forgi.visual.mplotlib as fvm
import matplotlib.pyplot as plt

from ...renderer import NodeType, Renderer, StatisticResponse


# Vienna format generates RNA secondary structure diagrams
@Renderer.register("bio_vienna")
class RendererBioVienna(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "varna": {
            "algorithm": "radiate",
            "show_labels": "False",
            "draw_backbone": "True",
            "theme": "default",
            "color_backbone": "",
            "color_base_pair": "",
            "color_base_inner": "",
            "color_base_outer": "",
            "color_base_name": "",
            "color_base_number": "",
        },
        "forgi": {
            "backbone_color": "#000000",
            "backbone_width": 2,
            "bp_color": "#FF0000",
            "bp_width": 1,
            "label_color": "#000000",
            "label_weight": "normal",
            "label_size": 10,
        },
        "r2dt": {},
    }

    def preprocess_code(self) -> str:
        code = ""
        for line in self._code.splitlines():
            line_str = line.strip()
            if (
                not line_str.startswith("#")
                and not line_str.startswith("!")
                and not line_str.startswith(";")
                and not line_str.startswith("//")
                and line_str != ""
            ):
                code += f"{line}\n"
        self._code = code.strip()
        if (
            len(self._code) > 1
            and ">" == self._code[0]
            and len(self._code.splitlines()) == 2
            and "(" in self._code.splitlines()[1]
            and "A" in self._code.splitlines()[0]
        ):
            self._code = self._code[1:]
        if ">" not in self._code.splitlines()[0] and len(self._code.splitlines()) <= 2:
            self._code = ">abc\n" + self._code.strip()

    def verify_code(self):
        return len(self._code.splitlines()) <= 10
        # TODO: sequence+brackets same length + check if only single sequence/dot-bracket - only the first will be rendered -> partly done

    def _render_varna(self):
        # https://varna.lisn.upsaclay.fr/index.php?lang=en&page=command&css=varna
        # supports following inputs: Vienna, CT, BPSeq or RNAML
        self._execute_process(
            commands=[
                "java",
                "-cp",
                f"{self._tool_path}/VARNAv3-93.jar",
                "fr.orsay.lri.varna.applications.VARNAcmd",
                "-i",
                self._filepath_code,
                "-o",
                f"{self.filepath_image}.png",
                "-titleSize",
                "0",
                "-resolution",
                "2.0",
                "-zoom",
                "1.0",
                "-border",
                "'20x30'",
                "-algorithm",
                self.tool_config["algorithm"],
                "-autoHelices",
                self.tool_config["show_labels"],
                "-autoInteriorLoops",
                self.tool_config["show_labels"],
                "-autoTerminalLoops",
                self.tool_config["show_labels"],
                "-drawBases",
                "True",
                "-drawBackbone",
                self.tool_config["draw_backbone"],
                "-bpStyle",
                "lw",
                "-bp",
                self.tool_config["color_base_pair"],
                "-baseOutline",
                self.tool_config["color_base_outer"],
                "-baseNum",
                self.tool_config["color_base_number"],
                "-baseName",
                self.tool_config["color_base_name"],
                "-baseInner",
                self.tool_config["color_base_inner"],
                "-backbone",
                self.tool_config["color_backbone"],
            ]
        )  #
        self._png_save(self.filepath_image)
        # os.system(f"java -cp {self._tool_path}/VARNAv3-93.jar fr.orsay.lri.varna.applications.VARNAcmd -i {self._filepath_code} -o {self.filepath_image}.png -titleSize 0 -resolution '2.0' -zoom 1.0 -border '20x30' -algorithm radiate")
        # TODO: split fasta into sequence and struvture and render pdf
        # os.system(f"java -cp {self._tool_path}/VARNAv3-93.jar fr.orsay.lri.varna.applications.VARNAcmd -sequenceDBN '{sequence} -structureDBN '{structure}' -o {self.filepath_image}1.eps -titleSize 0 -resolution '2.0' -zoom 1.0 -border '20x30' -algorithm radiate")
        # os.system(f"convert -density 500 {self.filepath_image}.eps {self.filepath_image}.pdf")
        # self._pdf_save(f"{self.filepath_image}")

    def _render_forgi(self):
        # https://viennarna.github.io/forgi/graph_tutorial.html
        cg = forgi.load_rna(self._filepath_code, allow_many=False)

        bb_kwargs = {
            "color": self.tool_config["backbone_color"],
            "linewidth": self.tool_config["backbone_width"],
            "linestyle": self.tool_config.get("backbone_style", "-"),
            "alpha": self.tool_config.get("alpha", 1.0),
        }

        bp_kwargs = {
            "color": self.tool_config["bp_color"],
            "linewidth": self.tool_config["bp_width"],
            "linestyle": self.tool_config.get("bp_style", "-"),
            "alpha": self.tool_config.get("alpha", 1.0),
        }

        txt_kwargs = {
            "color": self.tool_config["label_color"],
            "fontweight": self.tool_config["label_weight"],
            "fontsize": self.tool_config["label_size"],
        }
        fvm.plot_rna(
            cg,
            offset=(0, 0),
            backbone_kwargs=bb_kwargs,
            basepair_kwargs=bp_kwargs,
            text_kwargs=txt_kwargs,
            lighten=self.tool_config.get("lighten", 0.7),
        )
        # fvm.plot_rna(cg, text_kwargs={"fontweight": "black"}, lighten=0.7, backbone_kwargs={"linewidth": 2})
        plt.savefig(f"{self.filepath_image}.png")
        plt.close()
        self._png_save(self.filepath_image)

    def _render_r2dt(self):
        # https://docs.r2dt.bio/en/latest/usage.html
        # r2dt.py draw temp/test.fasta temp/test/examples
        # r2dt.py templatefree temp/test.fasta temp/test/examples --rnartist
        # docker run -it -v $R2DT_LIBRARY:/rna/r2dt/data/cms -v {self._tool_path}/r2dt_temp:/rna/r2dt/temp rnacentral/r2dt
        # docker run --entrypoint r2dt.py -v $R2DT_LIBRARY:/rna/r2dt/data/cms -v {self._tool_path}/r2dt_temp:/rna/r2dt/temp rnacentral/r2dt draw temp/test.fasta temp/test
        # docker run --entrypoint r2dt.py -v $R2DT_LIBRARY:/rna/r2dt/data/cms -v {self._tool_path}/r2dt_temp:/rna/r2dt/temp rnacentral/r2dt templatefree temp/test.fasta temp/test --rnartist

        path_temp = f"{self._tool_path}/r2dt_temp"
        shutil.copyfile(self._filepath_code, f"{path_temp}/test.fasta")
        # self._execute_process(commands=["docker", "run", "--entrypoint", "r2dt.py", "-v", "$R2DT_LIBRARY:/rna/r2dt/data/cms", "-v", f"{path_temp}:/rna/r2dt/temp", "rnacentral/r2dt", "draw", "temp/test.fasta", "temp/test"])
        os.system(
            f"docker run --entrypoint r2dt.py -v $R2DT_LIBRARY:/rna/r2dt/data/cms -v {path_temp}:/rna/r2dt/temp rnacentral/r2dt draw temp/test.fasta temp/test"
        )
        svg_files = glob.glob(f"{path_temp}/test/results/svg/*.svg")
        shutil.copyfile(svg_files[0], f"{self.filepath_image}.svg")
        self._execute_process(commands=["sudo", "rm", "-r", f"{path_temp}/test"])
        self._svg_save(path=self.filepath_image)

    def _has_second_gt(self, s):
        first_index = s.find(">")
        if first_index == -1:
            return False
        second_index = s.find(">", first_index + 1)
        if second_index == -1:
            return False
        return True

    def statistics(self) -> StatisticResponse:
        if self._has_second_gt(self._code):
            return StatisticResponse()
        counts = defaultdict(int)
        sequence = ""
        lines = self._code.strip().splitlines()
        for line in lines:
            if line.startswith(">"):
                continue
            if re.fullmatch(r"[().]+", line.strip()):
                continue
            sequence += line.strip()
        for char in sequence:
            if char.isalpha():
                counts[char.upper()] += 1
        return StatisticResponse(node_types=[NodeType(type=name, count=count) for name, count in counts.items()])
