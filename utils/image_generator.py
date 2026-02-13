"""Image generation utilities for roster calendar display."""
import io
from typing import List, Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from .constants import WOW_CLASS_COLORS


# Image configuration constants matching Google Sheets layout
# Player stats sidebar
PLAYER_NAME_COL_WIDTH = 100
RAIDS_COUNT_COL_WIDTH = 80
BENCHES_COUNT_COL_WIDTH = 80
PLAYER_STATS_WIDTH = PLAYER_NAME_COL_WIDTH + RAIDS_COUNT_COL_WIDTH + BENCHES_COUNT_COL_WIDTH

# Raid column widths
ROSTER_GRID_CELL_WIDTH = 80
ROSTER_GRID_CELL_HEIGHT = 25
ROSTER_GRID_COLS = 5  # 5 columns for main roster grid
ROSTER_GRID_WIDTH = ROSTER_GRID_CELL_WIDTH * ROSTER_GRID_COLS

# Side panels (per raid)
SIDE_PANEL_COL_WIDTH = 100
ABSENCES_COL_WIDTH = SIDE_PANEL_COL_WIDTH
BENCHES_COL_WIDTH = SIDE_PANEL_COL_WIDTH
SWAPS_COL_WIDTH = SIDE_PANEL_COL_WIDTH * 2  # Two sub-columns

# Total raid column width
RAID_COL_WIDTH = ROSTER_GRID_WIDTH + ABSENCES_COL_WIDTH + BENCHES_COL_WIDTH + SWAPS_COL_WIDTH

# Heights
HEADER_HEIGHT = 40
PLAYER_ROW_HEIGHT = 25

# Font sizes
FONT_SIZE = 10
PLAYER_NAME_FONT_SIZE = 12
HEADER_FONT_SIZE = 14
STATS_FONT_SIZE = 11

# Colors matching Google Sheets
BACKGROUND_COLOR = (211, 211, 211)  # #D3D3D3 - Light gray
YELLOW_BG = (255, 215, 0)  # #FFD700 - Yellow for player stats
GREEN_BG = (144, 238, 144)  # #90EE90 - Light green for bench counts
WHITE_BG = (255, 255, 255)  # White for side panels
BORDER_COLOR = (128, 128, 128)  # #808080 - Dark gray borders
TEXT_COLOR = (0, 0, 0)  # Black text for readability
BORDER_WIDTH = 1

PADDING = 5


def hex_to_rgb(hex_color: int) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple.
    
    Args:
        hex_color: Hex color as integer (e.g., 0xFF0000)
        
    Returns:
        RGB tuple (r, g, b)
    """
    return (
        (hex_color >> 16) & 0xFF,
        (hex_color >> 8) & 0xFF,
        hex_color & 0xFF
    )


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Get a font for drawing text.
    
    Args:
        size: Font size
        
    Returns:
        ImageFont object
    """
    try:
        # Try to use a common system font
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except (OSError, IOError):
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except (OSError, IOError):
            # Fallback to default font
            return ImageFont.load_default()


def draw_text_centered(draw: ImageDraw.ImageDraw, position: Tuple[int, int, int, int], 
                       text: str, font: ImageFont.FreeTypeFont, fill: Tuple[int, int, int]):
    """Draw text centered in a rectangle.
    
    Args:
        draw: ImageDraw object
        position: Rectangle (x1, y1, x2, y2)
        text: Text to draw
        font: Font to use
        fill: Text color
    """
    x1, y1, x2, y2 = position
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate centered position
    x = x1 + (x2 - x1 - text_width) // 2
    y = y1 + (y2 - y1 - text_height) // 2
    
    draw.text((x, y), text, font=font, fill=fill)


def draw_bordered_cell(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int,
                       text: str, bg_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                       font: ImageFont.FreeTypeFont, border_color: Tuple[int, int, int] = BORDER_COLOR,
                       border_width: int = BORDER_WIDTH):
    """Draw a cell with border, background, and centered text.
    
    Args:
        draw: ImageDraw object
        x, y: Top-left corner position
        width, height: Cell dimensions
        text: Text to display
        bg_color: Background color
        text_color: Text color
        font: Font to use
        border_color: Border color
        border_width: Border width in pixels
    """
    # Draw background
    draw.rectangle([x, y, x + width, y + height], fill=bg_color, outline=border_color, width=border_width)
    
    # Draw centered text
    if text:
        draw_text_centered(draw, (x, y, x + width, y + height), text, font, text_color)


