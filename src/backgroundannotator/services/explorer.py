# -*- coding: utf-8 -*-
"""
Explorer services
-----------------

This module provides utility functions for file selection dialogs, opening websites, and retrieving asset paths.
"""
import sys
import webbrowser
from pathlib import Path
from tkinter import filedialog
from typing import Literal


def select_files_from_explorer(filetypes: list[tuple[str, str]], multiple: bool = True) -> tuple[Path, ...]:
    """Open a file dialog to select one or more files.

    Parameters
    ----------
    filetypes : list[tuple[str, str]]
        A list of tuples specifying the file types to filter in the dialog.
        Each tuple should contain a description and a file extension pattern.
    multiple : bool, optional
        If True, allows selection of multiple files. If False, only a single file can be selected.
        Default is True.

    Returns
    -------
    tuple[Path, ...]
        A tuple of selected file paths. If no files are selected, it returns an empty tuple.
    """
    if multiple:
        file_paths: tuple[str, ...] | Literal[""] = filedialog.askopenfilenames(
            title="Select File(s)",
            filetypes=filetypes
        )
    else:
        file_path: str | Literal[""] = filedialog.askopenfilename(
            title="Select File",
            filetypes=filetypes
        )
        file_paths = (file_path,) if file_path else ()

    return tuple(Path(path) for path in file_paths if path)  # Filter out empty strings (if user canceled).


def save_file_via_explorer() -> Path | None:
    """Open a file dialog to save a file.

    Returns
    -------
    Path | None
        The path where the file is to be saved. If the user cancels the dialog, returns None.
    """
    file_path: str | Literal[""] = filedialog.asksaveasfilename(
        title="Save Image",
        defaultextension=".png",
    )

    return Path(file_path) if file_path else None  # Return None if user canceled.


def open_website(url: str) -> None:
    """Open a website in the default web browser.

    Parameters
    ----------
    url : str
        The URL of the website to open.
    """
    webbrowser.open(url)


def get_asset(relative_path: str) -> Path:
    """Get the absolute path to an asset file.

    Parameters
    ----------
    relative_path: str
        The relative path to the asset file.

    Returns
    -------
    str
        The absolute path to the asset file.
    """
    # Check if the application is run from a frozen state (e.g., an executable created with PyInstaller).
    # PyInstaller sets sys.frozen to True and uses sys._MEIPASS to store the temporary directory.
    if getattr(sys, "frozen", False):  # Returns False if the attribute 'frozen' does not exist.
        # We are running in a frozen state, i.e., from the executable. We need to use the temporary directory
        # created by PyInstaller: sys._MEIPASS.
        base: Path = Path(getattr(sys, "_MEIPASS"))  # Since there is no default value, we can use getattr safely.
    else:
        # We are not running in a frozen state, i.e., from the source code. Use the current directory.
        # __file__ is the path to the current file.
        # resolve() gives the absolute path.
        # parent.parent goes two levels up to the root of the project (one level would be the utils directory).
        base = Path(__file__).resolve().parent.parent

    return base / relative_path
