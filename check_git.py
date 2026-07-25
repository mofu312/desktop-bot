"""
Pure Python git history checker - no subprocess needed.
Manually parses .git/objects/pack/* to find if config.cfg was ever committed.
Writes results to check_git_result.txt
"""
import zlib
import os
import struct
from pathlib import Path

OUTPUT = Path(r"D:\ccwork\Resona-Desktop-Pet\check_git_result.txt")
GIT_DIR = Path(r"D:\ccwork\Resona-Desktop-Pet\.git")
PACK_DIR = GIT_DIR / "objects" / "pack"

def find_pack_files():
    """Find .idx and .pack files."""
    idxs = list(PACK_DIR.glob("*.idx"))
    packs = list(PACK_DIR.glob("*.pack"))
    return idxs, packs

def parse_idx_v2(path):
    """Parse a version 2 .idx file. Returns dict: sha_hex -> pack_offset."""
    data = path.read_bytes()
    if data[:4] != b'\xff\x4f\x63\x74':
        # Not v2, try v1 or fail
        return {}
    version = struct.unpack('>I', data[4:8])[0]
    if version != 2:
        return {}

    # Fanout table: 256 entries of 4-byte uint32
    fanout = []
    for i in range(256):
        val = struct.unpack('>I', data[8 + i*4 : 8 + i*4 + 4])[0]
        fanout.append(val)

    total_objects = fanout[255]
    pos = 8 + 256*4  # After fanout

    # SHA-1 hashes (20 bytes each), sorted by SHA
    shas = []
    for i in range(total_objects):
        sha = data[pos + i*20 : pos + i*20 + 20].hex()
        shas.append(sha)
    pos += total_objects * 20

    # CRC32 (4 bytes each)
    pos += total_objects * 4

    # 4-byte offsets
    offsets_4byte = []
    for i in range(total_objects):
        off = struct.unpack('>I', data[pos + i*4 : pos + i*4 + 4])[0]
        offsets_4byte.append(off)
    pos += total_objects * 4

    # 8-byte offsets (for entries with MSB set in 4-byte offset)
    # Not needed if all offsets < 2^31

    result = {}
    for sha, off in zip(shas, offsets_4byte):
        if off & 0x80000000:
            # Large offset - get from 8-byte table
            idx_in_large = off & 0x7FFFFFFF
            off = struct.unpack('>Q', data[pos + idx_in_large*8 : pos + idx_in_large*8 + 8])[0]
        result[sha] = off

    return result


def read_pack_object(pack_path, offset):
    """Read and decompress a single object from a pack file."""
    with open(pack_path, 'rb') as f:
        f.seek(offset)

        # Read type+size header (variable-length encoding)
        byte = f.read(1)[0]
        obj_type = (byte >> 4) & 0x7
        size = byte & 0x0F
        shift = 4
        while byte & 0x80:
            byte = f.read(1)[0]
            size |= (byte & 0x7F) << shift
            shift += 7

        # Decompress
        decompressor = zlib.decompressobj()
        data = b''
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            data += decompressor.decompress(chunk)
            if decompressor.eof:
                # Put back unconsumed data?
                break

        type_map = {1: 'commit', 2: 'tree', 3: 'blob', 4: 'tag', 6: 'ofs_delta', 7: 'ref_delta'}
        return type_map.get(obj_type, f'unknown_{obj_type}'), data


def parse_tree(data):
    """Parse a tree object, return set of filenames (top-level only)."""
    names = set()
    rest = data
    while rest and rest.find(b'\x00') != -1:
        space = rest.find(b' ')
        null = rest.find(b'\x00')
        name = rest[space+1:null].decode('utf-8', errors='replace')
        names.add(name)
        rest = rest[null+21:]  # skip null + 20-byte SHA
    return names


