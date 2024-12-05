import os
import sys
from importlib import reload

from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from constants import *
from tasks.task_manager import TaskManager


class FileChangeHandler(FileSystemEventHandler):
    @staticmethod
    def get_module_name(file_path):
        relative_path = os.path.relpath(file_path, os.getcwd())
        return relative_path.replace(os.sep, ".").rstrip(".py")

    @staticmethod
    def reload_module(module_name):
        if module_name in sys.modules:
            try:
                reload(sys.modules[module_name])
                print(f"Module {module_name} reloaded successfully!")
            except Exception as e:
                print(f"Error reloading module {module_name}: {e}")

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            module_name = self.get_module_name(event.src_path)
            self.reload_module(module_name)

    def on_created(self, event):
        if event.src_path.endswith('.py'):
            print(f"New file detected: {event.src_path}. You can integrate it dynamically.")


def load_environment_variables():
    if not os.path.exists('.env'):
        print("Error: .env file not found. Please run the setup script first.")
        sys.exit(1)
    load_dotenv('.env')


def display_main_menu():
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


def get_user_input():
    return {
        "script_prompt": input("Enter the name of the new script: ").strip(),
        "script_desc": input("Enter a description for the new script: ").strip(),
        "existing_script": input("Enter the name of the existing script: ").strip(),
        "modif_desc": input("Enter a description for the modifications: ").strip(),
        "commit_msg": input("Enter a commit message: ").strip()
    }


def process_user_choice(choice, user_input):
    task_manager = TaskManager()

    task_map = {
        "1": task_manager.analyze_project,
        "2": lambda: task_manager.create_script(user_input["script_prompt"], user_input["script_desc"]),
        "3": lambda: task_manager.modify_script(user_input["existing_script"], user_input["modif_desc"]),
        "4": task_manager.refine_project,
        "5": lambda: task_manager.push_to_github(user_input["commit_msg"]),
    }

    if choice == "6":
        print("Exiting Shapeshifter. Goodbye!")
        return False

    try:
        task_map.get(choice, lambda: print("Invalid choice. Please try again."))()
    except Exception as e:
        print(f"An unexpected error occurred while processing your choice: {e}")
    return True


def setup_file_observer():
    handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(handler, path=os.getcwd(), recursive=True)
    observer.start()
    print("Started watching project directory for real-time updates.")
    return observer


def run_main_loop(observer):
    try:
        user_input = get_user_input()
        while process_user_choice(display_main_menu(), user_input):
            pass
    except KeyboardInterrupt:
        print("\nStopping Shapeshifter.")
    finally:
        observer.stop()
        observer.join()
        print("Shapeshifter has stopped.")


def main():
    print("Welcome to Shapeshifter!")
    print("Your AI-powered Python project manager with real-time updates.")
    load_environment_variables()

    observer = setup_file_observer()
    run_main_loop(observer)


if __name__ == "__main__":
    main()