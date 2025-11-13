import platform
import tempfile
from pathlib import Path
import ctypes
from typing import Union

from PIL import Image, ImageFont, ImageDraw

from backgroundannotator.services.explorer import get_asset


def create_default_background(screen_size: tuple[int, int] = (1920, 1080),
                              ugent_logo_margin: int = 100,
                              ugent_logo_width: int = 400) -> Image:
    """Create an empty desktop background. The empty background is a blue (#1E64C8) image with the logo of Ghent
    University in the right top corner.

    Parameters
    ----------
    screen_size : tuple[int, int], optional
        The size of the screen (width, height), by default (1920, 1080).
    ugent_logo_margin : int, optional
        The margin between the logo and the edges of the screen, by default 100.
    ugent_logo_width : int, optional
        The width of the logo, by default 400.

    Returns
    -------
    Image
        The created empty desktop background.
    """
    # Create a new image with the size of the screen.
    image = Image.new(mode="RGB", size=screen_size, color="#1E64C8")

    # Load the logo of Ghent University.
    logo = Image.open(get_asset("assets/logo_ugent.png"))

    # Resize the logo to a width of 200 pixels
    width, height = logo.size
    logo.thumbnail(size=(ugent_logo_width, int(ugent_logo_width * height / width) + 1),
                   resample=Image.Resampling.LANCZOS)

    # Paste the logo in the right top corner using its alpha channel as a mask.
    image.paste(im=logo, box=(screen_size[0] - ugent_logo_width - ugent_logo_margin, ugent_logo_margin), mask=logo)

    return image


def resize_image(image: Image, target_size: tuple[int, int], keep_aspect_ratio: bool = True,
                 in_place: bool = False) -> Image:
    """Resize an image to the target size.

    Parameters
    ----------
    image : Image
        The image to resize.
    target_size : tuple[int, int]
        The target size (width, height).
    keep_aspect_ratio : bool, optional
        Whether to keep the aspect ratio of the image, by default True. If True, the image will be rescaled to fit
        within the target size while maintaining its aspect ratio.
    in_place : bool, optional
        Whether to resize the image in place, by default False. If False, a copy of the image will be resized.

    Returns
    -------
    Image
        The resized image.
    """
    # Copy the original image to avoid modifying it.
    if not in_place:
        image = image.copy()

    if keep_aspect_ratio:
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        return image
    return image.resize(target_size, Image.Resampling.LANCZOS)


def add_text_to_image(image: Image, text: str, text_position: tuple[int, int] = (500, 200),
                      text_size: int = 100, text_color: str = "#FFFFFF") -> Image:
    """Add text to an image.

    Parameters
    ----------
    image : Image
        The image to add text to.
    text : str
        The text to add to the image.
    text_position : tuple[int, int], optional
        The position to add the text to, by default (500, 200).
    text_size : int, optional
        The size of the text, by default 10.
    text_color : str, optional
        The color of the text, by default "#FFFFFF".

    Returns
    -------
    Image
        The image with the text added.
    """
    # Load the font.
    font = ImageFont.truetype(font=get_asset("assets/font_ugent.ttf"), size=text_size)

    # Copy the image, so we don't modify the original one.
    image = image.copy()

    # Create a drawing object.
    draw = ImageDraw.Draw(image)

    # Add the text to the image.
    draw.text(xy=text_position, text=text, font=font, fill=text_color)

    return image


def set_background(source: Union[Image.Image, Path, str]) -> Path:
    """Set the desktop background on Windows.

    Parameters
    ----------
    source :
        Either a PIL Image object or a path (str/Path) to an existing image file.

    Returns
    -------
    Path
        The path of the image file that was actually used as wallpaper
        (useful if a temporary file was created).

    Raises
    ------
    NotImplementedError
        If called on a non-Windows platform.
    FileNotFoundError
        If a path is given and the file does not exist.
    RuntimeError
        If the Windows API call fails.
    """
    if platform.system() != "Windows":
        raise NotImplementedError("set_background is only implemented for Windows.")

    # Decide whether we need to save a temp file.
    if isinstance(source, Image.Image):
        # Save to a temporary BMP file (historically safest for Windows).
        img = source.convert("RGB")
        tmp = tempfile.NamedTemporaryFile(suffix=".bmp", delete=False)
        tmp_path = Path(tmp.name)
        tmp.close()
        img.save(tmp_path, format="BMP")
        image_path = tmp_path
    else:
        # Treat as path.
        image_path = Path(source).expanduser().resolve()
        if not image_path.is_file():
            raise FileNotFoundError(f"Wallpaper file does not exist: {image_path}")

    # Call Windows API
    result = ctypes.windll.user32.SystemParametersInfoW(
        20,  # SPI_SETDESKWALLPAPER.
        0,
        str(image_path),
        0x01 | 0x02,  # SPIF_UPDATEINIFILE | SPIF_SENDCHANGE.
    )

    if result == 0:
        raise RuntimeError("Failed to set wallpaper via SystemParametersInfoW.")

    # Delete temporary file if the source was a PIL image.
    if isinstance(source, Image.Image):
        try:
            image_path.unlink()
        except OSError:
            pass

    return image_path


def save_image(image: Image, path: Path) -> None:
    """Save the image to the specified path.

    Parameters
    ----------
    image : Image
        The image to save.
    path : Path
        The path to save the image to.
    """
    image.save(path)
