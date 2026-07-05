import os
import shutil
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_SHIP = ROOT / "scripts" / "btb-ship-base"
SHIP_TEMPLATE = ROOT / "templates" / "ship.template"


def run(cmd, cwd, env=None, check=True):
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(map(str, cmd))}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def write_executable(path, content):
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def make_repo(tmp_path):
    repo = tmp_path / "repo"
    origin = tmp_path / "origin.git"
    repo.mkdir()
    run(["git", "init", "-b", "main"], repo)
    run(["git", "config", "user.name", "Test User"], repo)
    run(["git", "config", "user.email", "test@example.com"], repo)
    (repo / "README.md").write_text("hello\n")
    run(["git", "add", "README.md"], repo)
    run(["git", "commit", "-m", "initial"], repo)
    run(["git", "init", "--bare", str(origin)], tmp_path)
    run(["git", "remote", "add", "origin", str(origin)], repo)
    run(["git", "push", "-u", "origin", "main"], repo)
    return repo, origin


def make_env(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gh_log = tmp_path / "gh.log"
    fake_gh = fake_bin / "gh"
    write_executable(
        fake_gh,
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {gh_log}\n",
    )
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    return env, gh_log


def make_client_repo(tmp_path):
    repo = tmp_path / "client-repo"
    scripts_dir = repo / "scripts"
    git_info = repo / ".git" / "info"
    scripts_dir.mkdir(parents=True)
    git_info.mkdir(parents=True)
    shutil.copy2(SHIP_TEMPLATE, scripts_dir / "ship")
    return repo


def make_worktree_client_repo(tmp_path):
    repo = tmp_path / "client-worktree"
    scripts_dir = repo / "scripts"
    git_dir = tmp_path / "client-worktree.git"
    scripts_dir.mkdir(parents=True)
    (repo / ".git").write_text(f"gitdir: {git_dir}\n")
    (git_dir / "info").mkdir(parents=True)
    shutil.copy2(SHIP_TEMPLATE, scripts_dir / "ship")
    return repo, git_dir


def test_runs_hooks_in_order_and_creates_release_commit(tmp_path):
    repo, origin = make_repo(tmp_path)
    env, gh_log = make_env(tmp_path)
    hook_dir = repo / "scripts" / "ship.d"
    hook_dir.mkdir(parents=True)
    order_log = tmp_path / "hook-order.log"

    for hook in [
        "before-version",
        "after-version",
        "before-release-commit",
        "after-release-commit",
        "before-github-release",
        "after-github-release",
    ]:
        if hook == "before-release-commit":
            body = (
                "#!/usr/bin/env bash\n"
                f"printf '%s:%s:%s\\n' '{hook}' \"$BTB_VERSION_TAG\" \"$BTB_RELEASE_COMMIT_CREATED\" >> {order_log}\n"
                "printf 'built for %s\\n' \"$BTB_VERSION_TAG\" > generated.txt\n"
            )
        else:
            body = (
                "#!/usr/bin/env bash\n"
                f"printf '%s:%s:%s\\n' '{hook}' \"$BTB_VERSION_TAG\" \"$BTB_RELEASE_COMMIT_CREATED\" >> {order_log}\n"
            )
        write_executable(hook_dir / hook, body)

    run(["git", "add", "scripts/ship.d"], repo)
    run(["git", "commit", "-m", "add ship hooks"], repo)
    run(["git", "push", "origin", "main"], repo)
    run(["git", "tag", "v1.2.3"], repo)
    run(["git", "push", "origin", "v1.2.3"], repo)

    run([str(BASE_SHIP), "--repo-root", str(repo), "--bump-patch", "--yes"], repo, env=env)

    assert (repo / "generated.txt").read_text() == "built for v1.2.4\n"
    assert run(["git", "tag", "--list", "v1.2.4"], repo).stdout.strip() == "v1.2.4"
    assert run(["git", "ls-remote", "--tags", str(origin), "refs/tags/v1.2.4"], repo).stdout
    assert "release create v1.2.4 --title v1.2.4-beta --prerelease --generate-notes" in gh_log.read_text()
    assert order_log.read_text().splitlines() == [
        "before-version::false",
        "after-version:v1.2.4:false",
        "before-release-commit:v1.2.4:false",
        "after-release-commit:v1.2.4:true",
        "before-github-release:v1.2.4:true",
        "after-github-release:v1.2.4:true",
    ]


def test_updates_version_file_when_present(tmp_path):
    repo, _origin = make_repo(tmp_path)
    env, _gh_log = make_env(tmp_path)
    (repo / "VERSION").write_text("v1.0.0\n")
    run(["git", "add", "VERSION"], repo)
    run(["git", "commit", "-m", "add version"], repo)
    run(["git", "push", "origin", "main"], repo)

    run([str(BASE_SHIP), "--repo-root", str(repo), "--bump-minor", "--yes"], repo, env=env)

    assert (repo / "VERSION").read_text() == "v1.1.0\n"
    assert run(["git", "log", "-1", "--pretty=%s"], repo).stdout.strip() == "release v1.1.0"


def test_dry_run_does_not_execute_hooks_or_create_tags(tmp_path):
    repo, _origin = make_repo(tmp_path)
    env, gh_log = make_env(tmp_path)
    hook_dir = repo / "scripts" / "ship.d"
    hook_dir.mkdir(parents=True)
    write_executable(
        hook_dir / "before-release-commit",
        "#!/usr/bin/env bash\nprintf 'nope\\n' > generated.txt\n",
    )
    run(["git", "add", "scripts/ship.d"], repo)
    run(["git", "commit", "-m", "add dry-run hook"], repo)
    run(["git", "push", "origin", "main"], repo)

    result = run(
        [str(BASE_SHIP), "--repo-root", str(repo), "--bump-patch", "--dry-run"],
        repo,
        env=env,
    )

    assert "DRY-RUN:" in result.stdout
    assert not (repo / "generated.txt").exists()
    assert run(["git", "tag", "--list", "v0.1.0"], repo).stdout.strip() == ""
    assert not gh_log.exists()


def test_rejects_duplicate_tag(tmp_path):
    repo, _origin = make_repo(tmp_path)
    env, _gh_log = make_env(tmp_path)
    run(["git", "tag", "v1.2.3"], repo)

    result = run(
        [str(BASE_SHIP), "--repo-root", str(repo), "--set-version", "v1.2.3", "--yes"],
        repo,
        env=env,
        check=False,
    )

    assert result.returncode != 0
    assert "tag 'v1.2.3' already exists locally" in result.stderr


def test_pipeline_ship_wrapper_delegates_to_base_and_floats_v1(tmp_path):
    repo, _origin = make_repo(tmp_path)
    env, _gh_log = make_env(tmp_path)
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir()
    shutil.copy2(BASE_SHIP, scripts_dir / "btb-ship-base")
    shutil.copy2(ROOT / "scripts" / "ship", scripts_dir / "ship")
    run(["git", "add", "scripts"], repo)
    run(["git", "commit", "-m", "add pipeline ship scripts"], repo)
    run(["git", "push", "origin", "main"], repo)
    run(["git", "tag", "v1.0.0"], repo)
    run(["git", "push", "origin", "v1.0.0"], repo)

    result = run([str(scripts_dir / "ship"), "--bump-patch", "--dry-run"], repo, env=env)

    assert "create immutable tag v1.0.1" in result.stdout
    assert f"DRY-RUN: git -C {repo} tag -f v1 " in result.stdout


def test_client_ship_template_bootstraps_default_local_checkout(tmp_path):
    repo = make_client_repo(tmp_path)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    git_log = tmp_path / "git.log"
    args_file = tmp_path / "args.txt"
    fake_git = fake_bin / "git"
    write_executable(
        fake_git,
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {git_log}\n"
        'if [[ "$1" == "-C" && "$3" == "rev-parse" && "$4" == "--git-path" && "$5" == "info/exclude" ]]; then\n'
        '  printf "%s/.git/info/exclude\\n" "$2"\n'
        "  exit 0\n"
        "fi\n"
        'if [[ "$1" == "clone" ]]; then\n'
        '  destination="${@: -1}"\n'
        '  mkdir -p "$destination/scripts"\n'
        "  cat > \"$destination/scripts/btb-ship-base\" <<'EOF'\n"
        "#!/usr/bin/env bash\n"
        'printf \'%s\\n\' "$@" > "$BTB_BASE_ARGS_FILE"\n'
        "EOF\n"
        '  chmod +x "$destination/scripts/btb-ship-base"\n'
        "fi\n",
    )
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["BTB_BASE_ARGS_FILE"] = str(args_file)
    env.pop("BTB_PIPELINE_ROOT", None)

    result = run([str(repo / "scripts" / "ship"), "--dry-run"], repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "Fetching btb-pipeline@v1" in result.stdout
    assert git_log.read_text().splitlines() == [
        f"-C {repo} rev-parse --git-path info/exclude",
        "clone --quiet --config advice.detachedHead=false --depth 1 --branch v1 "
        "https://github.com/btoddb/btb-pipeline.git "
        f"{repo / '.btb-pipeline'}"
    ]
    assert args_file.read_text().splitlines() == [
        "--repo-root",
        str(repo),
        "--dry-run",
    ]
    assert (repo / ".git" / "info" / "exclude").read_text().splitlines() == [
        "/.btb-pipeline/"
    ]


def test_client_ship_template_reuses_existing_local_checkout(tmp_path):
    repo = make_client_repo(tmp_path)
    pipeline_root = repo / ".btb-pipeline"
    scripts_dir = pipeline_root / "scripts"
    scripts_dir.mkdir(parents=True)
    (pipeline_root / ".git").mkdir()
    args_file = tmp_path / "args.txt"
    write_executable(
        scripts_dir / "btb-ship-base",
        "#!/usr/bin/env bash\n"
        'printf \'%s\\n\' "$@" > "$BTB_BASE_ARGS_FILE"\n',
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    git_log = tmp_path / "git.log"
    fake_git = fake_bin / "git"
    write_executable(
        fake_git,
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {git_log}\n"
        'if [[ "$1" == "-C" && "$3" == "rev-parse" && "$4" == "--git-path" && "$5" == "info/exclude" ]]; then\n'
        '  printf "%s/.git/info/exclude\\n" "$2"\n'
        "  exit 0\n"
        "fi\n"
    )
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["BTB_BASE_ARGS_FILE"] = str(args_file)

    result = run([str(repo / "scripts" / "ship"), "--dry-run"], repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "Updating local btb-pipeline checkout" in result.stdout
    assert git_log.read_text().splitlines() == [
        f"-C {repo} rev-parse --git-path info/exclude",
        f"-C {pipeline_root} fetch --quiet --depth 1 --force origin refs/tags/v1:refs/tags/v1",
        f"-C {pipeline_root} checkout --quiet v1",
    ]
    assert args_file.read_text().splitlines() == [
        "--repo-root",
        str(repo),
        "--dry-run",
    ]


def test_client_ship_template_rejects_bad_explicit_pipeline_root(tmp_path):
    repo = make_client_repo(tmp_path)
    env = os.environ.copy()
    env["BTB_PIPELINE_ROOT"] = str(tmp_path / "missing-pipeline")

    result = run([str(repo / "scripts" / "ship"), "--dry-run"], repo, env=env, check=False)

    assert result.returncode == 1
    assert "BTB_PIPELINE_ROOT is set" in result.stderr


def test_client_ship_template_uses_git_path_for_worktree_exclude(tmp_path):
    repo, git_dir = make_worktree_client_repo(tmp_path)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    git_log = tmp_path / "git.log"
    args_file = tmp_path / "args.txt"
    fake_git = fake_bin / "git"
    write_executable(
        fake_git,
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {git_log}\n"
        'if [[ "$1" == "-C" && "$3" == "rev-parse" && "$4" == "--git-path" && "$5" == "info/exclude" ]]; then\n'
        '  printf "%s/info/exclude\\n" "$BTB_FAKE_GIT_DIR"\n'
        "  exit 0\n"
        "fi\n"
        'if [[ "$1" == "clone" ]]; then\n'
        '  destination="${@: -1}"\n'
        '  mkdir -p "$destination/scripts"\n'
        "  cat > \"$destination/scripts/btb-ship-base\" <<'EOF'\n"
        "#!/usr/bin/env bash\n"
        'printf \'%s\\n\' "$@" > "$BTB_BASE_ARGS_FILE"\n'
        "EOF\n"
        '  chmod +x "$destination/scripts/btb-ship-base"\n'
        "fi\n",
    )
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["BTB_BASE_ARGS_FILE"] = str(args_file)
    env["BTB_FAKE_GIT_DIR"] = str(git_dir)

    result = run([str(repo / "scripts" / "ship"), "--dry-run"], repo, env=env)

    assert result.returncode == 0, result.stderr
    assert git_log.read_text().splitlines()[0] == f"-C {repo} rev-parse --git-path info/exclude"
    assert (git_dir / "info" / "exclude").read_text().splitlines() == [
        "/.btb-pipeline/"
    ]
    assert not (repo / ".git" / "info" / "exclude").exists()
