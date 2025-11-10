import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from importlib import metadata

from backgroundannotator.services.explorer import get_asset, select_files_from_explorer


class MainWindow(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self._version = metadata.version("backgroundannotator")
        self._title = metadata.metadata("backgroundannotator").get("Summary", "BOB: Brain On Background")

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and arrange widgets in the main window."""
        # Initialize the main window.
        self.title(string=self._title)
        self.minsize(width=750, height=460)
        self.iconbitmap(get_asset("assets/bob.ico"))

        # Create the content of the window.
        self._create_menu()
        self._create_file_selection_frame()
        self._create_notes_frame()
        self._create_preview_frame()
        self._create_output_frame()

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

    def _create_notes_frame(self) -> None:
        """Create the notes frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="both", expand=True)

        ttk.Label(master=frame, text="Notes:").pack(anchor="nw")

        self._notes_text: tk.Text = tk.Text(master=frame, wrap="word")
        self._notes_text.pack(fill="both", expand=True, pady=(5, 0))

    def _create_preview_frame(self) -> None:
        """Create the preview frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="both", expand=True)

        ttk.Label(master=frame, text="Preview:").pack(anchor="nw")

        self._preview_canvas: tk.Canvas = tk.Canvas(master=frame, bg="lightgray")
        self._preview_canvas.pack(fill="both", expand=True, pady=(5, 0))

    def _create_output_frame(self) -> None:
        """Create the output frame."""
        frame: ttk.Frame = ttk.Frame(master=self, padding="10")
        frame.pack(fill="x")

        ttk.Button(master=frame, text="Save Image", command=self._save_image).pack(side="right")

        ttk.Button(master=frame, text="Set as Desktop Background", command=self._set_as_background
                   ).pack(side="right", padx=(0, 10))

    def _load_image(self) -> None:
        """Load the image from the specified path."""
        image_path: str = self._image_entry.get()

        if not image_path:
            return

        print(f"Loading image from: {image_path}")

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
        print("Saving the annotated image...")

    def _set_as_background(self) -> None:
        """Set the annotated image as the desktop background."""
        print("Setting the annotated image as desktop background...")

    def _show_about(self) -> None:
        """Show the dialog 'About'."""
        messagebox.showinfo(title="About",
                            message=f"{self._title}\n"
                                    f"Seppe Van Bogaert\n"
                                    f"Universiteit Gent\n"
                                    f"Version {'.'.join([str(i) for i in self._version])}\n"
                                    f"https://github.com/sevbogae/BackgroundAnnotator"
                            )

    @staticmethod
    def _show_help() -> None:
        """Show the dialog 'Help'."""
        messagebox.showinfo(title="Help",
                            message=f"BOB, which stands for Brain On Background, is an application to put notes onto your desktop background.\n\n"
                                    f""
                                    f"For the source code, visit GitHub: https://github.com/sevbogae/BackgroundAnnotator.git"
                            )

    def run(self) -> None:
        """Start the main event loop."""
        self.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
