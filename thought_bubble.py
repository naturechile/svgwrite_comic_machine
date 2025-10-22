import svgwrite
import math

# --- Configuration for the SVG Drawing ---
FILENAME = 'bubble_generator.svg'
# Increased size to accommodate long tails and large shadows
WIDTH, HEIGHT = 800, 600 
CENTER_X, CENTER_Y = WIDTH / 2, HEIGHT / 2 # Center is now (400, 300)

# Shape Radii (Used for both Speech Oval and Thought Bubble sizing)
RX = 150  # Horizontal Radius (Wider)
RY = 100  # Vertical Radius (Shorter)
CLOUD_RADIUS = 130 # Base size for the cloud body circles

# --- Shadow Configuration: Maps user input (1-10) to hex color ---
SHADOW_COLORS = {
    1: '#E0E0E0', # Very Light Gray
    2: '#C0C0C0', # Light Gray
    3: '#A0A0A0',
    4: '#808080', # Medium Gray
    5: '#606060',
    6: '#404040',
    7: '#303030',
    8: '#202020',
    9: '#101010',
    10: '#000000' # Pure Black
}


def time_to_angle(hour, minute):
    """
    Calculates the total degrees (clockwise from 12 o'clock) for positioning the tail/bubbles.
    """
    # Convert 12-hour format to 0-11 for calculation (12 o'clock is 0 for degrees)
    h = hour % 12 
    
    # Hour component: 30 degrees per hour (360/12)
    # Minute component: 0.5 degrees per minute (30 degrees/60 minutes)
    angle_degrees = (h * 30) + (minute * 0.5)
    return angle_degrees

# --- SPEECH BUBBLE GEOMETRY (Oval Body, Curved Tail) ---

def calculate_speech_bubble_path(angle_degrees, offset_x=0, offset_y=0, tail_length=15):
    """
    Calculates the single-line SVG Path data string for the oval bubble with the bent tail.
    """
    ANGLE_RAD = math.radians(angle_degrees)
    TIP_EXTENSION = tail_length 
    OFFSET_RAD = math.radians(5)    # Angular spread for the base
    CURVE_BEND_ANGLE = math.radians(2) 
    CURVE_BEND_RADIUS_RATIO = 0.6
    
    # 1. Base Points (P1 and P2) on the ellipse's circumference
    P1_X = (CENTER_X + offset_x) + RX * math.sin(ANGLE_RAD - OFFSET_RAD)
    P1_Y = (CENTER_Y + offset_y) - RY * math.cos(ANGLE_RAD - OFFSET_RAD)
    P2_X = (CENTER_X + offset_x) + RX * math.sin(ANGLE_RAD + OFFSET_RAD)
    P2_Y = (CENTER_Y + offset_y) - RY * math.cos(ANGLE_RAD + OFFSET_RAD)
    
    # 2. Tip Point (P_Tip)
    R_Tip = RX + TIP_EXTENSION 
    P_Tip_X = (CENTER_X + offset_x) + R_Tip * math.sin(ANGLE_RAD)
    P_Tip_Y = (CENTER_Y + offset_y) - R_Tip * math.cos(ANGLE_RAD)

    # 3. Control Points for the Bends (C1 and C2)
    R_C1 = RX + TIP_EXTENSION * CURVE_BEND_RADIUS_RATIO 
    Angle_C1 = ANGLE_RAD + CURVE_BEND_ANGLE 
    C1_X = (CENTER_X + offset_x) + R_C1 * math.sin(Angle_C1)
    C1_Y = (CENTER_Y + offset_y) - R_C1 * math.cos(Angle_C1)

    R_C2 = RX + TIP_EXTENSION * CURVE_BEND_RADIUS_RATIO 
    Angle_C2 = ANGLE_RAD - CURVE_BEND_ANGLE 
    C2_X = (CENTER_X + offset_x) + R_C2 * math.sin(Angle_C2)
    C2_Y = (CENTER_Y + offset_y) - R_C2 * math.cos(Angle_C2)

    # SVG Path Construction (M -> A -> Q -> Q)
    full_path = (
        f"M {P1_X},{P1_Y} " 
        f"A {RX},{RY} 0 1,0 {P2_X},{P2_Y} " 
        f"Q {C1_X},{C1_Y} {P_Tip_X},{P_Tip_Y} " 
        f"Q {C2_X},{C2_Y} {P1_X},{P1_Y} "
    )
    return full_path

