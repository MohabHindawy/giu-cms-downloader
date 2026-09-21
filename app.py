import sys

def main():
    start_in_tray = "--tray" in sys.argv
    from ui.main_window import MainWindow
    app = MainWindow(start_in_tray=start_in_tray)
    
    from core.single_instance import setup_single_instance
    setup_single_instance(app)
    
    app.mainloop()

if __name__ == "__main__":
    main()