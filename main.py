import os
import sys
from importlib import reload

from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from constants import *
from tasks.task_manager import TaskManager


class ProjectChangeHandler(FileSystemEventHandler):
    """
    Class to handle file system events and reload modules if necessary.
    """

    @staticmethod
    def get_module_name(file_path):
        """Returns the module name from the given file path."""
        relative_path = os.path.relpath(file_path, os.getcwd())
        return relative_path.replace(os.sep, ".").rstrip(".py")

    @staticmethod
    def reload_module(module_name):
        """Reloads the given module name if it exists in sys.modules."""
        if module_name in sys.modules:
            try:
                reload(sys.modules[module_name])
                print(f"Module {module_name} reloaded successfully!")
            except Exception as e:
                print(f"Error reloading module {module_name}: {e}")

    def on_modified(self, event):
        """Reloads the module if a python file is modified."""
        if event.src_path.endswith(PYTHON_EXTENSION):
            module_name = self.get_module_name(event.src_path)
            self.reload_module(module_name)

    def on_created(self, event):
        """Prints a message if a new python file is created."""
        if event.src_path.endswith(PYTHON_EXTENSION):
            print(f"New file detected: {event.src_path}. You can integrate it dynamically.")


def load_env_file():
    """Loads the .env file or exits the program if the file is not found."""
    if not os.path.exists(ENV_FILE):
        print("Error: .env file not found. Please run the setup script first.")
        sys.exit(1)
    load_dotenv(ENV_FILE)


def display_menu():
    """Displays the main menu and returns the user's choice."""
    print("\n=== Shapeshifter Main Menu ===")
    options = [
        "Analyze the entire project",
        "Create a new Python script",
        "Modify an existing Python script",
        "Refine the entire project",
        "Push changes to GitHub",
        "Exit",
    ]
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    return input("Choose an option: ").strip()


def handle_menu_choice(choice):
    """Handles the user's menu choice."""
    task_manager = TaskManager()

    script_prompt = input(NEW_SCRIPT_PROMPT).strip()
    script_desc = input(SCRIPT_DESC_PROMPT).strip()
    existing_script = input(EXISTING_SCRIPT_PROMPT).strip()
    modif_desc = input(MODIF_DESC_PROMPT).strip()
    commit_msg = input(COMMIT_MSG_PROMPT).strip()

    task_map = {
        "1": task_manager.analyze_project,
        "2": lambda: task_manager.create_script(script_prompt, script_desc),
        "3": lambda: task_manager.modify_script(existing_script, modif_desc),
        "4": task_manager.refine_project,
        "5": lambda: task_manager.push_to_github(commit_msg),
    }

    if choice == "6":
        print("Exiting Shapeshifter. Goodbye!")
        return False

    try:
        task_map.get(choice, lambda: print("Invalid choice. Please try again."))()
    except Exception as e:
        print(f"An unexpected error occurred while processing your choice: {e}")
    return True


def main():
    """Main function to run the program."""
    print("Welcome to Shapeshifter!")
    print("Your AI-powered Python project manager with real-time updates.")
    load_env_file()

    handler = ProjectChangeHandler()
    observer = Observer()
    observer.schedule(handler, path=os.getcwd(), recursive=True)
    observer.start()
    print("Started watching project directory for real-time updates.")

    try:
        while handle_menu_choice(display_menu()):
            pass
    except KeyboardInterrupt:
        print("\nStopping Shapeshifter.")
    finally:
        observer.stop()
        observer.join()
        print("Shapeshifter has stopped.")


if __name__ == "__main__":
    main()