import re

def simplify_css(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        css = f.read()
    
    # Example transformations:
    # 1. Remove @import lines (some PDF renderers ignore remote fonts).
    # css = re.sub(r"@import\s+url\('[^']+'\);\s*", "", css)

    # 2. Replace box-shadow with simpler syntax or remove entirely.
    css = re.sub(r"box-shadow:[^;]+;", "box-shadow: 1px 1px 4px rgba(0,0,0,0.25);", css)

    # 3. Remove absolute positioning if necessary.
    # css = re.sub(r"position:\s*absolute\s*;\s*", "", css)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(css)



if __name__ == "__main__":
    with open("static\\extremeheat\\style.css", "r") as f:
        content = f.read()
    simplify_css("static\\extremeheat\\style.css", "static\\extremeheat\\style.css")

