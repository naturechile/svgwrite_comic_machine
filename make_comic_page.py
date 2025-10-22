import svgwrite
import math

# --- Geometry Helper Functions (ADDED/MOVED) ---

def add_shift(point, shift):
    """Helper to add a 2D shift vector to a point."""
    return (point[0] + shift[0], point[1] + shift[1])

def get_normal_shift_vector(p1, p2, magnitude, direction='right'):
    """
    Calculates the unit vector perpendicular to the line segment (p1, p2) and scales it by magnitude.
    'right' shifts in the direction of (Vy, -Vx). 'left' shifts in the direction of (-Vy, Vx).
    """
    V_x = p2[0] - p1[0] 
    V_y = p2[1] - p1[1] 
    
    # Calculate the Normal Vector (perpendicular to V)
    if direction == 'right':
        N_x = V_y
        N_y = -V_x
    else: # 'left'
        N_x = -V_y
        N_y = V_x
    
    N_magnitude = math.sqrt(N_x**2 + N_y**2)
    
    if N_magnitude == 0:
        return (0, 0)

    # Unit Normal Vector U
    U_x = N_x / N_magnitude
    U_y = N_y / N_magnitude

    # Final Shift Vector S
    S_x = U_x * magnitude
    S_y = U_y * magnitude
    return (S_x, S_y)

def get_line_intersection(p1, p2, p3, p4):
    """
    Finds the intersection point of two infinite lines defined by (p1, p2) and (p3, p4).
    Returns (x, y) or None if parallel/collinear.
    """
    a1 = p2[1] - p1[1]
    b1 = p1[0] - p2[0]
    c1 = a1 * p1[0] + b1 * p1[1]

    a2 = p4[1] - p3[1]
    b2 = p3[0] - p4[0]
    c2 = a2 * p3[0] + b2 * p3[1]

    det = a1 * b2 - a2 * b1

    if det == 0:
        return None  # Parallel or collinear

    x = (b2 * c1 - b1 * c2) / det
    y = (a1 * c2 - a2 * c1) / det
    return (x, y)

# --- Main Drawing Logic ---

