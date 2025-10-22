import svgwrite
import math

# --- Configuration for the SVG Drawing ---
FILENAME = 'speech_bubble.svg'
# Increased size to accommodate long tails and large shadows
WIDTH, HEIGHT = 800, 600 
CENTER_X, CENTER_Y = WIDTH / 2, HEIGHT / 2 # Center is now (400, 300)

# Use separate radii for an oval shape (Horizontal and Vertical)
RX = 150  # Horizontal Radius (Wider)
RY = 100  # Vertical Radius (Shorter)

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
    Calculates the total degrees (clockwise from 12 o'clock) for the clock hand.
    """
    # Convert 12-hour format to 0-11 for calculation (12 o'clock is 0 for degrees)
    h = hour % 12 
    
    # Hour component: 30 degrees per hour (360/12)
    # Minute component: 0.5 degrees per minute (30 degrees/60 minutes)
    angle_degrees = (h * 30) + (minute * 0.5)
    
    return angle_degrees

def calculate_full_bubble_path_from_angle(angle_degrees, offset_x=0, offset_y=0, tail_length=15):
    """
    Calculates the geometry for the smooth, bent tail and generates the SVG Path data string 
    for the entire combined shape (main oval body arc + bent tail).
    
    The path now uses Quadratic Bézier curves (Q) to introduce a smooth bend.
    """
    ANGLE_RAD = math.radians(angle_degrees)
    
    # --- Tail Geometry Configuration ---
    TIP_EXTENSION = tail_length 
    OFFSET_RAD = math.radians(5)    # Angular spread for the base (5 degrees on each side)
    
    # Configuration for the curve's bend (relative to the angle)
    CURVE_BEND_ANGLE = math.radians(2) # 2 degrees angular displacement for the curve
    CURVE_BEND_RADIUS_RATIO = 0.6      # Control point placed 60% of the way to the tip
    
    # --- 1. Calculate the Base Points (P1 and P2) on the ellipse's circumference ---
    
    # P1 (Base Left) - Start of the perimeter drawing
    P1_X = (CENTER_X + offset_x) + RX * math.sin(ANGLE_RAD - OFFSET_RAD)
    P1_Y = (CENTER_Y + offset_y) - RY * math.cos(ANGLE_RAD - OFFSET_RAD)

    # P2 (Base Right) - End of the large arc
    P2_X = (CENTER_X + offset_x) + RX * math.sin(ANGLE_RAD + OFFSET_RAD)
    P2_Y = (CENTER_Y + offset_y) - RY * math.cos(ANGLE_RAD + OFFSET_RAD)
    
    # --- 2. Calculate the Single Tip Point (P_Tip) ---
    
    # P_Tip: 100% length, pointing straight out along the angle line.
    R_Tip = RX + TIP_EXTENSION 
    P_Tip_X = (CENTER_X + offset_x) + R_Tip * math.sin(ANGLE_RAD)
    P_Tip_Y = (CENTER_Y + offset_y) - R_Tip * math.cos(ANGLE_RAD)

    # --- 3. Calculate Control Points for the Bends (C1 and C2) ---
    
    # C1 (Controls P2 -> P_Tip side): Slightly displaced angularly
    R_C1 = RX + TIP_EXTENSION * CURVE_BEND_RADIUS_RATIO 
    Angle_C1 = ANGLE_RAD + CURVE_BEND_ANGLE 
    C1_X = (CENTER_X + offset_x) + R_C1 * math.sin(Angle_C1)
    C1_Y = (CENTER_Y + offset_y) - R_C1 * math.cos(Angle_C1)

    # C2 (Controls P_Tip -> P1 side): Mirror displacement angularly
    R_C2 = RX + TIP_EXTENSION * CURVE_BEND_RADIUS_RATIO 
    Angle_C2 = ANGLE_RAD - CURVE_BEND_ANGLE 
    C2_X = (CENTER_X + offset_x) + R_C2 * math.sin(Angle_C2)
    C2_Y = (CENTER_Y + offset_y) - R_C2 * math.cos(Angle_C2)

    # --- SVG Path Construction for the ENTIRE Oval Shape (Single Line) ---
    
    full_path = (
        f"M {P1_X},{P1_Y} " 
        # Main Oval Body Arc
        f"A {RX},{RY} 0 1,0 {P2_X},{P2_Y} " 
        
        # Curve 1: P2 (Base Right) -> P_Tip using C1 as control point
        f"Q {C1_X},{C1_Y} {P_Tip_X},{P_Tip_Y} " 
        
        # Curve 2: P_Tip -> P1 (Base Left) using C2 as control point
        # The 'Z' command is omitted as the second Q command targets P1, closing the path.
        f"Q {C2_X},{C2_Y} {P1_X},{P1_Y} "
    )

    return full_path

def create_custom_bubble(angle_degrees, hour, minute, shadow_size, shade_level, tail_length, bubble_text):
    """
    Generates an SVG file containing the oval bubble with the smooth tail (based on time angle) 
    and shadow, displaying custom text.
    """
    
    # Set offsets and color based on user input
    SHADOW_OFFSET_X = shadow_size
    SHADOW_OFFSET_Y = shadow_size
    # Get color from the dictionary based on the level (default to black if level is out of range)
    SHADOW_COLOR = SHADOW_COLORS.get(shade_level, '#000000') 
    
    # Calculate the path for the main bubble (no offset)
    main_bubble_path = calculate_full_bubble_path_from_angle(angle_degrees, tail_length=tail_length)
    
    # Calculate the path for the shadow (with offset)
    shadow_path = calculate_full_bubble_path_from_angle(angle_degrees, SHADOW_OFFSET_X, SHADOW_OFFSET_Y, tail_length=tail_length)
    
    # BOLD STROKE for Comic Book Look
    STROKE_WIDTH = 4
    FILL_COLOR = '#FFFFFF'
    STROKE_COLOR = 'black'
    
    # Create the drawing object
    dwg = svgwrite.Drawing(FILENAME, size=(WIDTH, HEIGHT), profile='full')
    
    # --- Draw the Shadow First (so it appears behind the main bubble) ---
    # The shadow is filled with the user-selected gray and has no stroke/border
    dwg.add(dwg.path(
        d=shadow_path,
        fill=SHADOW_COLOR,
        stroke='none', 
        stroke_width=0
    ))
    
    # 1. Draw the main bubble shape as a single Path
    # This sits on top of the shadow
    dwg.add(dwg.path(
        d=main_bubble_path,
        fill=FILL_COLOR,
        stroke=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
        stroke_linecap='round',
        stroke_linejoin='round'
    ))

    # 2. Add the custom BUBBLE TEXT in the center
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
    print(f"Successfully generated {FILENAME} with text: '{bubble_text}' and angle corresponding to {hour:02d}:{minute:02d}.")


def get_user_input():
    """Prompts the user for all parameters, including custom bubble text."""
    
    # Initialize defaults
    HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH = 3, 45, 5, 5, 15
    BUBBLE_TEXT = "ZAP!"
    
    # --- Get Time Input (Used for Angle) ---
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
    while True:
        try:
            tail_str = input("Enter the TAIL LENGTH (e.g., 5 for short, 30 for medium, 90 for very long): ")
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

    # --- Get Bubble Text Input (New) ---
    try:
        BUBBLE_TEXT = input("Enter the TEXT you want inside the bubble: ")
        if not BUBBLE_TEXT:
             BUBBLE_TEXT = "ZAP!"
    except EOFError:
        print("Text input not available. Using default ('ZAP!').")
        pass
            
    return HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH, BUBBLE_TEXT

if __name__ == '__main__':
    
    # --- GET USER INPUT ---
    print("\n--- Oval Speech Bubble Generator ---")
    HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH, BUBBLE_TEXT = get_user_input()
    
    # Calculate the angle based on the chosen time
    calculated_angle = time_to_angle(HOUR, MINUTE)
    
    # Generate the custom bubble SVG
    create_custom_bubble(calculated_angle, HOUR, MINUTE, SHADOW_SIZE, SHADE_LEVEL, TAIL_LENGTH, BUBBLE_TEXT)
    
# --- To view the bubble, run this script and open 'speech_bubble.svg' in a web browser. ---

