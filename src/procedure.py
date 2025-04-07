from procedure.base import BufferTableGraphManager


def draw_buffer_directory(directory):
    manager = BufferTableGraphManager()
    manager.process_directory(directory)
    manager.visualize("Full Dependencies Graph")


if __name__ == "__main__":
    directory = input("Enter the directory path containing SQL files: ")
    draw_buffer_directory(directory)
