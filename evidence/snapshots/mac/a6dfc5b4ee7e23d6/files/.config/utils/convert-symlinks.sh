convert_symlinks() {
    for file in "$1"/*; do
        if [[ -h "$file" ]]; then
            target="$(readlink "$file")"
            cp "$target" "$file"
            rm "$file"
        elif [[ -d "$file" ]]; then
            convert_symlinks "$file"
        fi
    done
}