# --- THOUGHT BUBBLE GEOMETRY (Cloud Body, Circle Tail) ---

def calculate_cloud_path(offset_x=0, offset_y=0):
    """
    Generates a cloud-like shape path using a series of semi-circular arcs.
    FIX: Changed sweep-flag to 0 to make the arcs bulge outward (convex).
    """
    CX = CENTER_X + offset_x
    CY = CENTER_Y + offset_y
    R = CLOUD_RADIUS # Base radius for the cloud

    # Define the 12 key points around the shape for the cloud's perimeter
    # Coordinates are slightly offset for an irregular, hand-drawn look
    points = [
        (CX + R * 0.9, CY - R * 0.1),
        (CX + R * 0.8, CY - R * 0.4),
        (CX + R * 0.4, CY - R * 0.9),
        (CX + R * 0.1, CY - R * 0.8),
        (CX - R * 0.5, CY - R * 0.9),
        (CX - R * 0.9, CY - R * 0.5),
        (CX - R * 0.8, CY - R * 0.1),
        (CX - R * 0.9, CY + R * 0.5),
        (CX - R * 0.4, CY + R * 0.8),
        (CX + R * 0.1, CY + R * 0.9),
        (CX + R * 0.5, CY + R * 0.8),
        (CX + R * 0.9, CY + R * 0.4),
    ]

    path = f"M {points[0][0]},{points[0][1]}"
    
    # Use arcs (A) between each point to create the cloud bumps
    # sweep-flag = 0 now ensures the arc bulges OUTWARD
    for i in range(1, len(points)):
        path += f" A 30 30 0 0 0 {points[i][0]},{points[i][1]}"
        
    # Close the loop
    path += f" A 30 30 0 0 0 {points[0][0]},{points[0][1]}"

    return path

def calculate_thought_bubble_tail(angle_degrees, offset_x=0, offset_y=0, tail_length=15):
    """
    Calculates the position and radius for the diminishing circles of the thought bubble tail.
    Returns a list of (cx, cy, radius) tuples.
    """
    ANGLE_RAD = math.radians(angle_degrees)
    
    # Tail is composed of 3 diminishing circles
    NUM_CIRCLES = 3
    tail_bubbles = []
    
    # Start position for the smallest bubble, determined by the tip extension
    START_RADIUS = CLOUD_RADIUS + tail_length / NUM_CIRCLES
    
    for i in range(NUM_CIRCLES):
        # Calculate radius and size based on index (i=0 is the smallest)
        bubble_radius = 5 + (NUM_CIRCLES - 1 - i) * 3  # Radii: 5, 8, 11
        
        # Calculate distance from center, shrinking toward the cloud body
        distance_from_center = START_RADIUS + i * (tail_length / NUM_CIRCLES)
        
        # Calculate center coordinates
        cx = (CENTER_X + offset_x) + distance_from_center * math.sin(ANGLE_RAD)
        cy = (CENTER_Y + offset_y) - distance_from_center * math.cos(ANGLE_RAD)
        
        tail_bubbles.append((cx, cy, bubble_radius))
        
    return tail_bubbles

# --- MAIN DRAWING FUNCTION ---

