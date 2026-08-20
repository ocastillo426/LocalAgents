import subprocess
import requests
import os
from ics import Calendar


def get_ai_folder_notes(folder_name="AI Notes"):
    """Fetches all notes and their contents from a specific Apple Notes folder in one fast pass."""
    print(f"--> Scanning Apple Notes folder: '{folder_name}'...")

    # AppleScript that grabs both title and body for every note in the target folder
    script = f'''
    tell application "Notes"
        if not (exists folder "{folder_name}") then
            return "ERROR:FOLDER_NOT_FOUND"
        end if

        set output to ""
        tell folder "{folder_name}"
            repeat with n in notes
                set noteTitle to name of n
                set noteBody to body of n
                set output to output & noteTitle & ":::SPLIT_CONTENT:::" & noteBody & ":::SPLIT_NOTE:::"
            end repeat
        end tell
        return output
    end tell
    '''

    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        raw_output = result.stdout.strip()

        if raw_output == "ERROR:FOLDER_NOT_FOUND":
            print(f"[!] Warning: Folder '{folder_name}' not found in Apple Notes.")
            return []

        if not raw_output:
            print(f"--> Folder '{folder_name}' is empty.")
            return []

        notes = []
        raw_notes = raw_output.split(":::SPLIT_NOTE:::")
        for entry in raw_notes:
            if ":::SPLIT_CONTENT:::" in entry:
                title, body = entry.split(":::SPLIT_CONTENT:::", 1)
                # Clean up HTML tags from Apple Notes
                clean_body = body.replace('<div>', '\n').replace('<br>', '\n').replace('</div>', '').strip()
                notes.append({"title": title.strip(), "content": clean_body})

        return notes

    except subprocess.CalledProcessError as e:
        print(f"Error accessing Apple Notes: {e}")
        return []


def get_apple_calendar_events(calendar_name="7shifts", days_ahead=14):
    """Fetches upcoming events directly from macOS Calendar."""
    print(f"--> Fetching upcoming events from Calendar: '{calendar_name}'...")

    # AppleScript to pull the next 14 days of events from a specific calendar
    script = f'''
    set startDate to (current date)
    set endDate to startDate + ({days_ahead} * days)
    set output to "Upcoming Schedule for {calendar_name}:\\n"

    tell application "Calendar"
        if not (exists calendar "{calendar_name}") then
            return "Error: Calendar '{calendar_name}' not found."
        end if

        -- Grab events within our time window
        set theEvents to (every event of calendar "{calendar_name}" whose start date ≥ startDate and start date ≤ endDate)

        if (count of theEvents) is 0 then
            return "No upcoming events scheduled."
        end if

        -- Format them cleanly for the LLM
        repeat with e in theEvents
            set output to output & "- " & (summary of e) & ": " & (start date of e) & "\\n"
        end repeat
    end tell
    return output
    '''

    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error reading Apple Calendar: {e}"