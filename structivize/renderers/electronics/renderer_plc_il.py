import re
import shutil
from pathlib import Path

from ...renderer import Renderer

il_commands = {
    "LD",
    "LDN",
    "LDR",
    "LDF",
    "AND",
    "ANDN",
    "ANDR",
    "ANDF",
    "OR",
    "ORN",
    "ORR",
    "ORF",
    "XOR",
    "XORN",
    "XORR",
    "XORF",
    "NOT",
    "ST",
    "STN",
    "S",
    "R",
    "SR",
    "ADD",
    "SUB",
    "MUL",
    "DIV",
    "GT",
    "GE",
    "EQ",
    "NE",
    "LE",
    "LT",
    "CALL",
    "RET",
    "JMP",
    "JMPC",
    "JMPCN" "JMZ",
    "JNZ",
    "JCN",
    "JMPC",
    "MOV",
    ")",
}


@Renderer.register("plc_il")
class RendererPlcIl(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "plc": {},
    }

    def __ensure_end_var(self, plc_text: str) -> str:
        lines = plc_text.splitlines()

        # 1 – find the opening VAR line
        var_idx = None
        for i, line in enumerate(lines):
            if line.strip().lower() == "var":
                var_idx = i
                var_upper = line.strip().isupper()
                break
        if var_idx is None:  # no variable block at all
            return plc_text

        # 2 – abort early if it is already closed
        if any(ln.strip().lower() == "end_var" for ln in lines[var_idx + 1 :]):
            return plc_text

        # 3 – decide where the END_VAR should go
        insert_at = len(lines)  # fallback: end of file
        for j in range(var_idx + 1, len(lines)):
            word = lines[j].strip().split(" ", 1)[0] if lines[j].strip() else ""
            if word in il_commands:  # first instruction ⇒ end of VAR section
                insert_at = j
                break

        # 4 – insert END_VAR (matching the case of the opener)
        end_var_kw = "END_VAR" if var_upper else "end_var"
        lines.insert(insert_at, end_var_kw)
        # add a blank line for readability (unless one is there already)
        if insert_at + 1 < len(lines) and lines[insert_at + 1].strip():
            lines.insert(insert_at + 1, "")

        return "\n".join(lines)

    def preprocess_code(self) -> str:
        code = ""
        for line in self._code.splitlines():
            line_str = line.strip()
            if (
                not line_str.startswith("(*")
                and not line_str.startswith("#")
                and not line_str.startswith("//")
                and not (line_str.startswith("%") and ":" not in line_str)
                and not line_str == "IL"
                and not line_str == "IL_END"
            ):
                code += f"{line}\n"
        lines = code.strip().splitlines()
        if lines and ("PROGRAM" in lines[0] or "PRG" in lines[0]):
            lines = lines[1:]
        self._code = "\n".join(lines)
        self._code = self.__ensure_end_var(self._code).strip().replace("end_var", "END_VAR").replace("var\n", "VAR\n")

    def verify_code(self):
        lines = [line.strip() for line in self._code.strip().splitlines() if line.strip() != ""]

        # Check VAR section
        if not lines or not lines[0].startswith("VAR"):
            print("Error: Missing or incorrect start of VAR section")
            return False

        try:
            end_var_index = lines.index("END_VAR")
        except ValueError:
            print("Error: Missing END_VAR")
            return False

        # Validate variable declarations
        var_lines = lines[1:end_var_index]
        var_pattern = re.compile(r"^%?[a-zA-Z_][\w]*\s*:\s*[A-Z]+")

        for line in var_lines:
            if not var_pattern.match(line):
                print(f"Invalid variable declaration: {line}")
                return False

        # Validate commands and labels
        instruction_lines = lines[end_var_index + 1 :]
        label_pattern = re.compile(r"^%?[a-zA-Z_][\w]*:")

        for line in instruction_lines:
            if label_pattern.match(line):
                continue
            first_token = line.split()[0]
            if first_token not in il_commands:
                print(f"Invalid command or syntax: {line}")
                return False

        return True

    def _render_plc(self):
        # TODO: implement rendering
        reference_path = Path(__file__).parent / "../../../examples/reference/sample_ladder.png"
        shutil.copyfile(f"{reference_path}", f"{self.filepath_image}.png")