def create_custom_bubble(bubble_type, angle_degrees, hour, minute, shadow_size, shade_level, tail_length, bubble_text):
    """
    Generates an SVG file based on the selected bubble type and user inputs.
    """
    
    # Set offsets and color based on user input
    SHADOW_OFFSET_X = shadow_size
    SHADOW_OFFSET_Y = shadow_size
    SHADOW_COLOR = SHADOW_COLORS.get(shade_level, '#000000') 
    
    STROKE_WIDTH = 4
    FILL_COLOR = '#FFFFFF'
    STROKE_COLOR = 'black'
    
    dwg = svgwrite.Drawing(FILENAME, size=(WIDTH, HEIGHT), profile='full')
    
    # --- Shadow and Main Body Drawing ---
    
    if bubble_type == 'SPEECH':
        # SPEECH BUBBLE (Oval Path with Curved Tail)
        
        # 1. Shadow Path
        shadow_path = calculate_speech_bubble_path(angle_degrees, SHADOW_OFFSET_X, SHADOW_OFFSET_Y, tail_length=tail_length)
        dwg.add(dwg.path(d=shadow_path, fill=SHADOW_COLOR, stroke='none'))
        
        # 2. Main Path
        main_bubble_path = calculate_speech_bubble_path(angle_degrees, tail_length=tail_length)
        dwg.add(dwg.path(d=main_bubble_path, fill=FILL_COLOR, stroke=STROKE_COLOR, stroke_width=STROKE_WIDTH, 
                        stroke_linecap='round', stroke_linejoin='round'))
        
    elif bubble_type == 'THOUGHT':
        # THOUGHT BUBBLE (Cloud Path with Diminishing Circles)

        # 1. Shadow Cloud Path
        shadow_cloud_path = calculate_cloud_path(SHADOW_OFFSET_X, SHADOW_OFFSET_Y)
        dwg.add(dwg.path(d=shadow_cloud_path, fill=SHADOW_COLOR, stroke='none'))
        
        # 2. Main Cloud Path
        main_cloud_path = calculate_cloud_path()
        dwg.add(dwg.path(d=main_cloud_path, fill=FILL_COLOR, stroke=STROKE_COLOR, stroke_width=STROKE_WIDTH))

        # 3. Draw Shadow Tail Bubbles (Behind Main Bubbles)
        shadow_tail_bubbles = calculate_thought_bubble_tail(angle_degrees, SHADOW_OFFSET_X, SHADOW_OFFSET_Y, tail_length=tail_length)
        for cx, cy, r in shadow_tail_bubbles:
             dwg.add(dwg.circle(center=(cx, cy), r=r, fill=SHADOW_COLOR, stroke='none'))

        # 4. Draw Main Tail Bubbles (On Top)
        main_tail_bubbles = calculate_thought_bubble_tail(angle_degrees, tail_length=tail_length)
        for cx, cy, r in main_tail_bubbles:
             dwg.add(dwg.circle(center=(cx, cy), r=r, fill=FILL_COLOR, stroke=STROKE_COLOR, stroke_width=STROKE_WIDTH/2))
        
    # --- Add Text (Same for both types) ---
    dwg.add(dwg.text(
        bubble_text,
        insert=(CENTER_X, CENTER_Y + 10),
        font_size='22px',
        text_anchor='middle',
        fill='black',
        font_family='Impact, sans-serif'
    ))

    # Save the SVG file
    dwg.save(pretty=True)
    print(f"Successfully generated {bubble_type} bubble named '{FILENAME}' with text: '{bubble_text}' and position corresponding to {hour:02d}:{minute:02d}.")


