import argparse
import json
import sys
from pathlib import Path

from . import renderers as _renderers  # Registers available renderers.
from .renderer import Renderer


def _parse_tool_configs(items: list[str]) -> dict:
    tool_configs: dict[str, dict] = {}
    for item in items:
        if "=" not in item or "." not in item.split("=", 1)[0]:
            raise ValueError("tool-config must be in the form tool.key=value")
        key, raw_value = item.split("=", 1)
        tool, config_key = key.split(".", 1)
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            value = raw_value
        tool_configs.setdefault(tool, {})[config_key] = value
    return tool_configs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="structivize",
        description="Render a single file with a selected Structivize renderer.",
    )
    parser.add_argument("--renderer", help="Renderer key, e.g. 'bio_fasta' or 'circuit_spice'.")
    parser.add_argument("--code", help="Path to the input code file to render.")
    parser.add_argument("--output", help="Output base path without extension (defaults to input file path).")
    parser.add_argument("--format", choices=["svg", "pdf", "png"], default="png", help="Output image format.")
    parser.add_argument("--category", help="Optional category key for the renderer.")
    parser.add_argument("--tool", help="Specific tool name when a renderer supports multiple tools.")
    parser.add_argument("--max-width", type=int, default=1024, help="Maximum output image width.")
    parser.add_argument("--max-height", type=int, default=1024, help="Maximum output image height.")
    parser.add_argument("--list-renderers", action="store_true", help="List available renderer keys and exit.")
    parser.add_argument("--list-tools", action="store_true", help="List available tool keys and exit.")
    parser.add_argument(
        "--tool-config",
        action="append",
        default=[],
        help="Override tool config: tool.key=value (JSON values supported).",
    )
    return parser


def _list_renderers() -> list[str]:
    return sorted(Renderer.registry.keys())


def _list_tools(renderer_key: str | None) -> list[str]:
    if renderer_key:
        renderer_cls = Renderer.registry.get(renderer_key)
        if renderer_cls is None:
            raise ValueError(f"Unknown renderer: {renderer_key}")
        return sorted(renderer_cls.DEFAULT_TOOL_CONFIGS.keys())

    tools: set[str] = set()
    for renderer_cls in Renderer.registry.values():
        tools.update(renderer_cls.DEFAULT_TOOL_CONFIGS.keys())
    return sorted(tools)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_renderers:
        print("\n".join(_list_renderers()))
        return 0

    if args.list_tools:
        try:
            tools = _list_tools(args.renderer)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print("\n".join(tools))
        return 0

    if not args.renderer or not args.code:
        parser.error("--renderer and --code are required unless listing renderers or tools.")

    code_path = Path(args.code)
    if not code_path.is_file():
        parser.error(f"code file not found: {code_path}")

    output_base_path = args.output or str(code_path.with_suffix(""))

    try:
        tool_configs = _parse_tool_configs(args.tool_config)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        renderer = Renderer.from_dict(
            renderer=args.renderer,
            code_path=str(code_path),
            output_base_path=output_base_path,
            output_format=args.format,
            category=args.category,
            max_width=args.max_width,
            max_height=args.max_height,
            tool_configs=tool_configs,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    result = renderer.render(tool=args.tool) if args.tool else renderer.render()
    print(json.dumps(result.model_dump(), indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