def walk_history(sha_to_offset, pack_path, start_sha):
    """Walk commit history starting from start_sha, checking each commit for config.cfg."""
    commits_checked = []
    found_in = []

    visited = set()
    to_visit = [start_sha]

    while to_visit:
        sha = to_visit.pop(0)
        if sha in visited:
            continue
        visited.add(sha)

        if sha not in sha_to_offset:
            continue

        try:
            obj_type, data = read_pack_object(pack_path, sha_to_offset[sha])
        except Exception:
            continue

        if obj_type != 'commit':
            continue

        text = data.decode('utf-8', errors='replace')
        tree_sha = None
        parents = []
        commit_msg = ''

        for line in text.split('\n'):
            if line.startswith('tree '):
                tree_sha = line.split()[1].strip()
            elif line.startswith('parent '):
                parents.append(line.split()[1].strip())
            elif line.strip() and not line.startswith('author ') and not line.startswith('committer '):
                commit_msg = line.strip()

        # Get author line for display
        author = ''
        for line in text.split('\n'):
            if line.startswith('author '):
                author = line[len('author '):].strip()
                break

        commits_checked.append((sha, commit_msg, author))

        # Check tree for config.cfg
        if tree_sha and tree_sha in sha_to_offset:
            try:
                tree_type, tree_data = read_pack_object(pack_path, sha_to_offset[tree_sha])
                if tree_type == 'tree':
                    names = parse_tree(tree_data)
                    if 'config.cfg' in names:
                        found_in.append((sha, commit_msg, author))
            except Exception:
                pass

        for p in parents:
            if p not in visited:
                to_visit.append(p)

    return commits_checked, found_in


def check_tags(sha_to_offset, pack_path):
    """Check all tag refs too."""
    refs_dir = GIT_DIR / "refs" / "tags"
    packed = GIT_DIR / "packed-refs"
    tag_shas = {}

    if packed.exists():
        for line in packed.read_text().splitlines():
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            parts = line.split()
            if parts:
                tag_shas[parts[0]] = f"tag:{parts[-1] if len(parts)>1 else 'unknown'}"

    return tag_shas


def check_index():
    """Read .git/index and check if config.cfg is tracked."""
    idx_path = GIT_DIR / "index"
    if not idx_path.exists():
        return None

    data = idx_path.read_bytes()
    # Index entries have null-terminated paths. Search for config.cfg
    # with proper framing (after mode/sha, before null)
    if b'config.cfg\x00' in data:
        return True
    return False


def main():
    lines = []
    lines.append("=== Git History Check for config.cfg ===")
    lines.append(f"Repository: D:\\ccwork\\Resona-Desktop-Pet")
    lines.append("")

    # Parse pack files
    idxs, packs = find_pack_files()
    if not idxs:
        lines.append("ERROR: No pack .idx files found!")
        OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
        return

    lines.append(f"Found {len(idxs)} idx, {len(packs)} pack file(s)")

    # Parse all idx files into one SHA->offset map
    sha_to_offset = {}
    for idx_path in idxs:
        pack_path = idx_path.with_suffix(".pack")
        if not pack_path.exists():
            continue
        result = parse_idx_v2(idx_path)
        sha_to_offset.update(result)
        lines.append(f"  Parsed {idx_path.name}: {len(result)} objects")

    lines.append(f"  Total objects: {len(sha_to_offset)}")
    lines.append("")

    # Get HEAD
    head_path = GIT_DIR / "HEAD"
    if head_path.exists():
        head_content = head_path.read_text().strip()
        if head_content.startswith("ref: "):
            ref_path = head_content[5:]
            ref_file = GIT_DIR / ref_path
            if ref_file.exists():
                head_sha = ref_file.read_text().strip()
                lines.append(f"HEAD: {head_sha} (ref: {ref_path})")
            else:
                head_sha = None
                lines.append("HEAD ref file not found!")
        else:
            head_sha = head_content
            lines.append(f"HEAD (detached): {head_sha}")
    else:
        head_sha = None
        lines.append("HEAD file not found!")

    lines.append("")

    # Walk history
    if head_sha and head_sha in sha_to_offset:
        pack_path = idxs[0].with_suffix(".pack")
        commits, found = walk_history(sha_to_offset, pack_path, head_sha)

        lines.append(f"=== Commits checked: {len(commits)} ===")
        for sha, msg, author in commits:
            lines.append(f"  {sha[:8]} - {msg[:60]}")
        lines.append("")

        if found:
            lines.append("⚠️  config.cfg FOUND in these commits:")
            for sha, msg, author in found:
                lines.append(f"  {sha[:8]} - {msg[:60]}")
                lines.append(f"    Author: {author}")
        else:
            lines.append("✅ config.cfg NOT found in any commit's tree")
    else:
        lines.append("WARNING: Cannot read HEAD commit (SHA not in pack index)")

    lines.append("")

    # Check git index (staging area)
    in_index = check_index()
    if in_index is True:
        lines.append("⚠️  config.cfg IS tracked in git index (staging area)")
        lines.append("    .gitignore won't help until you: git rm --cached config.cfg")
    elif in_index is False:
        lines.append("✅ config.cfg is NOT tracked in git index")
    else:
        lines.append("? Cannot check git index")

    lines.append("")
    lines.append("=== Done ===")

    OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
    print("Results written to check_git_result.txt")

if __name__ == "__main__":
    main()
