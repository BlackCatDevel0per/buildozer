from pathlib import Path
from os import environ

use_git_caching = environ.get('USE_GIT_CACHING')

ct_path = Path(__file__).parent
# workaround script to avoid some source changes..
git_cache_script = str(Path(ct_path, 'bash', 'git_cache'))


def select_git(*, allow_cache: bool = False, force_cache: bool = False) -> str:
	# DOTO: rich logging..
	# print(allow_cache, use_git_caching)
	if allow_cache and any((use_git_caching, force_cache)):
		return git_cache_script
	return "git"
