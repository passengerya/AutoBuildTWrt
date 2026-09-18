#!/bin/sh

BASE_DIR="extra-packages"
TEMP_DIR="$BASE_DIR/temp-unpack"
TARGET_DIR="packages"
DIAG_DIR="${BUILD_LOG_DIR:-$TARGET_DIR}"
INVENTORY="$DIAG_DIR/package-inventory-ipk.tsv"
BASENAME_DUP_REPORT="$DIAG_DIR/package-duplicate-basenames-ipk.txt"
LOGICAL_DUP_REPORT="$DIAG_DIR/package-duplicate-names-ipk.txt"
CANDIDATE_LIST="$TEMP_DIR/ipk-candidates.list"
TAB="$(printf '\t')"

ipk_field() {
    pkg="$1"
    field="$2"
    control_member="$(tar -tzf "$pkg" 2>/dev/null | grep '/control.tar.gz$' | head -n 1)"
    [ -n "$control_member" ] || control_member="$(tar -tzf "$pkg" 2>/dev/null | grep '^control.tar.gz$' | head -n 1)"

    if [ -n "$control_member" ]; then
        for control_file in ./control control; do
            value="$(tar -xOzf "$pkg" "$control_member" 2>/dev/null | tar -xzO "$control_file" 2>/dev/null | awk -F': ' -v field="$field" '$1 == field { print $2; exit }')"
            if [ -n "$value" ]; then
                printf '%s\n' "$value"
                return 0
            fi
        done
    fi

    if command -v ar >/dev/null 2>&1; then
        for control_file in ./control control; do
            value="$(ar p "$pkg" control.tar.gz 2>/dev/null | tar -xzO "$control_file" 2>/dev/null | awk -F': ' -v field="$field" '$1 == field { print $2; exit }')"
            if [ -n "$value" ]; then
                printf '%s\n' "$value"
                return 0
            fi
        done
    fi

    return 1
}

ipk_name_from_filename() {
    name="${1##*/}"
    name="${name%.ipk}"
    name="$(printf '%s\n' "$name" | sed -E 's/[_-](all|x86_64|aarch64([._-][A-Za-z0-9.-]+)?|arm_[A-Za-z0-9._-]+|mips(el)?_[A-Za-z0-9._-]+|i386(_[A-Za-z0-9._-]+)?)$//')"
    printf '%s\n' "$name" | awk -F_ '
        BEGIN { OFS = "_" }
        {
            for (i = NF; i > 1; i--) {
                if ($i ~ /^(v?[0-9]|r[0-9]|git-)/) {
                    for (j = 1; j < i; j++) {
                        printf "%s%s", (j > 1 ? OFS : ""), $j
                    }
                    printf "\n"
                    exit
                }
            }
            print $0
        }'
}

arch_from_filename() {
    name="${1##*/}"
    case "$name" in
        *_all.ipk|*-all.ipk) printf '%s\n' all ;;
        *_x86_64.ipk) printf '%s\n' x86_64 ;;
        *_aarch64*.ipk) printf '%s\n' aarch64 ;;
        *_i386*.ipk) printf '%s\n' i386 ;;
        *) printf '%s\n' unknown ;;
    esac
}

write_inventory_row() {
    pkg="$1"
    base="${pkg##*/}"
    pkg_name="$(ipk_field "$pkg" Package 2>/dev/null || true)"
    name_source="metadata"
    if [ -z "$pkg_name" ]; then
        pkg_name="$(ipk_name_from_filename "$base")"
        name_source="filename"
    fi
    version="$(ipk_field "$pkg" Version 2>/dev/null || true)"
    arch="$(ipk_field "$pkg" Architecture 2>/dev/null || true)"
    [ -n "$arch" ] || arch="$(arch_from_filename "$base")"
    printf 'ipk%s%s%s%s%s%s%s%s%s%s%s%s%s\n' "$TAB" "$pkg" "$TAB" "$base" "$TAB" "$pkg_name" "$TAB" "$version" "$TAB" "$arch" "$TAB" "$name_source" >> "$INVENTORY"
}

# 清理旧的目录
rm -rf "$TEMP_DIR" "$TARGET_DIR"
mkdir -p "$TEMP_DIR" "$TARGET_DIR" "$DIAG_DIR"

# 解压 .run 文件（仅 ipk 通道：跳过 25_/25- 前缀的 apk 通道包）
for run_file in "$BASE_DIR"/*.run; do
    [ -e "$run_file" ] || continue
    case "$run_file" in
        */25_*|*/25-*) echo "⏭️ 跳过 apk 通道包 $run_file"; continue ;;
    esac
    echo "🧩 解压 $run_file -> $TEMP_DIR"
    if ! sh "$run_file" --target "$TEMP_DIR" --noexec; then
        echo "❌ 解压失败: $run_file"
        exit 1
    fi
done

