from PIL import Image, ImageDraw, ImageFont
import os

class RedditPostImage:
    def __init__(self, output_dir="assets/screenshots", logo_path="assets/redditlogo.png"):
        self.output_dir = output_dir
        self.logo_path = logo_path
        os.makedirs(output_dir, exist_ok=True)
        
        # Reddit-like color scheme
        self.bg_color = (26, 26, 27)  # Dark background
        self.card_color = (30, 30, 31)  # Card background
        self.title_color = (215, 218, 220)  # White-ish
        self.body_color = (129, 131, 132)  # Gray
        self.upvote_color = (255, 69, 0)  # Reddit orange
    
    def wrap_text(self, text, font, max_width):
        """
        Wrap text to fit within max_width pixels
        
        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels
        
        Returns:
            List of lines
        """
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
        
    def create_post_image(self, title, body, subreddit="r/AskReddit", width=1080, padding=40):
        """
        Create a Reddit-style post image
        
        Args:
            title: Post title
            body: Post body text
            subreddit: Subreddit name
            width: Image width in pixels
            padding: Padding around content
        
        Returns:
            Path to the saved image
        """
        # Try to load fonts, fall back to default if not available
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            sub_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
        
        # Calculate available width for text
        card_margin = 20
        text_margin = padding + 20
        available_width = width - (card_margin * 2) - (text_margin * 2)
        
        # Wrap text properly based on pixel width
        title_lines = self.wrap_text(title, title_font, available_width)
        body_lines = self.wrap_text(body, body_font, available_width) if body else []
        
        # Calculate heights
        title_line_height = 50
        body_line_height = 40
        
        title_height = len(title_lines) * title_line_height
        body_height = len(body_lines) * body_line_height if body_lines else 0
        
        # Calculate total height
        total_height = (
            padding +           # Top padding
            40 +               # Subreddit name height
            title_height +     # Title height
            (30 if body_height > 0 else 0) +  # Space between title and body
            body_height +      # Body height
            padding            # Bottom padding
        )
        
        # Create the image
        img = Image.new('RGB', (width, int(total_height)), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw card background
        draw.rounded_rectangle(
            [card_margin, card_margin, width - card_margin, total_height - card_margin],
            radius=15,
            fill=self.card_color
        )
        
        # Load and paste Reddit logo in top-right corner
        if os.path.exists(self.logo_path):
            try:
                logo = Image.open(self.logo_path)
                
                # Convert to RGBA to handle transparency properly and avoid warnings
                if logo.mode != 'RGBA':
                    logo = logo.convert('RGBA')
                
                # Resize logo to reasonable size (e.g., 60x60 pixels)
                logo_size = 60
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Position in top-right corner with some margin
                logo_x = width - logo_size - card_margin - 20
                logo_y = card_margin + 20
                
                # Paste with alpha channel as mask
                img.paste(logo, (logo_x, logo_y), logo)
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")
        
        y_position = padding + 20
        
        # Draw subreddit name
        draw.text((text_margin, y_position), subreddit, fill=self.body_color, font=sub_font)
        y_position += 40
        
        # Draw title (line by line)
        for line in title_lines:
            draw.text(
                (text_margin, y_position),
                line,
                fill=self.title_color,
                font=title_font
            )
            y_position += title_line_height
        
        # Add spacing before body
        if body_lines:
            y_position += 30
        
        # Draw body (line by line)
        for line in body_lines:
            draw.text(
                (text_margin, y_position),
                line,
                fill=self.body_color,
                font=body_font
            )
            y_position += body_line_height
        
        # Save the image
        filename = f"reddit_post_{title[:30].replace(' ', '_').replace('/', '_')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        print(f"Post image created: {filepath}")
        return filepath

    def create_from_json(self, json_path="assets/post_data.json"):
        """
        Create post image from the JSON file created by reddit_fetcher.py
        
        Args:
            json_path: Path to the post data JSON file
        
        Returns:
            Path to the saved image
        """
        import json
        
        with open(json_path, 'r') as f:
            post_data = json.load(f)
        
        return self.create_post_image(
            title=post_data['title'],
            body=post_data['body']
        )

# Example usage
if __name__ == "__main__":
    creator = RedditPostImage()
    
    # Create from existing JSON (after running reddit_fetcher.py)
    if os.path.exists("assets/post_data.json"):
        creator.create_from_json()
    else:
        # Or create directly
        creator.create_post_image(
            title="AITA for telling my sister she can't come to my wedding?",
            body="Long story short, my sister has been really toxic lately and I don't want that energy at my wedding...",
            subreddit="r/AmItheAsshole"
        )