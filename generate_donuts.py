import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Circle
import math
from io import StringIO
import base64

# Register fonts
font_path_bold = "static/fonts/Lexend-Bold.ttf"
font_path_extra_bold = "static/fonts/Lexend-ExtraBold.ttf"
font_path_semi_bold = "static/fonts/Lexend-SemiBold.ttf"
for fpath in [font_path_bold, font_path_extra_bold, font_path_semi_bold]:
    try:
        fm.fontManager.addfont(fpath)
    except Exception as e:
        print(f"[ERROR-401] Failed to register font {fpath}: {e}")

fp_bold = fm.FontProperties(fname=font_path_bold)
fp_extra_bold = fm.FontProperties(fname=font_path_extra_bold)
fp_semi_bold = fm.FontProperties(fname=font_path_semi_bold)

def format_total(num):
    if num >= 1_000_000:
        rounded_num = round(num / 1_000_000, 1)
        if rounded_num.is_integer():
            return f"{int(rounded_num)}M"
        return f"{rounded_num:.1f}M"
    rounded_num = round(num / 1_000, 1)
    if rounded_num.is_integer():
        return f"{int(rounded_num)}K"
    return f"{rounded_num:.1f}K"

def font_to_base64(font_path):
    with open(font_path, 'rb') as font_file:
        return base64.b64encode(font_file.read()).decode('utf-8')

def draw_donut(data, county_name, output_dir):
    wedge_names = [k for k in data if k != 'Total']
    wedge_sizes = [data[k] for k in wedge_names]
    colors = ['#ac3434', '#ac6a34', '#333333']

    fig_width_inches = 3.0
    fig_height_inches = 3.0
    fig, ax = plt.subplots(
        figsize=(fig_width_inches, fig_height_inches),
        dpi=100,
        subplot_kw=dict(aspect="equal"),
        facecolor='none'
    )

    wedges, _ = ax.pie(
        wedge_sizes,
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.4, edgecolor='none')
    )

    centre_circle = plt.Circle((0, 0), 0.65, fc='none')
    ax.add_artist(centre_circle)
    ax.set_axis_off()

    total_str = format_total(data['Total'])
    parts = total_str.split()
    main_number = parts[0]
    main_unit = parts[1] if len(parts) > 1 else ''

    ax.text(
        0, 0.05, main_number,
        ha='center', va='center',
        fontproperties=fp_extra_bold,
        fontsize=16, color='#000000'
    )
    ax.text(
        0, -0.15, main_unit,
        ha='center', va='center',
        fontproperties=fp_semi_bold,
        fontsize=12, color='#000000'
    )

    wedge_angles = np.cumsum([0] + wedge_sizes) / sum(wedge_sizes) * 360
    for i, w in enumerate(wedges):
        angle = (wedge_angles[i] + wedge_angles[i+1]) / 2
        rad = 1.0
        x = rad * math.cos(math.radians(angle))
        y = rad * math.sin(math.radians(angle))

        # Calculate the centroid angle for the label and circle
        label_angle = (w.theta1 + w.theta2) / 2
        label_rad = 0.85  # Adjust this value to position the label closer or farther from the center
        label_x = label_rad * math.cos(math.radians(label_angle))
        label_y = label_rad * math.sin(math.radians(label_angle))

        # Draw shadow effect with multiple circles with transparency
        for j in range(1, 4):
            shadow_circle = Circle((label_x, label_y), 0.2 + j*0.01, facecolor='#dedede', edgecolor='none', alpha=0.05 * (4-j), zorder=4-j)
            ax.add_patch(shadow_circle)

        # Draw main circle
        circle = Circle((label_x, label_y), 0.2, facecolor='#ffffff', edgecolor='#dedede', linewidth=1, zorder=5)
        ax.add_patch(circle)

        # Draw label
        ax.text(
            label_x, label_y, f"{wedge_sizes[i]:.0f}%",
            ha='center', va='center', fontsize=10,
            fontproperties=fp_bold,
            zorder=6, color='#000000'
        )

    svg_io = StringIO()
    plt.savefig(svg_io, format='svg', bbox_inches='tight', transparent=True)
    plt.close(fig)

    svg_content = svg_io.getvalue()

    font_face = f"""
    <defs>
    <style type="text/css">
    @font-face {{
        font-family: 'Lexend-Bold';
        src: url('data:font/ttf;base64,{font_to_base64(font_path_bold)}') format('truetype');
    }}
    @font-face {{
        font-family: 'Lexend-ExtraBold';
        src: url('data:font/ttf;base64,{font_to_base64(font_path_extra_bold)}') format('truetype');
    }}
    @font-face {{
        font-family: 'Lexend-SemiBold';
        src: url('data:font/ttf;base64,{font_to_base64(font_path_semi_bold)}') format('truetype');
    }}
    </style>
    </defs>
    """

    if '<defs>' in svg_content:
        svg_content = svg_content.replace('<defs>', f'<defs>{font_face}')
    else:
        svg_content = svg_content.replace('<svg ', f'<svg {font_face}\n')

    os.makedirs(output_dir, exist_ok=True)
    outfile = os.path.join(output_dir, f"{county_name}_donut.svg")
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Saved {outfile}")