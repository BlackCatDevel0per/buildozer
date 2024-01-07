from typing import Union

from pathlib import Path
from os import environ

use_git_caching = environ.get('USE_GIT_CACHING')

ct_path = Path(__file__).parent
# workaround script to avoid some source changes..
git_cache_script = Path(ct_path, 'bash', 'git_cache')


def select_git(*, allow_cache: bool = False) -> Union[Path, str]:
	# DOTO: rich logging..
	# print(allow_cache, use_git_caching)
	if allow_cache and use_git_caching:
		return git_cache_script
	return "git"