def draw_split_panels(dwg, x_start_p1, y_top, panel_width, panel_height, gutter, panel_stroke, panel_fill, split_type, split_params):
    """
    Helper function to draw two adjacent panels (Panel 1 and Panel 2) 
    split by a dynamic line (arrow, straight, or lightning) with a gutter in between.
    """
    
    # 1. Calculate boundaries for Panel 1 (P1) and Panel 2 (P2)
    P1_WIDTH = (panel_width - gutter) / 2
    
    x_end_p1 = x_start_p1 + P1_WIDTH
    x_start_p2 = x_end_p1 + gutter
    x_end_p2 = x_start_p2 + P1_WIDTH # P1_WIDTH is also P2_WIDTH
    
    y_bottom = y_top + panel_height
    
    # Extract ratios for the main line start/end points (used by all types)
    top_x_ratio = split_params.get('top_x_ratio', 1.3)
    bot_x_ratio = split_params.get('bot_x_ratio', 0.7)
    
    # Initialize point lists
    p1_points = []
    p2_points = []

    # Helper function to calculate X coordinate based on ratio relative to P1's start
    def calc_x_ratio(ratio):
        return x_start_p1 + P1_WIDTH * ratio 

    # 2. Define the coordinates for the split line based on split_type
    
    if split_type == 'straight':
        # Straight Diagonal Split (4 vertices for P1, 4 for P2)
        
        # P1 Boundary Points (Left Side of Gutter)
        P1_TOP_L = (calc_x_ratio(top_x_ratio), y_top) 
        P1_BOT_L = (calc_x_ratio(bot_x_ratio), y_bottom) 
        
        # P2 Boundary Points (Right Side of Gutter)
        P2_TOP_R = (P1_TOP_L[0] + gutter, P1_TOP_L[1])
        P2_BOT_R = (P1_BOT_L[0] + gutter, P1_BOT_L[1])
        
        # Panel 1 (Left Panel) Points (Clockwise)
        p1_points = [
            (x_start_p1, y_top),     # Top-Left (TL)
            P1_TOP_L,                # Diagonal Start (Top)
            P1_BOT_L,                # Diagonal End (Bottom)
            (x_start_p1, y_bottom)   # Bottom-Left (BL)
        ]
        
        # Panel 2 (Right Panel) Points (Clockwise)
        p2_points = [
            (x_end_p2, y_top),       # Top-Right (TR) - START
            (x_end_p2, y_bottom),    # Bottom-Right (BR)
            (x_start_p2, y_bottom),  # Bottom-Left corner of P2
            P2_BOT_R,                # Diagonal End (Bottom)
            P2_TOP_R                 # Diagonal Start (Top)
        ]

    elif split_type == 'arrow':
        # Arrow Split (5 vertices for P1, 6 for P2)
        
        mid_y_ratio = split_params.get('mid_y_ratio', 0.5)
        depth_x_ratio = split_params.get('depth_x_ratio', 0.8)
        
        # P1 Boundary Points (Left Side of Gutter)
        P1_TOP_L = (calc_x_ratio(top_x_ratio), y_top) 
        P1_MID_L = (calc_x_ratio(depth_x_ratio), y_top + panel_height * mid_y_ratio) # Arrow Tip
        P1_BOT_L = (calc_x_ratio(bot_x_ratio), y_bottom) 
        
        # P2 Boundary Points (Right Side of Gutter)
        P2_TOP_R = (P1_TOP_L[0] + gutter, P1_TOP_L[1])
        P2_MID_R = (P1_MID_L[0] + gutter, P1_MID_L[1])
        P2_BOT_R = (P1_BOT_L[0] + gutter, P1_BOT_L[1])
        
        # Panel 1 (Left Panel) Points (Clockwise)
        p1_points = [
            (x_start_p1, y_top),     # TL
            P1_TOP_L,                # Diagonal Start (Top)
            P1_MID_L,                # Arrow Tip (Middle)
            P1_BOT_L,                # Diagonal End (Bottom)
            (x_start_p1, y_bottom)   # BL
        ]

        # Panel 2 (Right Panel) Points (Clockwise)
        p2_points = [
            (x_end_p2, y_top),       # TR - START
            (x_end_p2, y_bottom),    # BR
            (x_start_p2, y_bottom),  # BL corner of P2
            P2_BOT_R,                # Diagonal End (Bottom)
            P2_MID_R,                # Arrow Indent (Middle)
            P2_TOP_R                 # Diagonal Start (Top)
        ]

    elif split_type == 'lightning':
        
        # --- NEW STABLE LIGHTNING GEOMETRY ---
        
        # Get point ratios from parameters
        zig_y_ratio = split_params.get('zig_y_ratio', 0.60)
        zig_depth_x_ratio = split_params.get('zig_depth_x_ratio', 1.0)
        zag_y_ratio = split_params.get('zag_y_ratio', 0.55)
        zag_depth_x_ratio = split_params.get('zag_depth_x_ratio', 0.9)
        
        SHIFT = gutter / 2.0
        Y_TOP = y_top
        Y_BOTTOM = y_bottom
        
        # 1. CENTER LINE (A_C to D_C) POINTS
        # These points define the geometric core of the lightning bolt.
        A_C = (calc_x_ratio(top_x_ratio), Y_TOP) 
        B_C = (calc_x_ratio(zig_depth_x_ratio), Y_TOP + panel_height * zig_y_ratio)
        C_C = (calc_x_ratio(zag_depth_x_ratio), Y_TOP + panel_height * zag_y_ratio)
        D_C = (calc_x_ratio(bot_x_ratio), Y_BOTTOM)

        # 2. CALCULATE SHIFT VECTORS
        S_AB_R = get_normal_shift_vector(A_C, B_C, SHIFT, 'right')
        S_BC_R = get_normal_shift_vector(B_C, C_C, SHIFT, 'right')
        S_CD_R = get_normal_shift_vector(C_C, D_C, SHIFT, 'right')
        S_AB_L = get_normal_shift_vector(A_C, B_C, SHIFT, 'left')
        S_BC_L = get_normal_shift_vector(B_C, C_C, SHIFT, 'left')
        S_CD_L = get_normal_shift_vector(C_C, D_C, SHIFT, 'left')

        # 3. CALCULATE RAW SHIFTED POINTS
        E_raw = add_shift(A_C, S_AB_R)
        B_prime_AB_R = add_shift(B_C, S_AB_R)
        B_prime_BC_R = add_shift(B_C, S_BC_R)
        C_prime_BC_R = add_shift(C_C, S_BC_R)
        C_prime_CD_R = add_shift(C_C, S_CD_R)
        D_prime_R = add_shift(D_C, S_CD_R) 
        I_raw = add_shift(A_C, S_AB_L)
        B_prime_AB_L = add_shift(B_C, S_AB_L)
        B_prime_BC_L = add_shift(B_C, S_BC_L)
        C_prime_BC_L = add_shift(C_C, S_BC_L)
        C_prime_CD_L = add_shift(C_C, S_CD_L)
        D_prime_L = add_shift(D_C, S_CD_L) 

        # 4. CALCULATE INTERSECTIONS (The four jagged corner points: F, G, J, K)
        F = get_line_intersection(E_raw, B_prime_AB_R, B_prime_BC_R, C_prime_BC_R)
        if F is None: F = B_prime_AB_R 
        G = get_line_intersection(B_prime_BC_R, C_prime_BC_R, C_prime_CD_R, D_prime_R)
        if G is None: G = C_prime_BC_R 
        J = get_line_intersection(I_raw, B_prime_AB_L, B_prime_BC_L, C_prime_BC_L)
        if J is None: J = B_prime_AB_L 
        K = get_line_intersection(B_prime_BC_L, C_prime_BC_L, C_prime_CD_L, D_prime_L)
        if K is None: K = C_prime_BC_L 

        # 5. CALCULATE TOP/BOTTOM EDGE INTERSECTIONS to seal the panel
        TOP_EDGE_P1 = (x_start_p1, Y_TOP)
        TOP_EDGE_P2 = (x_end_p2, Y_TOP)
        BOT_EDGE_P1 = (x_start_p1, Y_BOTTOM)
        BOT_EDGE_P2 = (x_end_p2, Y_BOTTOM)
        
        # Right Boundary Points (E_top, F, G, H_bot)
        E_top = get_line_intersection(E_raw, F, TOP_EDGE_P1, TOP_EDGE_P2)
        if E_top is None: E_top = E_raw # Should be on Y_TOP
        H_bot = get_line_intersection(G, D_prime_R, BOT_EDGE_P1, BOT_EDGE_P2)
        if H_bot is None: H_bot = D_prime_R # Should be on Y_BOTTOM
        
        # Left Boundary Points (I_top, J, K, L_bot)
        I_top = get_line_intersection(I_raw, J, TOP_EDGE_P1, TOP_EDGE_P2)
        if I_top is None: I_top = I_raw # Should be on Y_TOP
        L_bot = get_line_intersection(K, D_prime_L, BOT_EDGE_P1, BOT_EDGE_P2)
        if L_bot is None: L_bot = D_prime_L # Should be on Y_BOTTOM

        # 6. ASSEMBLE FINAL PANEL POINTS
        boundary_R = [E_top, F, G, H_bot] # Right side of the bolt (Panel 2's inner edge)
        boundary_L = [I_top, J, K, L_bot] # Left side of the bolt (Panel 1's inner edge)

        # Panel 1 (Left Panel) Points (Clockwise: TL -> I_top -> J -> K -> L_bot -> BL)
        p1_points = [
            (x_start_p1, y_top)      # TL
        ] + boundary_L + [
            (x_start_p1, y_bottom)   # BL
        ]
        
        # Panel 2 (Right Panel) Points (Clockwise: TR -> BR -> BL_P2 -> L_bot_R -> K_R -> J_R -> I_top_R)
        # Note: Panel 2's inner edge is boundary_R, traversed in reverse order from bottom up.
        p2_points = [
            (x_end_p2, y_top),       # TR
            (x_end_p2, y_bottom),    # BR
            (x_start_p2, y_bottom),  # BL corner of P2
            H_bot,                   # Bottom of split line R
            G,                       # Second Angle R
            F,                       # First Angle R
            E_top                    # Top of split line R
        ]
        
    else:
        # Fallback for unknown type
        print(f"Error: Unknown split type '{split_type}'. Drawing standard rectangles.")
        return x_end_p2


    # 3. Draw Panel 1 (Left)
    dwg.add(dwg.polygon(
        points=p1_points,
        stroke=panel_stroke,
        fill=panel_fill,
        stroke_width=3
    ))

    # 4. Draw Panel 2 (Right)
    dwg.add(dwg.polygon(
        points=p2_points,
        stroke=panel_stroke,
        fill=panel_fill,
        stroke_width=3
    ))
    
    # Return the x-coordinate of the end of Panel 2
    return x_end_p2


