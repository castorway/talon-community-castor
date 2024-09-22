import os
import subprocess

from talon import Context, Module, app

# path to community/knausj root directory
REPO_DIR = os.path.dirname(os.path.dirname(__file__))
SETTINGS_DIR = os.path.join(REPO_DIR, "settings")
# path to secret settings dir for my words
SECRET_SETTINGS_DIR = os.path.join("/home/sintacks/.talon/user/castor-talon/settings")

mod = Module()
ctx = Context()
mod.list(
    "edit_file",
    desc="Absolute paths to frequently edited files (Talon list, CSV, etc.)",
)

_edit_files = {
    "additional words": os.path.join(SECRET_SETTINGS_DIR, "vocabulary.talon-list"),
    "alphabet": os.path.join(SECRET_SETTINGS_DIR, "letter.talon-list"),
    "homophones": os.path.join(SECRET_SETTINGS_DIR, "homophones.csv"),
    "search engines": os.path.join(SECRET_SETTINGS_DIR, "search_engine.talon-list"),
    "unix utilities": os.path.join(SECRET_SETTINGS_DIR, "unix_utility.talon-list"),
    "websites": os.path.join(SECRET_SETTINGS_DIR, "website.talon-list"),
}

_settings_csvs = {
    name: os.path.join(SECRET_SETTINGS_DIR, file_name)
    for name, file_name in {
        "abbreviations": "abbreviations.csv",
        "file extensions": "file_extensions.csv",
        "words to replace": "words_to_replace.csv",
    }.items()
}

_edit_files.update(_settings_csvs)
ctx.lists["self.edit_file"] = _edit_files


@mod.action_class
class ModuleActions:
    def edit_text_file(path: str):
        """Tries to open a file in the user's preferred text editor."""


winctx, linuxctx, macctx = Context(), Context(), Context()
winctx.matches = "os: windows"
linuxctx.matches = "os: linux"
macctx.matches = "os: mac"


@winctx.action_class("self")
class WinActions:
    def edit_text_file(path):
        # If there's no applications registered that can open the given type
        # of file, 'edit' will fail, but 'open' always gives the user a
        # choice between applications.
        try:
            os.startfile(path, "edit")
        except OSError:
            os.startfile(path, "open")


@macctx.action_class("self")
class MacActions:
    def edit_text_file(path):
        # -t means try to open in a text editor.
        open_with_subprocess(path, ["/usr/bin/open", "-t", path])


@linuxctx.action_class("self")
class LinuxActions:
    def edit_text_file(path):
        # we use xdg-open for this even though it might not open a text
        # editor. we could use $EDITOR, but that might be something that
        # requires a terminal (eg nano, vi).
        open_with_subprocess(path, ["/usr/bin/xdg-open", path])


# Helper for linux and mac.
def open_with_subprocess(path, args):
    """Tries to open a file using the given subprocess arguments."""
    try:
        return subprocess.run(args, timeout=0.5, check=True)
    except subprocess.TimeoutExpired:
        app.notify(f"Timeout trying to open file for editing: {path}")
        raise
    except subprocess.CalledProcessError:
        app.notify(f"Could not open file for editing: {path}")
        raise
