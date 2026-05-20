"""Command-line entrypoint for fastqt6."""

from __future__ import annotations

import argparse
from pathlib import Path

from .designer import write_auth_ui, write_form_ui, write_main_window_ui
from .fields import field
from .scaffold import scaffold_basic_app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fastqt6")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold_parser = subparsers.add_parser("scaffold", help="create a small starter app")
    scaffold_parser.add_argument("target")

    auth_parser = subparsers.add_parser("ui-auth", help="create auth.ui")
    auth_parser.add_argument("path")

    main_parser = subparsers.add_parser("ui-main", help="create main.ui with tabs")
    main_parser.add_argument("path")
    main_parser.add_argument("--tabs", default="Каталог,Мои заказы,Все заказы,Статистика")

    form_parser = subparsers.add_parser("ui-form", help="create a form .ui from field declarations")
    form_parser.add_argument("path")
    form_parser.add_argument("--title", default="Форма")
    form_parser.add_argument("--class-name", default="Form")
    form_parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="field as name:kind:label, for example article:text:Артикул",
    )

    args = parser.parse_args(argv)

    if args.command == "scaffold":
        scaffold_basic_app(args.target)
        print(f"Created {args.target}")
        return 0
    if args.command == "ui-auth":
        write_auth_ui(args.path)
        print(args.path)
        return 0
    if args.command == "ui-main":
        tabs = [tab.strip() for tab in args.tabs.split(",") if tab.strip()]
        write_main_window_ui(args.path, tabs=tabs)
        print(args.path)
        return 0
    if args.command == "ui-form":
        specs = [_parse_field(raw) for raw in args.field]
        write_form_ui(args.path, specs, title=args.title, class_name=args.class_name)
        print(args.path)
        return 0
    return 1


def _parse_field(raw: str):
    parts = raw.split(":", 2)
    if len(parts) == 1:
        return field(parts[0])
    if len(parts) == 2:
        return field(parts[0], kind=parts[1])
    return field(parts[0], parts[2], parts[1])


if __name__ == "__main__":
    raise SystemExit(main())