def make_comic_page(
    filename="comic_page.svg",
    width=1920,
    height=1080,
    row_config=[1, 2, 3],
    margin=20,
    gutter=10,
    background="#ffffff",
    panel_stroke="#000000",
    panel_fill="none",
    split_panels=[], # List of (row_index, start_col_index) for split pairs
    split_type='arrow', # Type of diagonal separation
    split_params={} # Dictionary of split ratios
):
    """Generate a flexible comic page layout with optional dynamic diagonal splits."""

    dwg = svgwrite.Drawing(filename, size=(width, height))
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=background))

    total_rows = len(row_config)
    
    if total_rows == 0:
        dwg.save()
        print(f"Comic layout saved as {filename} (empty page)")
        return

    # 1. Calculate general panel height (assuming equal row height)
    panel_height = (height - 2 * margin - (total_rows - 1) * gutter) / total_rows
    y = margin
    
    # 2. Iterate through rows
    for r, total_cols in enumerate(row_config):
        
        # Calculate the standard width for an equally divided panel in this row
        standard_panel_width = (width - 2 * margin - (total_cols - 1) * gutter) / total_cols
        
        x = margin
        c = 0 # Current column index

        # 3. Iterate through columns
        while c < total_cols:
            
            # Check if this panel (c) and the next panel (c+1) should be split
            is_split_pair = (r, c) in split_panels and c + 1 < total_cols
            
            if is_split_pair:
                # If this is a split pair, the total width for the split operation covers 
                # two standard panels and one gutter.
                split_area_width = (standard_panel_width * 2) + gutter
                
                x = draw_split_panels(
                    dwg, 
                    x, 
                    y, 
                    split_area_width, 
                    panel_height, 
                    gutter, 
                    panel_stroke, 
                    panel_fill,
                    split_type,
                    split_params # Pass the dynamic parameters
                )
                
                # BUG FIX: After the two split panels are drawn, we must add the gutter 
                # that separates this pair from the next panel (c+2).
                if c + 2 < total_cols:
                    x += gutter 
                
                # We drew two panels, so skip the next column index
                c += 2 
            
            else:
                # Standard rectangular panel drawing
                dwg.add(dwg.rect(
                    insert=(x, y),
                    size=(standard_panel_width, panel_height),
                    stroke=panel_stroke,
                    fill=panel_fill,
                    stroke_width=3
                ))
                x += standard_panel_width + gutter
                c += 1 # Move to the next column
                
        # Move down to the next row
        y += panel_height + gutter

    dwg.save()
    print(f"Comic layout saved as {filename}")


