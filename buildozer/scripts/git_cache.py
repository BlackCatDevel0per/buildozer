from typing import Tuple, List

import argparse
from shlex import split as split4shell
from hashlib import sha1
from pathlib import Path
import subprocess

# TODO: Use as cli & upload to PyPi?)

# TODO: Optional local caching
CACHE_DIR = Path(Path.home(), ".buildozer/cache/git")


# -> command, destination2cache, origin_destination, is_clone_command
def parse_git() -> Tuple[List[str], Path, Path, bool]:
	parser = argparse.ArgumentParser(description="Git cache wrapper")
	parser.add_argument(
		'sub_command', type=str, default='', nargs='?',
	)

	parser.add_argument(
		'repo', metavar='repository', type=str, nargs='?',
		help='Repository URL', default='',
	)
	parser.add_argument(
		'--single-branch', metavar='single_branch', type=str, default='',
	)

	parser.add_argument(
		'path', metavar='path', type=str, nargs='?',
		default='',
		help='Path to clone repository',
	)
	parser.add_argument(
		'-o', '--origin', type=str, default=None,
		help='Name of remote to track',
	)

	args, other_args_ = parser.parse_known_args()

	other_args: str = ' '.join(other_args_)
	# print(other_args)

	if args.sub_command != 'clone':
		# print(args)
		if args.path:
			_other_args = f'{args.repo} {args.path}'
		else:
			_other_args = f'{args.repo}'
		##
		if other_args:
			_other_args = f'{_other_args} {other_args}'
		_def_path_from_command = Path(args.path or args.origin or Path(args.repo).stem)
		return split4shell(
			f'git {args.sub_command} {_other_args}'.strip(),
		), Path(), _def_path_from_command, False


	repo = args.repo
	# FIXME: Check large paths..
	if args.path:
		##
		orig_path = Path(args.path)
		cached_path = Path(CACHE_DIR, args.path)
	elif args.origin:
		##
		orig_path = Path(args.path)
		cached_path = Path(CACHE_DIR, args.origin)
		args.origin = None
	else:
		if not repo:
			repo = args.single_branch
		_git_url = Path(repo)
		_des_dirname_from_repo = _git_url.stem

		orig_path = Path(_des_dirname_from_repo)
		cached_path = Path(CACHE_DIR, _des_dirname_from_repo)

	hash_value = sha1(repo.encode()).hexdigest()

	des2cache = Path(cached_path.parent, Path(f"{cached_path.stem}_{hash_value}"))

	# FIXME: Crutchy~
	if orig_path.stem == other_args_[-1]:
		del other_args_[-1]
		other_args = ' '.join(other_args_)

	##
	if args.repo:
		final_command = f'git {args.sub_command} {repo} {des2cache} {other_args}'
	elif args.single_branch:
		##
		final_command = (
			f'git {args.sub_command}'
			' '
			f'{other_args}'
			' '
			f'--single-branch {args.single_branch}'
			' '
			f'{des2cache}'
		)
	else:
		# mb will fail..
		final_command = f'git {args.sub_command} {des2cache} {other_args}'

	return split4shell(
		final_command.strip()
	), des2cache, orig_path, True



def main(command: List[str], des2cache: Path, origin_des: Path, is_clone_command: bool) -> None:
	print(
		(
			f"{command}"
			'\n'
			f"cache_des: '{des2cache}',"
			'\n'
			'***'
			'\n'
			f"origin_des: '{origin_des}', clone: '{is_clone_command}'"
		)
	)

	if not is_clone_command:
		subprocess.run(command)
		return

	print(f"Git cache dir: '{CACHE_DIR}'")
	CACHE_DIR.mkdir(parents=True, exist_ok=True)

	# TODO: DRYS
	# TODO: Mb check there for symlinks..?
	# TODO: Copy mode if is not posix or not supports posix..
	if origin_des.exists():
		print(f"Directory '{origin_des}' exists! Skip..?")
		subprocess.run(command)
		return

	if des2cache.exists():
		print(f"Using cached {des2cache}")
		origin_des.symlink_to(des2cache)
	else:
		if des2cache.is_symlink():
			print(f"Broken cached symlink: '{des2cache}', unlink..")
			des2cache.unlink()

		print(f"Caching into {des2cache}")
		subprocess.run(command)

		if not origin_des.exists():
			if origin_des.is_symlink():
				print(f"Broken symlink: '{origin_des}', unlink..")
				origin_des.unlink()

			origin_des.symlink_to(des2cache)

	# TODO: Reckeck after synlink/copy the path..?


if __name__ == "__main__":
	command, des2cache, origin_des, is_clone_command = parse_git()
	main(command, des2cache, origin_des, is_clone_command)
