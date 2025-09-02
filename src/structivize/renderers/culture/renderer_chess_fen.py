from collections import defaultdict

import chess
import chess.svg

from ...renderer import Renderer, StatisticResponse


@Renderer.register("chess_fen")
class RendererChessFen(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "chess": {},
    }

    def preprocess_code(self):
        self._clean_code_lines("/")
        self._code = self._code.strip()

    def verify_code(self):
        return self._is_single_line() and "/" in self._code

    def _render_chess(self):
        board = chess.Board(self._code)
        svg_code = chess.svg.board(board)
        self._svg_save(path=self.filepath_image, svg_code=svg_code)

    def statistics(self) -> StatisticResponse:
        piece_map = {"p": "pawns", "r": "rooks", "n": "knights", "b": "bishops", "q": "queens", "k": "kings"}
        piece_counts = defaultdict(int)
        board = self._code.strip().split()[0]
        for char in board:
            if char.lower() in piece_map:
                piece = piece_map[char.lower()]
                piece_counts[piece] += 1
        return StatisticResponse(node_types=dict(piece_counts))
