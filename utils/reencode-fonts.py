import os
import base64

def embed_fonts_in_css(fonts_path, css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        existing_css = f.read()

    new_rules = []
    for filename in os.listdir(fonts_path):
        if filename.endswith(".ttf"):
            weight = 700 if "Bold" in filename else 400
            font_path = os.path.join(fonts_path, filename)
            with open(font_path, "rb") as f:
                encoded_data = base64.b64encode(f.read()).decode("utf-8")

            new_rules.append(
                f"@font-face {{\n"
                f"    font-family: 'MyFont';\n"
                f"    font-weight: {weight};\n"
                f"    src: url(data:font/truetype;base64,{encoded_data}) format('truetype');\n"
                f"}}\n"
            )

    with open(css_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_rules) + "\n" + existing_css)
        
if __name__ == "__main__":
    embed_fonts_in_css(
        r"..\static\extremeheat\fonts",
        r"..\static\extremeheat\style.css"
    )