def get_float_input(prompt, default_val):
    """Utility to safely get a float input."""
    try:
        val = float(input(f"{prompt} (default {default_val}): ") or default_val)
        
        # Only constrain Y-ratios (0.0 to 1.0). X-ratios > 1.0 are allowed for jutting.
        if "Y position ratio" in prompt:
             return max(0.0, min(1.0, val))
        return val
        
    except ValueError:
        print(f"Invalid input. Using default value: {default_val}")
        return default_val


def get_user_input():
    print("Advanced Comic Layout Builder (Dynamic Split Enabled)\n")

    # Page size
    preset = input("Use a preset size? (1) 1920x1080  (2) A4 (2480x3508)  (3) Custom [1/2/3]: ").strip()
    if preset == "2":
        width, height = 2480, 3508
    elif preset == "3":
        width = int(input("Enter page width (pixels): "))
        height = int(input("Enter page height (pixels): "))
    else:
        width, height = 1920, 1080

    # Row configuration
    raw_rows = input("Enter number of panels per row (comma-separated, e.g. 1,2,3): ").strip()
    row_config = [int(x) for x in raw_rows.split(",") if x.strip().isdigit()]
    
    # Split Type Input: Now uses a number
    split_choice = input("Choose split type (1: straight, 2: arrow, 3: lightning - default 3): ").strip()
    
    if split_choice == '1':
        split_type = 'straight'
    elif split_choice == '2':
        split_type = 'arrow'
    else:
        split_type = 'lightning' # Default is 3 or any other invalid input

    # ----------------------------------------------------
    # Dynamic Split Parameters Input
    # ----------------------------------------------------
    print(f"\nSplit Geometry Ratios for {split_type.upper()} (Ratio relative to Panel 1 width: 1.0 is P1's edge):")
    
    split_params = {}
    
    # Setting defaults based on your last request (1.3, 0.7)
    default_top_x = 1.3
    default_bot_x = 0.7
    
    split_params['top_x_ratio'] = get_float_input(
        f"Split line START X ratio (where line hits top edge of left panel, default {default_top_x})", 
        default_top_x
    )
    
    split_params['bot_x_ratio'] = get_float_input(
        f"Split line END X ratio (where line hits bottom edge of left panel, default {default_bot_x})", 
        default_bot_x
    )

    if split_type == 'arrow':
        # Controls the position and depth of the arrow peak
        split_params['mid_y_ratio'] = get_float_input(
            "Arrow peak Y position ratio (where arrow hits vertically, e.g., 0.5 for middle)", 
            0.5
        )
        split_params['depth_x_ratio'] = get_float_input(
            "Arrow peak X depth ratio (how far it juts out horizontally, e.g., 1.5 for large jut)", 
            1.5
        )
    
    elif split_type == 'lightning':
        # Controls the position and depth of the two angles in the lightning bolt
        print("\n--- Lightning Split Specific Ratios ---")
        
        # Setting defaults based on your last request (0.6, 1.0, 0.55, 0.9)
        default_zig_y = 0.60
        default_zig_depth_x = 1.0
        default_zag_y = 0.55
        default_zag_depth_x = 0.9
        
        split_params['zig_y_ratio'] = get_float_input(
            f"First angle Y position ratio (Zig, default {default_zig_y})", 
            default_zig_y 
        )
        split_params['zig_depth_x_ratio'] = get_float_input(
            f"First angle X depth ratio (Zig, default {default_zig_depth_x})", 
            default_zig_depth_x 
        )
        
        split_params['zag_y_ratio'] = get_float_input(
            f"Second angle Y position ratio (Zag, default {default_zag_y})", 
            default_zag_y 
        )
        split_params['zag_depth_x_ratio'] = get_float_input(
            f"Second angle X depth ratio (Zag, default {default_zag_depth_x})", 
            default_zag_depth_x 
        )
    # ----------------------------------------------------
    
    # Diagonal Splits Input
    print(f"\nDiagonal Split Configuration (Type: {split_type.upper()}):")
    raw_splits = input("Enter STARTING panel coordinates for adjacent pairs to split (row,col comma-separated, e.g. 1,0,2,3): ").strip()
    split_panels = []
    
    # Process the input for splits (r, c)
    coords = [x.strip() for x in raw_splits.split(',') if x.strip()]
    if len(coords) % 2 == 0:
        for i in range(0, len(coords), 2):
            try:
                r = int(coords[i])
                c = int(coords[i+1])
                # Validation: check if the coordinate is within the config bounds and if the next panel exists
                if 0 <= r < len(row_config) and 0 <= c + 1 < row_config[r]:
                    split_panels.append((r, c))
                else:
                    print(f"Warning: Split coordinate ({r},{c}) requires two adjacent panels and is out of bounds or invalid and ignored.")
            except ValueError:
                print("Warning: Non-integer coordinates detected for splits and ignored.")

    margin = int(input("\nMargin around the page (default 20): ") or 20)
    gutter = int(input("Space between panels (default 10): ") or 10)
    background = input("Background color (default white): ") or "#ffffff"
    stroke_color = input("Panel border color (default black): ") or "#000000"
    filename = input("Output file name (default comic_page.svg): ") or "comic_page.svg"

    return {
        "filename": filename,
        "width": width,
        "height": height,
        "row_config": row_config,
        "margin": margin,
        "gutter": gutter,
        "background": background,
        "panel_stroke": stroke_color,
        "split_panels": split_panels, 
        "split_type": split_type,
        "split_params": split_params # Pass the dictionary of ratios
    }


if __name__ == "__main__":
    settings = get_user_input()
    make_comic_page(**settings)

