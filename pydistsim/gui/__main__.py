try:
    from .simulationgui import main
except ImportError:
    from pydistsim.gui.simulationgui import main

if __name__ == "__main__":
    main()
