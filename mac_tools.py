import subprocess

def get_apple_note(note_name):
    """Fetches the text of a specific Apple Note natively using macOS AppleScript."""
    print(f"--> Reading: '{note_name}'...")
    script = f'''
    tell application "Notes"
        set targetNote to first note whose name is "{note_name}"
        return body of targetNote
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        clean_text = result.stdout.replace('<div>', '\n').replace('<br>', '\n').replace('</div>', '')
        return clean_text.strip()
    except subprocess.CalledProcessError:
        return f"Error: Could not find '{note_name}'."

def get_all_note_names():
    """Fetches the titles of all Apple Notes on the machine."""
    print("--> Scanning system for all Apple Notes...")
    script = '''
    tell application "Notes"
        set nameList to name of every note
        set AppleScript's text item delimiters to "|||"
        set nameString to nameList as string
        set AppleScript's text item delimiters to ""
        return nameString
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        return [name.strip() for name in result.stdout.split('|||') if name.strip()]
    except subprocess.CalledProcessError:
        print("Error: Could not access Apple Notes list.")
        return []