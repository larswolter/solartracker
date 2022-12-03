from PIL import Image, ImageDraw, ImageFont

width = 128
height = 64

image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
defaultFont = ImageFont.load_default()

# Load bigger font.
font = ImageFont.load('10x20.pil')

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

def drawLines(lines):
    """
    Draw lines onto image and return
    """


    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Write four lines of text.

    for line in range(len(lines)):
        if line > 2:
            draw.text((x, top + 40+(line-2)*11), lines[line], font=defaultFont, fill=255)
        else:
            draw.text((x, top + line*20), lines[line], font=font, fill=255)
    return image