: > "$CANDIDATE_LIST"
find "$TEMP_DIR" -type f -name "*.ipk" -print >> "$CANDIDATE_LIST"
find "$BASE_DIR" -mindepth 2 -maxdepth 2 -type f -name "*.ipk" ! -path "$TEMP_DIR/*" -print >> "$CANDIDATE_LIST"

# 剔除冗余/冲突包(名单与 store/sync_run_files.py 的 EXCLUDED_PACKAGE_RE 保持一致):
# store 中可能仍保留历史旧 .run(内含已被剔除的包, 如 easytier-noweb,
# 在新资产同步前不会被替换), 这里兜底过滤, 防止其重新进入 packages/ 被烘焙。
EXCLUDED_PKG_RE='^(easytier-noweb|luci-i18n-easytier-zh-cn)[-_].*\.ipk$'
: > "$CANDIDATE_LIST.filtered"
while IFS= read -r pkg; do
    [ -n "$pkg" ] || continue
    base="${pkg##*/}"
    if printf '%s\n' "$base" | grep -qE "$EXCLUDED_PKG_RE"; then
        echo "⏭️ 剔除冗余/冲突包: $base"
    else
        printf '%s\n' "$pkg" >> "$CANDIDATE_LIST.filtered"
    fi
done < "$CANDIDATE_LIST"
mv "$CANDIDATE_LIST.filtered" "$CANDIDATE_LIST"

if [ ! -s "$CANDIDATE_LIST" ]; then
    echo "❌ 未找到任何 ipk 软件包, 无法继续构建第三方软件包列表"
    exit 1
fi

printf 'channel%ssource%sbasename%spackage%sversion%sarchitecture%sname_source\n' "$TAB" "$TAB" "$TAB" "$TAB" "$TAB" "$TAB" > "$INVENTORY"
while IFS= read -r pkg; do
    [ -n "$pkg" ] || continue
    write_inventory_row "$pkg"
done < "$CANDIDATE_LIST"

# 1. 重名文件检查: 内容不同才算错误(复制会覆盖); 内容一致仅记录诊断
awk -F "$TAB" 'NR > 1 { count[$3]++ } END { for (k in count) if (count[k] > 1) print k }' "$INVENTORY" | sort > "$BASENAME_DUP_REPORT"
duplicate_conflict=0
if [ -s "$BASENAME_DUP_REPORT" ]; then
    : > "$BASENAME_DUP_REPORT.details"
    while IFS= read -r basename; do
        echo "basename: $basename" >> "$BASENAME_DUP_REPORT.details"
        first_source=""
        for source in $(awk -F "$TAB" -v wanted="$basename" 'NR > 1 && $3 == wanted { print $2 }' "$INVENTORY"); do
            echo "  $source" >> "$BASENAME_DUP_REPORT.details"
            if [ -z "$first_source" ]; then
                first_source="$source"
            elif ! cmp -s "$first_source" "$source"; then
                duplicate_conflict=1
                echo "  ❌ 内容不同: $first_source <> $source" >> "$BASENAME_DUP_REPORT.details"
            fi
        done
    done < "$BASENAME_DUP_REPORT"
    mv "$BASENAME_DUP_REPORT.details" "$BASENAME_DUP_REPORT"
    if [ "$duplicate_conflict" -ne 0 ]; then
        echo "⚠️ 检测到内容不同的重复 ipk 文件名(复制到 packages/ 时按序覆盖, 与旧行为一致; 生效的是清单中最后一份):"
        cat "$BASENAME_DUP_REPORT"
    else
        echo "⚠️ 检测到重复 ipk 文件名, 内容完全一致; 已保留诊断记录: $BASENAME_DUP_REPORT"
        cat "$BASENAME_DUP_REPORT"
    fi
else
    echo "未检测到重复 ipk 文件名"
fi

# 2. 逻辑包名重复检查: 仅告警(依赖包常被多个应用目录重复携带, 属已知现象)
awk -F "$TAB" 'NR > 1 { count[$4]++; paths[$4] = paths[$4] "\n  " $2 " (" $5 ", " $6 ", " $7 ")" } END { for (k in count) if (k != "" && count[k] > 1) print k paths[k] }' "$INVENTORY" > "$LOGICAL_DUP_REPORT"
if [ -s "$LOGICAL_DUP_REPORT" ]; then
    echo "⚠️ 检测到重复 ipk 包名, 已写入诊断报告: $LOGICAL_DUP_REPORT"
    cat "$LOGICAL_DUP_REPORT"
fi

while IFS= read -r pkg; do
    [ -n "$pkg" ] || continue
    echo "👉 Found: $pkg"
    cp -v "$pkg" "$TARGET_DIR"/
done < "$CANDIDATE_LIST"

echo "✅ 所有 .ipk 文件已整理至 $TARGET_DIR/"
echo "🧾 ipk 软件包清单: $INVENTORY"
