FONT = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"


def _escape(text):
    text = str(text)
    text = text.replace("\\", r"\\")
    text = text.replace("'", r"\'")
    text = text.replace(":", r"\:")
    text = text.replace(",", r"\,")

    return text


def style_7(hotel_number, hotel_name):
    number = _escape(f"NO. {hotel_number}")
    name = _escape(hotel_name)

    font = FONT.replace("\\", "/").replace(":", r"\:")
    font_bold = FONT_BOLD.replace("\\", "/").replace(":", r"\:")

    flash = (
        "if(lt(t\\,0.12)\\,"
        "0.35+0.65*t/0.12\\,"
        "1)"
    )

    return (
        # Light black background behind the title
        # BLACK BACKGROUND
        "drawbox="
        "x=50:"
        "y=h-315:"
        "w=650:"
        "h=235:"
        "color=black@0.65:"
        "t=fill:"
        "enable='between(t,0,5)',"

        # Blue vertical line
        "drawbox="
        "x=70:"
        "y=h-300:"
        "w=7:"
        "h=170:"
        "color=00AEEF:"
        "t=fill:"
        "enable='between(t,0,5)',"

        f"drawtext="
        f"fontfile='{font}':"
        f"text='{number}':"
        f"x=105:"
        f"y=h-292:"
        f"fontsize=58:"
        f"fontcolor=white:"
        f"bordercolor=black@0.45:"
        f"borderw=2:"
        f"alpha='{flash}':"
        f"enable='between(t,0,5)',"

        f"drawtext="
        f"fontfile='{font_bold}':"
        f"text='{name}':"
        f"x=105:"
        f"y=h-210:"
        f"fontsize=62:"
        f"fontcolor=00AEEF:"
        f"bordercolor=black@0.45:"
        f"borderw=2:"
        f"shadowcolor=00AEEF@0.35:"
        f"shadowx=2:"
        f"shadowy=2:"
        f"alpha='{flash}':"
        f"enable='between(t,0,5)'"
    )


def get_overlay(style, hotel_number, hotel_name):
    return style_7(hotel_number, hotel_name)
