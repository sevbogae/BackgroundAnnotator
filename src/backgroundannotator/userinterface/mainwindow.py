import tkinter as tk
from tkinter import ttk


class MainWindow(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and arrange widgets in the main window."""
        ...

    def run(self) -> None:
        """Start the main event loop."""
        self.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
