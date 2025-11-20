import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, scrolledtext, colorchooser
from PIL import Image, ImageTk

from backgroundannotator.services.background import (create_default_background, resize_image, add_text_to_image,
                                                     set_background)
from backgroundannotator.services.explorer import get_asset, select_files_from_explorer, save_file_via_explorer
from backgroundannotator import __version__, __title__


class MainWindow(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self._version = __version__
        self._title = __title__

        self._original_image: Image.Image | None = create_default_background()
        self._image_with_text: Image.Image | None = self._original_image.copy()
        self._preview_photo: Image.Image | None = None

        self._text_x_position_percent = tk.IntVar(value=50)
        self._text_y_position_percent = tk.IntVar(value=50)
        self._text_size = tk.IntVar(value=100)
        self._text_color_hex = tk.StringVar(value="#FFFFFF")

        self._canvas_height: int = 350

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and arrange widgets in the main window."""
        # Initialize the main window.
        self.title(string=self._title)
        self.minsize(width=680, height=650)
        self.iconbitmap(get_asset("assets/bob.ico"))

        # Create the content of the window.
        self._create_menu()
        self._create_file_selection_frame()
        self._create_notes_frame()
        self._create_text_options_frame()
        self._create_preview_frame()
        self._create_output_frame()

        # Put the preview image on the canvas.
        self._update_preview_image()

    def _create_menu(self) -> None:
        """Create the menu bar for the application."""
        menubar: tk.Menu = tk.Menu(master=self)

        # Adding the File menu.
        file_menu: tk.Menu = tk.Menu(master=menubar, tearoff=False)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Adding the Help menu.
        help_menu: tk.Menu = tk.Menu(master=menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._show_help)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Attach the menubar to the window.
        self.config(menu=menubar)

    def _create_file_selection_frame(self) -> None:
        """Create the file selection frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="x")
        frame.columnconfigure(index=1, weight=1)

        ttk.Label(master=frame, text="Select Image:").grid(row=0, column=0, padx=(0, 10), sticky="e")
        self._image_entry = ttk.Entry(master=frame, width=50)
        self._image_entry.grid(row=0, column=1, sticky="ew", rowspan=True, padx=(0, 10))
        self._image_entry.bind(sequence="<FocusOut>", func=lambda event: self._load_image())
        self._image_entry.focus_set()  # Set focus to the entry field.
        ttk.Button(master=frame, text="Browse...", command=self._browse_button_pressed
                   ).grid(row=0, column=2, padx=(0, 10), sticky="w")
        ttk.Button(master=frame, text="Default", command=lambda: self._load_image(default=True)
                   ).grid(row=0, column=3, sticky="w")

    def _create_notes_frame(self) -> None:
        """Create the notes frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="both", expand=True)

        ttk.Label(master=frame, text="Notes:").pack(anchor="nw")

        self._notes_text: scrolledtext.ScrolledText = scrolledtext.ScrolledText(master=frame, wrap="word", height=5)
        self._notes_text.pack(fill="both", expand=True, pady=(5, 0))

        # Bind typing events to trigger image updates
        self._notes_text.bind("<KeyRelease>", self._on_notes_key_release)
        self._notes_update_after_id: str | None = None

    def _create_text_options_frame(self) -> None:
        """Create the text position frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="x", expand=False)

        # Spacing between sections.
        column_spacing: int = 50

        # X and Y position spinboxes.
        ttk.Label(master=frame, text="Text Position:").grid(row=1, column=0, sticky='w')
        for row, (xi, direction) in enumerate(zip(('x', 'y'), ('Horizontal', 'Vertical')), start=2):
            ttk.Label(master=frame, text=f"{direction.title()} Position (%):"
                      ).grid(row=row, column=0, sticky='w', padx=(0, 5))
            spin = ttk.Spinbox(master=frame, from_=0, to=100, width=5, command=self._update_preview_image,
                               textvariable=getattr(self, f"_text_{xi}_position_percent"))
            spin.grid(row=row, column=1, sticky='w')
            spin.bind("<FocusOut>", lambda e: self._update_preview_image())
            spin.bind("<Enter>", lambda e: self._update_preview_image())

        # Font size spinbox.
        ttk.Label(master=frame, text="Text Size:").grid(row=1, column=3, sticky='w', padx=(column_spacing, 0))
        font_size_spin = ttk.Spinbox(master=frame, from_=1, to=3000, width=5, command=self._update_preview_image,
                                     textvariable=self._text_size)
        font_size_spin.grid(row=2, column=3, sticky='w', padx=(column_spacing, 0))
        font_size_spin.bind("<FocusOut>", lambda e: self._update_preview_image())
        font_size_spin.bind("<Enter>", lambda e: self._update_preview_image())

        # Text color selection.
        ttk.Label(master=frame, text="Text Color:").grid(row=1, column=4, sticky='w', padx=(column_spacing, 0))
        # Color entry field.
        color_entry = ttk.Entry(master=frame, width=10, textvariable=self._text_color_hex)
        color_entry.grid(row=2, column=4, sticky='w', padx=(column_spacing, 0))
        color_entry.bind("<FocusOut>", lambda e: self._update_preview_image())
        color_entry.bind("<Enter>", lambda e: self._update_preview_image())
        # Color swatch (small box showing the color).
        self._text_color_swatch: tk.Canvas = tk.Canvas(master=frame, width=20, height=20,
                                                       bg=self._text_color_hex.get(), borderwidth=1,
                                                       relief="solid")
        self._text_color_swatch.grid(row=2, column=5, sticky='w', padx=(5, 0))
        # Button to open color picker.
        ttk.Button(master=frame, text="Choose Color...", command=self._on_choose_text_color
                   ).grid(row=2, column=6, sticky='w', padx=(5, 0))

    def _create_preview_frame(self) -> None:
        """Create the preview frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="x", expand=False)

        ttk.Label(master=frame, text="Preview:").pack(anchor="nw")

        # Get the aspect ratio of the screen to set the preview canvas size accordingly.
        aspect_ratio: float = self._original_image.size[0] / self._original_image.size[1]
        canvas_width: int = int(self._canvas_height * aspect_ratio)
        self._preview_canvas: tk.Canvas = tk.Canvas(master=frame, bg="lightgray",
                                                    width=canvas_width, height=self._canvas_height)
        self._preview_canvas.pack(anchor='s', fill="none", expand=True, pady=(5, 0))

    def _create_output_frame(self) -> None:
        """Create the output frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="x")

        ttk.Button(master=frame, text="Save Image...", command=self._save_image).pack(side="right")

        ttk.Button(master=frame, text="Set as Desktop Background", command=self._set_as_background
                   ).pack(side="right", padx=(0, 10))

    def _on_choose_text_color(self) -> None:
        """Handle the text color selection."""
        # Open the color chooser dialog.
        color_code: str | None = colorchooser.askcolor(title="Choose Text Color",
                                                       initialcolor=self._text_color_hex.get())[1]
        if color_code:
            self._text_color_hex.set(color_code)
            self._text_color_swatch.config(bg=color_code)
            self._update_preview_image()

    def _load_image(self, default: bool = False) -> None:
        """Load the image as a PIL image and update the preview. If default is True, load the default background."""
        if default:
            self._original_image = create_default_background()
            self._image_with_text = self._original_image.copy()

            # Clear the image entry field.
            self._image_entry.delete(0, tk.END)
        else:

            image_path_str = self._image_entry.get().strip()
            if not image_path_str:
                return

            path = Path(image_path_str)
            if not path.is_file():
                messagebox.showerror("Error", "Selected file does not exist.")
                return

            try:
                img = Image.open(path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image:\n{e}")
                return

            # Store original image (RGBA is convenient for later drawing text/overlays).
            self._original_image = img.convert("RGBA")
            self._image_with_text = self._original_image.copy()

        # Rescale the canvas according to the new image's aspect ratio.
        aspect_ratio: float = self._original_image.size[0] / self._original_image.size[1]
        canvas_width: int = int(self._canvas_height * aspect_ratio)
        self._preview_canvas.config(width=canvas_width, height=self._canvas_height)

        # Draw it on the preview canvas (scaled).
        self._update_preview_image()

    def _on_notes_key_release(self, _: tk.Event) -> None:
        """Handle typing in the notes box with a short delay before updating."""
        # Cancel any scheduled update to prevent too frequent redraws
        if self._notes_update_after_id is not None:
            self.after_cancel(self._notes_update_after_id)

        # Schedule an update 300 ms after last key release
        self._notes_update_after_id = self.after(300, lambda _: self._update_preview_image(), ())

    def _update_preview_image(self) -> None:
        """Update the preview image on the canvas."""
        if self._original_image is None:
            return

        # Add the notes to the image.
        self._image_with_text = add_text_to_image(image=self._original_image,
                                                  text=self._notes_text.get("1.0", tk.END).strip(),
                                                  text_size=self._text_size.get(),
                                                  text_color=self._text_color_hex.get(),
                                                  text_position=(
                                                      int(self._text_x_position_percent.get() / 100
                                                          * self._original_image.size[0]),
                                                      int(self._text_y_position_percent.get() / 100
                                                          * self._original_image.size[1])
                                                  ))

        # Convert to PhotoImage for Tkinter.
        self._preview_photo = ImageTk.PhotoImage(resize_image(image=self._image_with_text, target_size=(650, 350)))

        # Clear the canvas and display the new image
        self._preview_canvas.delete("all")
        self._preview_canvas.create_image(
            0, 0,
            anchor="nw",
            image=self._preview_photo
        )

    def _browse_button_pressed(self) -> None:
        """Handle the browse button press event."""
        file_paths: tuple[Path, ...] = select_files_from_explorer(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                       ("All files", "*.*")],
            multiple=True
        )

        if file_paths:
            self._image_entry.delete(0, tk.END)
            self._image_entry.insert(0, str(file_paths[0]))
            self._load_image()

    def _save_image(self) -> None:
        """Save the annotated image."""
        # Ask the user where to save the image.
        save_path: Path | None = save_file_via_explorer()
        if save_path is None:
            return  # User canceled.

        image_to_save = self._image_with_text if self._image_with_text is not None else self._original_image
        if image_to_save is None:
            messagebox.showerror("Error", "No image to save.")
            return

        try:
            image_to_save.convert("RGB").save(save_path)
            messagebox.showinfo("Success", f"Image saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image:\n{e}")

    def _set_as_background(self) -> None:
        """Set the annotated image as the desktop background."""
        image_to_set = self._image_with_text if self._image_with_text is not None else self._original_image
        if image_to_set is None:
            messagebox.showerror("Error", "No image to set as background.")
            return

        try:
            set_background(source=image_to_set)
            messagebox.showinfo("Success", "Desktop background updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not set desktop background:\n{e}")

    def _show_about(self) -> None:
        """Show the dialog 'About'."""
        messagebox.showinfo(title="About",
                            message=f"{self._title}\n"
                                    f"Seppe Van Bogaert\n"
                                    f"Universiteit Gent\n"
                                    f"Version {self._version}\n"
                                    f"https://github.com/sevbogae/BackgroundAnnotator"
                            )

    @staticmethod
    def _show_help() -> None:
        """Show the dialog 'Help'."""
        messagebox.showinfo(title="Help",
                            message=f"BOB, which stands for Brain On Background, is an application to put notes onto your desktop background.\n\n"
                                    f"First, select an image file from your computer or use the default background (UGent blue with UGent logo). This will be the desktop image.\n\n"
                                    f"In the notes box, type the text you want to appear on your desktop background. You can adjust the position, size, and color of the text using the options provided.\n\n"
                                    f"The preview area shows how your desktop background will look with the notes overlaid.\n\n"
                                    f"Once you're satisfied with the appearance, you can either save the annotated image to your computer or set it directly as your desktop background using the provided buttons.\n\n"
                                    f"For the source code, visit GitHub: https://github.com/sevbogae/BackgroundAnnotator.git"
                            )

    def run(self) -> None:
        """Start the main event loop."""
        self.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
