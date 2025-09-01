import os
import re
import shutil
import tempfile

from ...renderer import Renderer
from ...utils import save_text
from .renderer_db_dbml import RendererDbDbml


@Renderer.register("db_prisma")
class RendererDbPrisma(RendererDbDbml):
    DEFAULT_TOOL_CONFIGS = {
        "prisma": {},
    }

    def preprocess_code(self):
        pattern = r"(generator client\s*\{[^}]*\}|datasource db\s*\{[^}]*\}|generator dbml\s*\{[^}]*\})"
        cleaned_schema = re.sub(pattern, "", self._code, flags=re.DOTALL)
        self._code = cleaned_schema.strip()

    def _add_metadata(self):
        metadata = f"""generator client {{
  provider = "prisma-client-js"
}}

datasource db {{
  provider = "mysql"
  url      = env("DATABASE_URL")
}}

generator dbml {{
    provider   = "prisma-dbml-generator"
    output     = "{os.path.dirname(os.path.abspath(self.filepath_image))}"
    outputName = "{self.filepath_image.split("/")[-1]}.dbml"
}}

"""
        self._code = f"{metadata}\n{self._code }".strip()
        save_text(filename=self._filepath_code, data=self._code)

    def _render_prisma(self):
        self._add_metadata()
        # with tempfile.TemporaryDirectory() as tmp_dir:
        #     tmp_path = os.path.join(tmp_dir, os.path.basename(self._filepath_code))
        #     shutil.copyfile(self._filepath_code, tmp_path)

        self._execute_process(commands=["prisma", "generate", "--schema", self._filepath_code])
        self._render_dbml(f"{self.filepath_image}.dbml", self.filepath_image)
