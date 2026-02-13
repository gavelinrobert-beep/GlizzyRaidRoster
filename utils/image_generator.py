"""Image generation utilities for roster calendar display."""
import io
from typing import List, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
from .constants import WOW_CLASS_COLORS


# Image configuration constants
CELL_WIDTH = 150
CELL_HEIGHT = 30
HEADER_HEIGHT = 40
PLAYER_STATS_WIDTH = 200
FONT_SIZE = 12
HEADER_FONT_SIZE = 14
PADDING = 5
BACKGROUND_COLOR = (44, 47, 51)  # #2C2F33 - Discord dark mode
TEXT_COLOR = (255, 255, 255)  # White
GRID_COLOR = (153, 170, 181)  # #99AAB5 - Light gray


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
    """Generate a visual roster calendar image.
    
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
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    # Calculate dimensions
    num_raids = len(raids_data)
    num_players = len(all_players)
    
    # Image dimensions
    total_width = PLAYER_STATS_WIDTH + (num_raids * CELL_WIDTH) + PADDING * 2
    total_height = HEADER_HEIGHT + (num_players * CELL_HEIGHT) + PADDING * 2
    
    # Create image
    img = Image.new('RGB', (total_width, total_height), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    header_font = get_font(HEADER_FONT_SIZE)
    cell_font = get_font(FONT_SIZE)
    
    # Draw header row
    y_offset = PADDING
    
    # Player stats header
    x_offset = PADDING
    rect = (x_offset, y_offset, x_offset + PLAYER_STATS_WIDTH, y_offset + HEADER_HEIGHT)
    draw.rectangle(rect, outline=GRID_COLOR, width=2)
    draw_text_centered(draw, rect, "Player (Raids/Benches)", header_font, TEXT_COLOR)
    
    # Raid date headers
    x_offset += PLAYER_STATS_WIDTH
    for raid, _ in raids_data:
        rect = (x_offset, y_offset, x_offset + CELL_WIDTH, y_offset + HEADER_HEIGHT)
        draw.rectangle(rect, outline=GRID_COLOR, width=2)
        # Format date nicely
        date_text = raid.raid_date
        if len(date_text) > 10:
            date_text = date_text[:10]
        draw_text_centered(draw, rect, date_text, header_font, TEXT_COLOR)
        x_offset += CELL_WIDTH
    
    # Create a mapping of players to their assignments for each raid
    player_assignments = {}
    for player in all_players:
        player_assignments[player.player_id] = {}
        for raid, roster_data in raids_data:
            player_assignments[player.player_id][raid.raid_id] = None
            for assignment, p, class_name in roster_data:
                if p.player_id == player.player_id:
                    player_assignments[player.player_id][raid.raid_id] = (assignment.status, class_name, assignment.character_name)
                    break
    
    # Draw player rows
    y_offset += HEADER_HEIGHT
    for player in all_players:
        x_offset = PADDING
        
        # Player stats cell
        rect = (x_offset, y_offset, x_offset + PLAYER_STATS_WIDTH, y_offset + CELL_HEIGHT)
        draw.rectangle(rect, outline=GRID_COLOR, width=1)
        
        stats_text = f"{player.player_name} ({player.total_raids_rostered}/{player.total_benches})"
        stats_text = truncate_text(stats_text, PLAYER_STATS_WIDTH - PADDING * 2, cell_font, draw)
        draw.text((x_offset + PADDING, y_offset + PADDING), stats_text, font=cell_font, fill=TEXT_COLOR)
        
        # Assignment cells
        x_offset += PLAYER_STATS_WIDTH
        for raid, _ in raids_data:
            rect = (x_offset, y_offset, x_offset + CELL_WIDTH, y_offset + CELL_HEIGHT)
            
            assignment_data = player_assignments[player.player_id].get(raid.raid_id)
            
            if assignment_data:
                status, class_name, char_name = assignment_data
                
                # Determine background color based on status and class
                if status == "main":
                    # Use class color
                    bg_color = hex_to_rgb(WOW_CLASS_COLORS.get(class_name, 0x808080))
                elif status == "bench":
                    # Darker version of class color
                    base_color = hex_to_rgb(WOW_CLASS_COLORS.get(class_name, 0x808080))
                    bg_color = tuple(c // 2 for c in base_color)
                elif status == "absent":
                    # Red tint
                    bg_color = (100, 50, 50)
                elif status == "swap":
                    # Orange/yellow tint
                    bg_color = (120, 100, 50)
                else:
                    bg_color = BACKGROUND_COLOR
                
                # Draw colored cell
                draw.rectangle(rect, fill=bg_color, outline=GRID_COLOR, width=1)
                
                # Draw character name
                char_text = truncate_text(char_name, CELL_WIDTH - PADDING * 2, cell_font, draw)
                draw.text((x_offset + PADDING, y_offset + PADDING), char_text, font=cell_font, fill=TEXT_COLOR)
            else:
                # Empty cell
                draw.rectangle(rect, outline=GRID_COLOR, width=1)
            
            x_offset += CELL_WIDTH
        
        y_offset += CELL_HEIGHT
    
    # Save to BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
