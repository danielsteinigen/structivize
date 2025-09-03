import io

import chess
import chess.pgn
import chess.svg

from ...renderer import Renderer


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

        if board.fen() != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":  # better: check for "illegal san:" in log output
            svg_code = chess.svg.board(board)
            self._svg_save(path=self.filepath_image, svg_code=svg_code)
