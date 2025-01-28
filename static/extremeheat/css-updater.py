import re

def update_css_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        css = f.read()
    print("[DEBUG] Original CSS length:", len(css))

    font_mappings = {
        100: 'Lexend-Thin',
        200: 'Lexend-ExtraLight',
        300: 'Lexend-Light',
        400: 'Lexend-Regular',
        500: 'Lexend-Medium',
        600: 'Lexend-SemiBold',
        700: 'Lexend-Bold',
        800: 'Lexend-ExtraBold',
        900: 'Lexend-Black'
    }

    # 1) Update @font-face blocks:
    #    Matches either font-family: 'Lexend' or font-family: "Lexend"
    for w, fam in font_mappings.items():
        print(f"[DEBUG] Checking @font-face for weight {w} -> {fam}")
        block_pattern = (
            rf"(@font-face\s*\{{[^}}]*?"
            rf"font-family:\s*[\"']Lexend[\"']\s*;\s*"
            rf"font-style:\s*normal\s*;\s*"
            rf"font-weight:\s*{w}\s*;"
            rf"[^}}]*?\}})"
        )
        block_matches = re.findall(block_pattern, css, flags=re.DOTALL)
        if block_matches:
            print(f"[DEBUG] Found {len(block_matches)} block match(es) for weight {w}")
            for i, block in enumerate(block_matches, 1):
                print(f"[DEBUG] @font-face match #{i}:\n{block}\n---")
        # Replace
        css = re.sub(
            block_pattern,
            lambda m: m.group(0).replace('font-family: "Lexend";',  f'font-family: "{fam}";')
                               .replace("font-family: 'Lexend';", f"font-family: '{fam}';"),
            css,
            flags=re.DOTALL
        )

    # 2) Update in-rule usage:
    #    Matches either font-family: "Lexend", Helvetica OR font-family: 'Lexend', Helvetica
    #    Possibly on separate lines, so we run DOTALL as well.
    for w, fam in font_mappings.items():
        print(f"[DEBUG] Checking usage in rules for weight {w} -> {fam}")
        usage_pattern = (
            rf"(font-family:\s*[\"']Lexend[\"'],\s*Helvetica\s*;[^;]*font-weight:\s*{w}\s*;)"
        )
        usage_matches = re.findall(usage_pattern, css, flags=re.DOTALL)
        if usage_matches:
            print(f"[DEBUG] Found {len(usage_matches)} usage match(es) for weight {w}")
            for i, match in enumerate(usage_matches, 1):
                print(f"[DEBUG] Usage match #{i}:\n{match}\n---")
        # Replace
        css = re.sub(
            usage_pattern,
            lambda m: m.group(0)
                .replace('font-family: "Lexend", Helvetica;',  f'font-family: "{fam}", Helvetica;')
                .replace("font-family: 'Lexend', Helvetica;", f"font-family: '{fam}', Helvetica;"),
            css,
            flags=re.DOTALL
        )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(css)

    print("[DEBUG] Updated CSS length:", len(css))

if __name__ == "__main__":
    css_file_path = "c:/Users/hikou/repos/ucla/lppi/report-generator/static/extremeheat/style.css"
    update_css_file(css_file_path)