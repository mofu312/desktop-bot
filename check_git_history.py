"""Check if config.cfg was ever committed to git history."""
import subprocess, sys

def run(cmd):
    return subprocess.check_output(cmd, cwd=r"D:\ccwork\Resona-Desktop-Pet", text=True, stderr=subprocess.STDOUT)

print("=== Checking if config.cfg was ever committed ===")

# Check if config.cfg is in the current tree
try:
    result = run(["git", "ls-tree", "HEAD", "--", "config.cfg"])
    if result.strip():
        print("⚠️  config.cfg IS in the current HEAD tree:")
        print(result)
    else:
        print("✅ config.cfg is NOT in the current HEAD tree")
except subprocess.CalledProcessError:
    print("✅ config.cfg is NOT in the current HEAD tree")

# Check git log for config.cfg
try:
    result = run(["git", "log", "--all", "--oneline", "--", "config.cfg"])
    if result.strip():
        print("\n⚠️  config.cfg WAS committed in history:")
        print(result)
    else:
        print("\n✅ No history of config.cfg in any branch")
except subprocess.CalledProcessError:
    print("\n✅ No history of config.cfg found")

# Check if config.cfg is currently tracked (in index)
try:
    result = run(["git", "ls-files", "--", "config.cfg"])
    if result.strip():
        print("\n⚠️  config.cfg IS currently tracked (in git index)")
    else:
        print("\n✅ config.cfg is NOT tracked (correctly ignored)")
except subprocess.CalledProcessError:
    print("\n✅ config.cfg not in index")

# Check if .gitignore itself is tracked and current
try:
    result = run(["git", "ls-files", "--", ".gitignore"])
    if result.strip():
        print("\n✅ .gitignore is tracked")
except:
    pass

print("\n=== Done ===")
