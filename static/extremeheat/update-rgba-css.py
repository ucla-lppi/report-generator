import re

def fix_8digit_hex_colors(text):
    pattern = re.compile(r'#([A-Fa-f0-9]{8})')
    def replace_hex(match):
        hex_value = match.group(1)
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
        a = int(hex_value[6:8], 16) / 255.0
        return f'rgba({r}, {g}, {b}, {a:.2f})'
    return pattern.sub(replace_hex, text)

if __name__ == "__main__":
    with open("static\wextremeheat\wstyle.css", "r") as f:
        content = f.read()
    fixed_content = fix_8digit_hex_colors(content)
    with open("static\wextremeheat\wstyle.css", "w") as f:
        f.write(fixed_content)