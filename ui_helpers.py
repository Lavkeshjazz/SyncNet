import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion

class PathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        dirname = os.path.dirname(text) or "."
        try:
            entries = os.listdir(dirname)
        except FileNotFoundError:
            return

        for entry in entries:
            full_path = os.path.join(dirname, entry)
            if os.path.isdir(full_path):
                display = f"{entry}/"
            else:
                display = entry
            yield Completion(
                text=os.path.join(dirname, entry),
                start_position=-len(text),
                display=display
            )

def get_file_path():
    while True:
        file_path = prompt("📁 Select file: ", completer=PathCompleter(), complete_while_typing=True)
        if os.path.isfile(file_path):
            return file_path
        print("❌ Invalid file. Please try again.")
