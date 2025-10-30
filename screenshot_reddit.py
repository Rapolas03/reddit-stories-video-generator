from PIL import Image, ImageDraw, ImageFont
import os
import platform

class RedditPostImage:
    def __init__(self, output_dir="assets/screenshots", logo_path="assets/redditlogo.png"):
        self.output_dir = output_dir
        self.logo_path = logo_path
        os.makedirs(output_dir, exist_ok=True)
        
        # Reddit-like color scheme
        self.bg_color = (26, 26, 27)      # Dark background
        self.card_color = (30, 30, 31)    # Card background
        self.title_color = (215, 218, 220)
        self.body_color = (129, 131, 132)
        self.upvote_color = (255, 69, 0)
    
    def _get_font_path(self):
        """Return a system font path based on OS, or None if not found."""
        system = platform.system()
        candidates = []

        if system == "Darwin":  # macOS
            candidates = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Arial.ttf"
            ]
        elif system == "Windows":
            candidates = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "C:\\Windows\\Fonts\\segoeui.ttf"
            ]
        else:  # Linux / other
            candidates = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
            ]
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        return None  # fallback
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width pixels."""
        lines = []
        words = text.split()
        if not words:
            return lines

        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + ' ' + word
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines
        
    def create_post_image(self, title, body="", subreddit="r/example", width=1080, padding=40):
        """Create a Reddit-style post image."""
        font_path = self._get_font_path()

        if font_path:
            title_font = ImageFont.truetype(font_path, 36)
            body_font = ImageFont.truetype(font_path, 28)
            sub_font = ImageFont.truetype(font_path, 24)
        else:
            print("Warning: no system font found, using default Pillow font.")
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
        
        card_margin = 20
        text_margin = padding + 20
        available_width = width - (card_margin * 2) - (text_margin * 2)
        
        title_lines = self.wrap_text(title, title_font, available_width)
        body_lines = self.wrap_text(body, body_font, available_width) if body else []
        
        title_line_height = 50
        body_line_height = 40
        title_height = len(title_lines) * title_line_height
        body_height = len(body_lines) * body_line_height if body_lines else 0
        
        total_height = (
            padding + 40 + title_height + 
            (30 if body_height > 0 else 0) + 
            body_height + padding
        )
        
        img = Image.new('RGB', (width, int(total_height)), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        draw.rounded_rectangle(
            [card_margin, card_margin, width - card_margin, total_height - card_margin],
            radius=15, fill=self.card_color
        )
        
        # Draw logo if available
        if os.path.exists(self.logo_path):
            try:
                logo = Image.open(self.logo_path).convert('RGBA')
                logo_size = 60
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                logo_x = width - logo_size - card_margin - 20
                logo_y = card_margin + 20
                img.paste(logo, (logo_x, logo_y), logo)
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")
        
        y_position = padding + 20
        draw.text((text_margin, y_position), subreddit, fill=self.body_color, font=sub_font)
        y_position += 40
        
        for line in title_lines:
            draw.text((text_margin, y_position), line, fill=self.title_color, font=title_font)
            y_position += title_line_height
        
        if body_lines:
            y_position += 30
            for line in body_lines:
                draw.text((text_margin, y_position), line, fill=self.body_color, font=body_font)
                y_position += body_line_height
        
        filename = "new.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        print(f"Post image created: {filepath}")
        return filepath

    def create_from_json(self, json_path="assets/post_data.json"):
        import json
        with open(json_path, 'r') as f:
            post_data = json.load(f)
        return self.create_post_image(
            title=post_data['title'],
            body=post_data.get('body', ''),
            subreddit=post_data['subreddit']
        )

if __name__ == "__main__":
    creator = RedditPostImage()
    if os.path.exists("assets/post_data.json"):
        creator.create_from_json()
    else:
        creator.create_post_image(
            title="AITA for telling my sister she can't come to my wedding?",
            body="Long story short, my sister has been really toxic lately and I don't want that energy at my wedding...",
            subreddit="r/AmItheAsshole"
        )
