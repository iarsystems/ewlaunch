from collections.abc import Mapping
from typing import Optional

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
ttk_style: Optional[str] = None
template_header = ''
template = ''
template_footer = ''
argvars_path = ''
argvars_version_re = ''
workspace_template = ''
shortname: Mapping[str, str] = {}
subcmd: Optional[str] = None
ws = ''
version: Optional[str] = None
out_file: Optional[str] = None
rest_args: list[str] = []
version_filter = ''
noheading = False
installations: Optional[str] = None
reg = False
exec_name = ''