def get_player_class_color(class_name: Optional[str]) -> Tuple[int, int, int]:
    """Get the WoW class color as RGB tuple.
    
    Args:
        class_name: WoW class name
        
    Returns:
        RGB tuple for the class color
    """
    if not class_name or class_name == "Unknown":
        return (128, 128, 128)  # Gray for unknown
    return hex_to_rgb(WOW_CLASS_COLORS.get(class_name, 0x808080))


def layout_roster_grid(main_roster: List[Tuple], max_cols: int = ROSTER_GRID_COLS) -> List[List[Tuple]]:
    """Arrange roster assignments in a grid layout.
    
    Args:
        main_roster: List of (RosterAssignment, Player, class_name) tuples
        max_cols: Maximum columns per row
        
    Returns:
        List of rows, where each row is a list of assignments
    """
    grid = []
    for i in range(0, len(main_roster), max_cols):
        grid.append(main_roster[i:i + max_cols])
    return grid


def truncate_text(text: str, max_width: int, font: ImageFont.FreeTypeFont, 
                 draw: ImageDraw.ImageDraw) -> str:
    """Truncate text to fit within max_width.
    
    Args:
        text: Text to truncate
        max_width: Maximum width in pixels
        font: Font being used
        draw: ImageDraw object for measuring
        
    Returns:
        Truncated text with ellipsis if needed
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    
    if text_width <= max_width:
        return text
    
    # Truncate and add ellipsis
    ellipsis = "..."
    while text and text_width > max_width - 20:
        text = text[:-1]
        bbox = draw.textbbox((0, 0), text + ellipsis, font=font)
        text_width = bbox[2] - bbox[0]
    
    return text + ellipsis


def generate_roster_calendar(raids_data: List[Tuple[object, List[Tuple[object, object, str]]]],
                            all_players: List[object]) -> io.BytesIO:
    """Generate a visual roster calendar image matching Google Sheets layout.
    
    Args:
        raids_data: List of (Raid, roster_data) tuples
        all_players: List of all Player objects for stats column
        
    Returns:
        BytesIO object containing the PNG image
    """
    if not raids_data:
        # Create a simple "no raids" image
        img = Image.new('RGB', (400, 100), color=BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        font = get_font(FONT_SIZE)
        draw_text_centered(draw, (0, 0, 400, 100), "No upcoming raids scheduled", font, TEXT_COLOR)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        return buffer
    
    # Sort players alphabetically by name
    all_players = sorted(all_players, key=lambda p: p.player_name)
    
    # Calculate dimensions
    num_raids = len(raids_data)
    num_players = len(all_players)
    
    # Calculate max roster size for proper height
    max_roster_size = 0
    for _, roster_data in raids_data:
        main_roster = [r for r in roster_data if r[0].status == "main"]
        max_roster_size = max(max_roster_size, len(main_roster))
    
    # Grid rows needed (at least 4 rows, or enough for the largest roster)
    grid_rows = max(4, (max_roster_size + ROSTER_GRID_COLS - 1) // ROSTER_GRID_COLS)
    
    # Image dimensions
    total_width = PLAYER_STATS_WIDTH + (num_raids * RAID_COL_WIDTH) + PADDING * 2
    total_height = HEADER_HEIGHT + (grid_rows * ROSTER_GRID_CELL_HEIGHT) + PADDING * 2
    
    # Create image with light gray background
    img = Image.new('RGB', (total_width, total_height), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    header_font = get_font(HEADER_FONT_SIZE)
    name_font = get_font(PLAYER_NAME_FONT_SIZE)
    cell_font = get_font(FONT_SIZE)
    stats_font = get_font(STATS_FONT_SIZE)
    
    # --- HEADER ROW ---
    y_offset = PADDING
    x_offset = PADDING
    
    # Player stats header columns
    draw_bordered_cell(draw, x_offset, y_offset, PLAYER_NAME_COL_WIDTH, HEADER_HEIGHT,
                      "Name:", YELLOW_BG, TEXT_COLOR, header_font)
    x_offset += PLAYER_NAME_COL_WIDTH
    
    draw_bordered_cell(draw, x_offset, y_offset, RAIDS_COUNT_COL_WIDTH, HEADER_HEIGHT,
                      "Raids:", YELLOW_BG, TEXT_COLOR, header_font)
    x_offset += RAIDS_COUNT_COL_WIDTH
    
    draw_bordered_cell(draw, x_offset, y_offset, BENCHES_COUNT_COL_WIDTH, HEADER_HEIGHT,
                      "Benches:", GREEN_BG, TEXT_COLOR, header_font)
    x_offset += BENCHES_COUNT_COL_WIDTH
    
    # Raid date headers (spanning full raid column width)
    for raid, _ in raids_data:
        # Format date and time nicely
        date_str = raid.raid_date
        time_str = raid.raid_time if raid.raid_time else ""
        header_text = f"{date_str} {time_str}"
        
        draw_bordered_cell(draw, x_offset, y_offset, RAID_COL_WIDTH, HEADER_HEIGHT,
                          header_text, WHITE_BG, TEXT_COLOR, header_font)
        x_offset += RAID_COL_WIDTH
    
    # --- PLAYER STATS ROWS (LEFT SIDEBAR) ---
    y_offset += HEADER_HEIGHT
    
    for i, player in enumerate(all_players):
        # Only draw as many rows as we have grid space
        if i >= grid_rows:
            break
            
        x_offset = PADDING
        
        # Player name (yellow background)
        player_name = truncate_text(player.player_name, PLAYER_NAME_COL_WIDTH - PADDING * 2, name_font, draw)
        draw_bordered_cell(draw, x_offset, y_offset, PLAYER_NAME_COL_WIDTH, PLAYER_ROW_HEIGHT,
                          player_name, YELLOW_BG, TEXT_COLOR, name_font)
        x_offset += PLAYER_NAME_COL_WIDTH
        
        # Raids rostered count (yellow background)
        raids_text = str(player.total_raids_rostered)
        draw_bordered_cell(draw, x_offset, y_offset, RAIDS_COUNT_COL_WIDTH, PLAYER_ROW_HEIGHT,
                          raids_text, YELLOW_BG, TEXT_COLOR, stats_font)
        x_offset += RAIDS_COUNT_COL_WIDTH
        
        # Benches count (green background, show "-" for zero)
        benches_text = str(player.total_benches) if player.total_benches > 0 else "-"
        draw_bordered_cell(draw, x_offset, y_offset, BENCHES_COUNT_COL_WIDTH, PLAYER_ROW_HEIGHT,
                          benches_text, GREEN_BG, TEXT_COLOR, stats_font)
        
        y_offset += PLAYER_ROW_HEIGHT
    
    # --- RAID COLUMNS ---
    for raid_idx, (raid, roster_data) in enumerate(raids_data):
        x_offset = PADDING + PLAYER_STATS_WIDTH + (raid_idx * RAID_COL_WIDTH)
        y_offset = PADDING + HEADER_HEIGHT
        
        # Separate roster by status
        main_roster = [(a, p, c) for a, p, c in roster_data if a.status == "main"]
        bench_roster = [(a, p, c) for a, p, c in roster_data if a.status == "bench"]
        absent_roster = [(a, p, c) for a, p, c in roster_data if a.status == "absent"]
        swap_roster = [(a, p, c) for a, p, c in roster_data if a.status == "swap"]
        
        # Sort main roster by position
        main_roster.sort(key=lambda x: x[0].position if x[0].position is not None else 999)
        
        # Layout main roster in grid
        roster_grid = layout_roster_grid(main_roster, ROSTER_GRID_COLS)
        
        # --- MAIN ROSTER GRID (5 columns) ---
        grid_x = x_offset
        grid_y = y_offset
        
        for row_idx in range(grid_rows):
            for col_idx in range(ROSTER_GRID_COLS):
                cell_x = grid_x + (col_idx * ROSTER_GRID_CELL_WIDTH)
                cell_y = grid_y + (row_idx * ROSTER_GRID_CELL_HEIGHT)
                
                # Check if we have a roster entry for this cell
                if row_idx < len(roster_grid) and col_idx < len(roster_grid[row_idx]):
                    assignment, player, class_name = roster_grid[row_idx][col_idx]
                    
                    # Get class color
                    bg_color = get_player_class_color(class_name)
                    
                    # Use character name
                    char_name = truncate_text(assignment.character_name, ROSTER_GRID_CELL_WIDTH - PADDING, cell_font, draw)
                    
                    draw_bordered_cell(draw, cell_x, cell_y, ROSTER_GRID_CELL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                                     char_name, bg_color, TEXT_COLOR, cell_font)
                else:
                    # Empty cell
                    draw_bordered_cell(draw, cell_x, cell_y, ROSTER_GRID_CELL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                                     "", WHITE_BG, TEXT_COLOR, cell_font)
        
        # --- SIDE PANELS (Absences, Benches, Swaps) ---
        side_panel_x = x_offset + ROSTER_GRID_WIDTH
        side_panel_y = y_offset
        
        # Absences column
        absence_x = side_panel_x
        draw_bordered_cell(draw, absence_x, side_panel_y, ABSENCES_COL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                          "absences", WHITE_BG, TEXT_COLOR, cell_font)
        
        for idx, (assignment, player, class_name) in enumerate(absent_roster[:grid_rows - 1]):
            cell_y = side_panel_y + ((idx + 1) * ROSTER_GRID_CELL_HEIGHT)
            player_name = truncate_text(player.player_name, ABSENCES_COL_WIDTH - PADDING, cell_font, draw)
            draw_bordered_cell(draw, absence_x, cell_y, ABSENCES_COL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                             player_name, WHITE_BG, TEXT_COLOR, cell_font)
        
        # Fill remaining absence cells
        for idx in range(len(absent_roster), grid_rows - 1):
            cell_y = side_panel_y + ((idx + 1) * ROSTER_GRID_CELL_HEIGHT)
            draw_bordered_cell(draw, absence_x, cell_y, ABSENCES_COL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                             "", WHITE_BG, TEXT_COLOR, cell_font)
        
        # Benches column
        bench_x = side_panel_x + ABSENCES_COL_WIDTH
        draw_bordered_cell(draw, bench_x, side_panel_y, BENCHES_COL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                          "benches:", WHITE_BG, TEXT_COLOR, cell_font)
        
        for idx, (assignment, player, class_name) in enumerate(bench_roster[:grid_rows - 1]):
            cell_y = side_panel_y + ((idx + 1) * ROSTER_GRID_CELL_HEIGHT)
            bg_color = get_player_class_color(class_name)
            char_name = truncate_text(assignment.character_name, BENCHES_COL_WIDTH - PADDING, cell_font, draw)
            draw_bordered_cell(draw, bench_x, cell_y, BENCHES_COL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                             char_name, bg_color, TEXT_COLOR, cell_font)
        
        # Fill remaining bench cells
        for idx in range(len(bench_roster), grid_rows - 1):
            cell_y = side_panel_y + ((idx + 1) * ROSTER_GRID_CELL_HEIGHT)
            draw_bordered_cell(draw, bench_x, cell_y, BENCHES_COL_WIDTH, ROSTER_GRID_CELL_HEIGHT,
                             "", WHITE_BG, TEXT_COLOR, cell_font)
        
        # Swaps columns (two sub-columns)
        swap_x = side_panel_x + ABSENCES_COL_WIDTH + BENCHES_COL_WIDTH
        swap_col_width = SWAPS_COL_WIDTH // 2
        
        # Swaps header with two sub-headers
        draw_bordered_cell(draw, swap_x, side_panel_y, swap_col_width, ROSTER_GRID_CELL_HEIGHT,
                          "swaps out:", WHITE_BG, TEXT_COLOR, cell_font)
        draw_bordered_cell(draw, swap_x + swap_col_width, side_panel_y, swap_col_width, ROSTER_GRID_CELL_HEIGHT,
                          "swaps in:", WHITE_BG, TEXT_COLOR, cell_font)
        
        for idx, (assignment, player, class_name) in enumerate(swap_roster[:grid_rows - 1]):
            cell_y = side_panel_y + ((idx + 1) * ROSTER_GRID_CELL_HEIGHT)
            bg_color = get_player_class_color(class_name)
            char_name = truncate_text(assignment.character_name, swap_col_width - PADDING, cell_font, draw)
            
            # Swapping out
            draw_bordered_cell(draw, swap_x, cell_y, swap_col_width, ROSTER_GRID_CELL_HEIGHT,
                             char_name, bg_color, TEXT_COLOR, cell_font)
            # Swapping in (would need additional data structure, leave empty for now)
            draw_bordered_cell(draw, swap_x + swap_col_width, cell_y, swap_col_width, ROSTER_GRID_CELL_HEIGHT,
                             "", WHITE_BG, TEXT_COLOR, cell_font)
        
        # Fill remaining swap cells
        for idx in range(len(swap_roster), grid_rows - 1):
            cell_y = side_panel_y + ((idx + 1) * ROSTER_GRID_CELL_HEIGHT)
            draw_bordered_cell(draw, swap_x, cell_y, swap_col_width, ROSTER_GRID_CELL_HEIGHT,
                             "", WHITE_BG, TEXT_COLOR, cell_font)
            draw_bordered_cell(draw, swap_x + swap_col_width, cell_y, swap_col_width, ROSTER_GRID_CELL_HEIGHT,
                             "", WHITE_BG, TEXT_COLOR, cell_font)
    
    # Save to BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)
    return buffer
