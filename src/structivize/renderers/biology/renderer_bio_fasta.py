import re
from collections import defaultdict

import logomaker
import matplotlib.pyplot as plt
from Bio import SeqIO, motifs

from ...renderer import Renderer, StatisticResponse


# Sequence Logo
@Renderer.register("bio_fasta")
class RendererBioFasta(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "logomaker": {"color_scheme": "base_pairing", "show_spines": False, "stack_order": "small_on_top"},
        "weblogo": {},
    }

    def preprocess_code(self) -> str:
        cleaned_lines = []
        for line in self._code.strip().splitlines():
            stripped = line.strip()
            if not stripped:
                continue  # skip empty lines
            if stripped.startswith((";", "!", "#")):
                continue  # skip comment lines
            cleaned_lines.append(stripped)
        self._code = "\n".join(cleaned_lines)
        self._code = self._code.strip()
        if ">" == self._code[0] and len(self._code.splitlines()) == 1:
            self._code = self._code[1:]
        if len(self._code) > 1 and ">" not in self._code.splitlines()[0]:
            self._code = f">Sequence0\n{self._code}"

    def _is_fasta(self):
        lines = self._code.strip().splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith(";"):
                i += 1
                continue
            if not line.startswith(">"):
                return False  # Expected header line
            i += 1

            # Skip comments and blank lines
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line.startswith(";"):
                    i += 1
                    continue
                break

            if i >= len(lines):
                return False  # No sequence line found after header

            sequence_line = lines[i].strip()
            if not re.fullmatch(r"[A-Za-z*-]+", sequence_line):
                return False  # Sequence line is invalid (must be letters only)
            i += 1

            # Ensure next lines (if any) are either blank, comments, or a new '>'
            while i < len(lines):
                peek = lines[i].strip()
                if not peek or peek.startswith(";"):
                    i += 1
                    continue
                if peek.startswith(">"):
                    break  # next entry
                else:
                    return False  # Invalid: second sequence line found
        return True

    def _read_fasta(self):
        seqs = []
        with open(self._filepath_code) as f:
            raw_seqs = f.readlines()
            seqs = [
                seq.strip()
                for seq in raw_seqs
                if ("#" not in seq) and (">" not in seq) and ("!" not in seq) and (";" not in seq) and (seq.strip() != "")
            ]
        return seqs

    def verify_code(self):
        return (self._is_single_line() or self._is_fasta()) and len(self._code) < 1000

    def _render_logomaker(self):
        # mat_df = logomaker.get_example_matrix('ww_information_matrix', print_description=False)
        # mat_df = logomaker.sequence_to_matrix(self._code)

        # https://logomaker.readthedocs.io/en/latest/implementation.html
        mat_df = logomaker.alignment_to_matrix(self._read_fasta())
        logo = logomaker.Logo(
            mat_df
        )  # , color_scheme="base_pairing", show_spines=False), color_scheme='NajafabadiEtAl2017', stack_order="small_on_top’"
        plt.savefig(f"{self.filepath_image}.png")
        plt.close()

    def _render_weblogo(self):
        # BioPython Motifs:
        # sequences = [record.seq for record in SeqIO.parse(self._filepath_code, "fasta")]
        # motif = motifs.create(sequences)
        # motif.weblogo(f"{self.filepath_image}.png") # uses Berkeley weblogo service

        self._execute_process(
            commands=["weblogo", "--format", "PDF", "-s", "large", "-P", "", "-f", self._filepath_code, "-o", f"{self.filepath_image}.pdf"]
        )  # https://weblogo.threeplusone.com/manual.html
        self._pdf_save(self.filepath_image)

    def _cnt_sequences(self, code):
        cnt = 0
        lines = code.strip().splitlines()
        for i, line in enumerate(lines):
            if line.startswith(">"):
                cnt += 1
        return cnt

    def statistics(self) -> StatisticResponse:
        counts = defaultdict(int)
        counts["sequences"] = self._cnt_sequences(self._code)
        sequence = ''
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
        return StatisticResponse(node_types=dict(counts))