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
    # millions: allow one decimal
    if num >= 1_000_000:
        rounded_num = round(num / 1_000_000, 1)
        if rounded_num.is_integer():
            return f"{int(rounded_num)}M"
        return f"{rounded_num:.1f}M"
    # for all totals under 1M, show thousands with no decimal
    thousands = round(num / 1_000)
    return f"{int(thousands)}K"

def font_to_base64(font_path):
    with open(font_path, 'rb') as font_file:
        return base64.b64encode(font_file.read()).decode('utf-8')

def draw_donut(data, county_name, output_dir):
    wedge_names = [k for k in data if k != 'Total']
    wedge_sizes = [data[k] for k in wedge_names]
    # Validate wedge sizes: skip if empty, all zeros, or contains only NaNs
    try:
        arr = np.array(wedge_sizes, dtype=float)
    except Exception:
        print(f"[SKIP] Invalid wedge data for {county_name}: {wedge_sizes}")
        return
    if arr.size == 0 or np.all(np.isnan(arr)) or np.nansum(arr) == 0:
        print(f"[SKIP] No valid data for {county_name}, skipping donut.")
        return
    colors = ['#005587', '#338F87', '#002E45']

    fig_width_inches = 3.0
    fig_height_inches = 3.0
    fig, ax = plt.subplots(
        figsize=(fig_width_inches, fig_height_inches),
        dpi=100,
        subplot_kw=dict(aspect="equal"),
        facecolor='none'
    )

    try:
        wedges, _ = ax.pie(
            wedge_sizes,
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='none')
        )
    except ValueError as e:
        # Matplotlib can raise ValueError if wedge sizes are invalid (e.g., NaN/empty)
        print(f"[SKIP] Matplotlib failed to draw donut for {county_name}: {e}")
        plt.close(fig)
        return

    centre_circle = plt.Circle((0, 0), 0.65, fc='none')
    ax.add_artist(centre_circle)
    ax.set_axis_off()

    total_str = format_total(data['Total'])
    parts = total_str.split()
    main_number = parts[0]
    main_unit = parts[1] if len(parts) > 1 else ''

    # Adjust center text positions
    center_fontsize = 18
    unit_fontsize   = 14
    label_fontsize  = 14

    # make the little bubble labels smaller for Imperial
    if county_name.lower() == "imperial":
        label_fontsize = 12     # drop from 14 to 12
        # optionally also shrink center text:
        center_fontsize -= 2    # now 16
        unit_fontsize   -= 2    # now 12

    wedge_angles = np.cumsum([0] + wedge_sizes) / sum(wedge_sizes) * 360

    bubble_radius = 0.35
    shadow_base   = 0.25
    if county_name.lower() == "imperial":
        # shrink both for Imperial
        bubble_radius -= 0.05    # now 0.30
        shadow_base   -= 0.05    # now 0.20

    # Modify the label placement logic to adjust both the radial distance and the angle
    # if bubbles are too close together.
    placed_labels = []  # store already placed label positions
    min_distance = 0.75  # minimum separation between bubble centers to avoid overlap (based on bubble radius)
    labels_overlapped = False  # flag to check if any labels overlap
    for i, w in enumerate(wedges):
        # Initial label position calculation
        orig_label_angle = (w.theta1 + w.theta2) / 2
        label_angle = orig_label_angle
        label_rad = 1.10  # initial radial position for label bubble
        label_x = label_rad * math.cos(math.radians(label_angle))
        label_y = label_rad * math.sin(math.radians(label_angle))
        
        # Adjust the label position repeatedly until no overlap occurs.
        attempts = 0
        while True:
            overlap = False
            for (prev_x, prev_y) in placed_labels:
                distance = math.sqrt((label_x - prev_x)**2 + (label_y - prev_y)**2)
                if distance < min_distance:
                    overlap = True
                    labels_overlapped = True  # set the flag if any overlap occurs
                    break
            # If no overlap, break out of loop.
            if not overlap:
                break
            # If overlapping, adjust the position:
            # Increase the radial distance and add a small horizontal offset based on the attempt count.
            label_rad += (min_distance - distance) * 0.5
            label_angle = orig_label_angle + (attempts * 2)  # shift angle by 2° per attempt
            label_x = label_rad * math.cos(math.radians(label_angle))
            label_y = label_rad * math.sin(math.radians(label_angle))
            attempts += 1
        
        placed_labels.append((label_x, label_y))
        
        # Draw shadow effect
        for j in range(1, 4):
            shadow_circle = Circle(
                (label_x, label_y),
                shadow_base + j*0.01,
                facecolor='#dedede',
                edgecolor='none',
                alpha=0.05 * (4-j),
                zorder=4-j
            )
            ax.add_patch(shadow_circle)
        
        # Draw main bubble circle
        circle = Circle(
            (label_x, label_y),
            bubble_radius,
            facecolor='#ffffff',
            edgecolor='#dedede',
            linewidth=1,
            zorder=5
        )
        ax.add_patch(circle)
        
		# Draw percentage label in the bubble (adjusted vertically for better centering)
        ax.text(
            label_x, label_y - 0.025,  # Adjusted the y-coordinate downward by 0.025
            f"{wedge_sizes[i]:.0f}%",
            ha='center', va='center', fontsize=label_fontsize,
            fontproperties=fp_bold,
            zorder=6, color='#000000'
        )

    # Adjust axis limits and font sizes if labels overlap
    if labels_overlapped:
        ax.set_xlim(-1.75, 1.75)
        ax.set_ylim(-1.75, 1.75)
        center_fontsize = 14  # decrease font size if labels overlap
        unit_fontsize = 10
        label_fontsize = 12  # decrease label font size if labels overlap
    else:
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)

    # Draw center text
    ax.text(
        0, -0.05, main_number,  # lowered from 0.05 to -0.05
        ha='center', va='center',
        fontproperties=fp_extra_bold,
        fontsize=center_fontsize, color='#000000'  # use adjusted font size
    )
    ax.text(
        0, -0.25, main_unit,  # lowered from -0.15 to -0.25
        ha='center', va='center',
        fontproperties=fp_semi_bold,
        fontsize=unit_fontsize, color='#000000'  # use adjusted font size
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

    # Standardize county name by replacing spaces with underscores
    county_filename = county_name.replace(" ", "_")
    # Set output directory to the fixed path
    output_dir = os.path.join("static", "extremeheat", "images", "population_donut")
    os.makedirs(output_dir, exist_ok=True)
    outfile = os.path.join(output_dir, f"{county_filename}_donut.svg")
    
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Saved {outfile}")