def get_user_input():
    """Prompts the user for all parameters, including bubble type and custom bubble text."""
    
    # Initialize defaults
    BUBBLE_TYPE = "SPEECH"
    HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH = 3, 45, 5, 5, 15
    BUBBLE_TEXT = "ZAP!"
    
    # --- Get Bubble Type Input ---
    while True:
        try:
            # FIX: Changed input prompt and check to use '1' or '2'
            type_str = input("Choose bubble type (1=SPEECH or 2=THOUGHT): ")
            if type_str == '1':
                BUBBLE_TYPE = 'SPEECH'
                break
            elif type_str == '2':
                BUBBLE_TYPE = 'THOUGHT'
                break
            else:
                print("Error: Please enter '1' for SPEECH or '2' for THOUGHT.")
        except EOFError:
            print("Bubble type input not available. Using default ('SPEECH').")
            break
            
    # --- Get Time Input (Used for Angle/Position) ---
    print("\n--- Positioning for Tail/Bubbles ---")
    while True:
        try:
            hour_str = input("Enter the HOUR (1-12) for the tail's ANGLE: ")
            HOUR = int(hour_str)
            if not (1 <= HOUR <= 12):
                print("Error: Hour must be between 1 and 12.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid whole number for the hour.")
        except EOFError:
            print("\nHour input not available. Using default (3).")
            break
            
    while True:
        try:
            minute_str = input("Enter the MINUTE (0-59) for the tail's ANGLE: ")
            MINUTE = int(minute_str)
            if not (0 <= MINUTE <= 59):
                print("Error: Minute must be between 0 and 59.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid whole number for the minute.")
        except EOFError:
            print("Minute input not available. Using default (45).")
            break
    
    # --- Get Shadow Size Input ---
    print("\n--- Shadow Configuration ---")
    while True:
        try:
            shadow_str = input("Enter the SHADOW SIZE (e.g., 2 for small, 10 for big): ")
            SHADOW_SIZE = int(shadow_str)
            if SHADOW_SIZE < 0:
                 print("Error: Shadow size must be a positive number.")
                 continue
            break
        except ValueError:
            print("Error: Please enter a valid whole number for the shadow size.")
        except EOFError:
            print("Shadow size input not available. Using default (5).")
            break
            
    # --- Get Shade Level Input ---
    while True:
        try:
            shade_str = input("Enter the SHADE LEVEL (1=light gray, 10=black): ")
            SHADE_LEVEL = int(shade_str)
            if not (1 <= SHADE_LEVEL <= 10):
                 print("Error: Shade level must be between 1 and 10.")
                 continue
            break
        except ValueError:
            print("Error: Please enter a valid whole number for the shade level.")
        except EOFError:
            print("Shade level input not available. Using default (5).")
            break
            
    # --- Get Tail Length Input ---
    print("\n--- Tail Configuration ---")
    while True:
        try:
            # Note: For THOUGHT bubbles, this controls the distance the smallest bubble extends
            tail_str = input("Enter the TAIL LENGTH (e.g., 5 for short, 90 for very long): ")
            TAIL_LENGTH = int(tail_str)
            if TAIL_LENGTH < 0:
                 print("Error: Tail length must be a positive number.")
                 continue
            break
        except ValueError:
            print("Error: Please enter a valid whole number for the tail length.")
        except EOFError:
            print("Tail length input not available. Using default (15).")
            break

    # --- Get Bubble Text Input ---
    try:
        BUBBLE_TEXT = input("Enter the TEXT you want inside the bubble: ")
        if not BUBBLE_TEXT:
             BUBBLE_TEXT = "THINKING..." if BUBBLE_TYPE == 'THOUGHT' else "ZAP!"
    except EOFError:
        print("Text input not available. Using default.")
        BUBBLE_TEXT = "THINKING..." if BUBBLE_TYPE == 'THOUGHT' else "ZAP!"
        pass
            
    return BUBBLE_TYPE, HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH, BUBBLE_TEXT

if __name__ == '__main__':
    
    # --- GET USER INPUT ---
    print("\n--- Custom SVG Bubble Generator ---")
    BUBBLE_TYPE, HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH, BUBBLE_TEXT = get_user_input()
    
    # Calculate the angle based on the chosen time
    calculated_angle = time_to_angle(HOUR, MINUTE)
    
    # Generate the custom bubble SVG
    create_custom_bubble(BUBBLE_TYPE, calculated_angle, HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH, BUBBLE_TEXT)
    
# --- To view the bubble, run this script and open 'bubble_generator.svg' in a web browser. ---

