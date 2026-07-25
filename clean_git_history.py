"""
清理 Git 历史中的 config.cfg（含 API 密钥）
使用 git filter-repo 或 git filter-branch 从所有历史中移除敏感文件
"""
import subprocess
import os
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SENSITIVE_FILES = ["config.cfg"]

def run_git(args, check=True):
    """运行 git 命令"""
    print(f"  [RUN] git {' '.join(args)}")
    result = subprocess.run(
        ["git"] + args,
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        print(f"  [FAIL] git {' '.join(args)} returned {result.returncode}")
        sys.exit(1)
    return result

def check_tracked():
    """检查 config.cfg 是否被 git 追踪"""
    result = subprocess.run(
        ["git", "ls-files", "config.cfg"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print(f"[INFO] config.cfg 已被 git 追踪，将从历史中移除")
        return True
    else:
        print(f"[INFO] config.cfg 未被 git 追踪（可能已在 .gitignore 中或已移除）")
        result2 = subprocess.run(
            ["git", "log", "--all", "--oneline", "--", "config.cfg"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
        )
        if result2.stdout.strip():
            print(f"[WARN] 但 config.cfg 仍存在于历史记录中：")
            print(result2.stdout.strip())
            return True
        else:
            print(f"[INFO] config.cfg 不在 git 历史中，无需清理")
            return False

def check_remote():
    """检查远程仓库"""
    result = subprocess.run(
        ["git", "remote", "-v"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    print(f"[INFO] 远程仓库：\n{result.stdout.strip()}")
    if "github.com" in result.stdout.lower() or "gitlab" in result.stdout.lower():
        print(f"[WARN] ⚠️  检测到公开平台远程仓库！密钥可能已泄露！")
        print(f"[WARN] 清理历史后必须 force push，并立即去对应平台轮换 API 密钥！")
        return True
    return False

def filter_branch_clean():
    """
    使用 git filter-branch 删除敏感文件
    """
    print(f"\n{'='*60}")
    print(f"[STEP] 使用 git filter-branch 从所有历史中删除敏感文件")
    print(f"{'='*60}\n")

    file_list = " ".join(SENSITIVE_FILES)

    # 使用 index-filter 逐个删除文件，这比 tree-filter 快很多
    cmd = [
        "git", "filter-branch", "--force", "--index-filter",
        f'git rm --cached --ignore-unmatch {file_list}',
        "--prune-empty", "--tag-name-filter", "cat", "--", "--all"
    ]

    print(f"[RUN] git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch {file_list}' --prune-empty --tag-name-filter cat -- --all")
    result = subprocess.run(
        cmd,
        cwd=REPO_DIR,
        capture_output=False,  # 让输出直接显示
    )
    if result.returncode != 0:
        print(f"[FAIL] filter-branch 失败，返回 {result.returncode}")
        sys.exit(1)
    print(f"[OK] filter-branch 完成")

def clean_refs():
    """清理 reflog 和垃圾回收"""
    print(f"\n{'='*60}")
    print(f"[STEP] 清理引用和垃圾回收")
    print(f"{'='*60}\n")

    # 删除 backup refs
    result = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)", "refs/original/"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    for ref in result.stdout.strip().split("\n"):
        if ref:
            run_git(["update-ref", "-d", ref], check=False)

    # 清理 reflog
    run_git(["reflog", "expire", "--expire=now", "--all"])
    # 垃圾回收
    run_git(["gc", "--prune=now", "--aggressive"])

    print(f"[OK] 清理完成")

def verify_clean():
    """验证清理结果"""
    print(f"\n{'='*60}")
    print(f"[STEP] 验证清理结果")
    print(f"{'='*60}\n")

    result = subprocess.run(
        ["git", "log", "--all", "--oneline", "--", "config.cfg"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print(f"[WARN] config.cfg 仍在历史中：")
        print(result.stdout.strip())
    else:
        print(f"[OK] config.cfg 已从所有历史中移除 ✓")

def main():
    print(f"[INFO] 仓库目录: {REPO_DIR}")
    print(f"[INFO] 敏感文件: {SENSITIVE_FILES}")

    if not check_tracked():
        # 再检查一下历史
        result = subprocess.run(
            ["git", "log", "--all", "--oneline", "--", "config.cfg"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            print("[INFO] 无需清理，退出")
            return

    has_remote = check_remote()

    print(f"\n[WARN] ==============================================")
    print(f"[WARN]  即将从 Git 历史中永久删除 config.cfg")
    print(f"[WARN]  这个操作不可逆！")
    print(f"[WARN] ==============================================")

    # 自动执行（如果你想加确认，取消下面的注释）
    # answer = input("\n确认继续？(y/N): ")
    # if answer.lower() != 'y':
    #     print("已取消")
    #     return

    filter_branch_clean()
    clean_refs()
    verify_clean()

    print(f"\n{'='*60}")
    print(f"[DONE] 清理完成！")
    print(f"{'='*60}")
    if has_remote:
        print(f"[TODO] 接下来你需要手动执行：")
        print(f"       1. git push origin --force --all")
        print(f"       2. git push origin --force --tags")
        print(f"       3. 去对应平台轮换所有已泄露的 API 密钥！")
        print(f"       4. 通知其他协作者重新 clone 仓库")
    else:
        print(f"[TODO] 如有远程仓库，执行 force push")


if __name__ == "__main__":
    main()
