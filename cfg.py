from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

console = False
ewlaunch_dir = ''
always_show_dialog = False
always_show_log = False
wait_after_launch = False
default_version = ''
default_save = False
list_box_lines = 10
min_window_width = 500
info_pane = True
ttk_style: str | None = None
template_header = ''
template = ''
template_footer = ''
argvars_path = ''
argvars_version_re = ''
workspace_template = ''
shortname: Mapping[str, str] = {}
subcmd: str | None = None
ws = ''
version: str | None = None
out_file: str | None = None
rest_args: list[str] = []
version_filter = ''
noheading = False
installations: str | None = None
reg = False
exec_name = ''
