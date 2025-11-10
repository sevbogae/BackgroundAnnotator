import tkinter as tk
from tkinter import ttk, messagebox
from importlib import metadata


class MainWindow(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self._version = metadata.version("backgroundannotator")
        self._title = metadata.metadata("backgroundannotator")
        print(self._title)

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and arrange widgets in the main window."""
        # M

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
