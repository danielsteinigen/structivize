import io
from pathlib import Path

import chess
import chess.pgn
import chess.svg

from ...image_utils import images_are_similar
from ...renderer import Renderer
from ...utils import remove_files


@Renderer.register("chess_pgn")
class RendererChessPgn(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "chess": {},
    }

    def _render_chess(self):
        pgn = chess.pgn.read_game(io.StringIO(self._code))
        board = pgn.board()

        for move in pgn.mainline_moves():
            board.push(move)

        svg_code = chess.svg.board(board)
        self._svg_save(path=self.filepath_image, svg_code=svg_code)

        reference_path = Path(__file__).parent / "../../../examples/reference/false_ref_chess.png"
        result = images_are_similar(f"{self.filepath_image}.png", f"{reference_path}", tolerance=5)
        if result:
            print("Remove PGN image")
            remove_files(self.filepath_image, ["png", "pdf", "svg"])
