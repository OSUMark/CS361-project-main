# Mark Brugger
# CS 361
# Spring 2026
# County Project - Monolith for Sprint 1

from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional


_STATE_NAME_TO_CODE: Dict[str, str] = {
    # 2-letter codes (map to themselves)
    "AL": "AL", "AK": "AK", "AZ": "AZ", "AR": "AR", "CA": "CA",
    "CO": "CO", "CT": "CT", "DE": "DE", "FL": "FL", "GA": "GA",
    "HI": "HI", "ID": "ID", "IL": "IL", "IN": "IN", "IA": "IA",
    "KS": "KS", "KY": "KY", "LA": "LA", "ME": "ME", "MD": "MD",
    "MA": "MA", "MI": "MI", "MN": "MN", "MS": "MS", "MO": "MO",
    "MT": "MT", "NE": "NE", "NV": "NV", "NH": "NH", "NJ": "NJ",
    "NM": "NM", "NY": "NY", "NC": "NC", "ND": "ND", "OH": "OH",
    "OK": "OK", "OR": "OR", "PA": "PA", "RI": "RI", "SC": "SC",
    "SD": "SD", "TN": "TN", "TX": "TX", "UT": "UT", "VT": "VT",
    "VA": "VA", "WA": "WA", "WV": "WV", "WI": "WI", "WY": "WY",
    "DC": "DC",


    # Full names -> USPS
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
    "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT",
    "DELAWARE": "DE", "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI",
    "IDAHO": "ID", "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA",
    "KANSAS": "KS", "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME",
    "MARYLAND": "MD", "MASSACHUSETTS": "MA", "MICHIGAN": "MI",
    "MINNESOTA": "MN", "MISSISSIPPI": "MS", "MISSOURI": "MO", "MONTANA": "MT",
    "NEBRASKA": "NE", "NEVADA": "NV", "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
    "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH",
    "OKLAHOMA": "OK", "OREGON": "OR", "PENNSYLVANIA": "PA",
    "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC", "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT", "VERMONT": "VT",
    "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY", "DISTRICT OF COLUMBIA": "DC",
    "WASHINGTON DC": "DC", "WASHINGTON, DC": "DC", "D.C.": "DC", "DC.": "DC",
}


def normalize_state_to_code(s: str) -> str:
    """Accept USPS code or full name (any case/punctuation)
    and return USPS 2-letter code."""
    if not isinstance(s, str):
        raise ValueError("State must be a string.")

    # Normalize spaces and punctuation for matching
    cleaned = " ".join(s.replace(".", " ").replace(",", " ").split()).upper()

    if len(cleaned) == 2 and cleaned.isalpha():
        code = _STATE_NAME_TO_CODE.get(cleaned)
        if code:
            return code

    # Try full-name mapping (includes some D.C. variants)
    code = _STATE_NAME_TO_CODE.get(cleaned)
    if code:
        return code

    raise ValueError(
        f"Unrecognized state: {s!r}. "
        "Use USPS code (e.g., OH) or full name (e.g., Ohio).")


def normalize_county_display(name: str) -> str:
    """Basic normalization for county display: trim + Title Case.

    Avoids assumptions like stripping 'County' suffix—users sometimes include
    borough/parish equivalents. Adjust if you want stronger rules.
    """
    if not isinstance(name, str):
        raise ValueError("County must be a string.")
    return " ".join(name.split()).title()


def normalize_date_format(date_str: str) -> str:
    """Return date as MM/DD/YY with leading zeros (e.g., 03/05/17)."""

    dt = datetime.strptime(date_str, "%m/%d/%y")
    return dt.strftime("%m/%d/%y")


class VisitStore:
    """Store county visits in a JSON list at the given path.

    - Accepts state as USPS code or full name, stores USPS code.
    - County/state duplicates are rejected (case-insensitive county).
    - File is created on first use; corrupted JSON is backed up.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    # ---------- file handling ----------

    def ensure_file(self) -> None:
        """Create the JSON file if it doesn't already exist."""
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

    def _load(self) -> List[dict]:
        """Load visits as a list. If corrupted, back it up and start fresh."""
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            # Backup the bad file, then reset
            backup = self.path.with_suffix(self.path.suffix + ".bak")
            try:
                self.path.replace(backup)
            except Exception:
                pass
            self.path.write_text("[]\n", encoding="utf-8")
            return []

    def _save(self, visits: List[dict]) -> None:
        """Save list of visits back to the file."""
        # Simple atomic-ish write via temp file and replace
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(visits, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        tmp.replace(self.path)

    # ---------- public API ----------

    def list_visits(self) -> List[dict]:
        """Return all stored visits."""
        return self._load()

    def add_visit(
        self,
        county: str,
        state: str,          # can be USPS code or full name
        date: str,           # already validated before call
        note: Optional[str] = None,
    ) -> None:
        """Append a new visit if (county, state) not already present."""
        visits = self._load()

        # Normalize inputs
        county_norm = normalize_county_display(county)
        state_code = normalize_state_to_code(state)
        date_clean = normalize_date_format(date)

        note_clean = None
        if isinstance(note, str) and note.strip():
            note_clean = note.strip()

        # Build duplicate index based on (county, state_code)
        existing_keys = {
            (normalize_county_display(v.get("county", "")).casefold(),
             str(v.get("state", "")).upper())
            for v in visits
            if isinstance(v, dict)
        }
        new_key = (county_norm.casefold(), state_code)

        if new_key in existing_keys:
            raise ValueError(
                f"A visit for county '{county_norm}' "
                "in state '{state_code}' already exists."
            )

        visits.append(
            {
                "county": county_norm,   # stored in Title Case
                "state": state_code,     # stored as USPS code
                "date": date_clean,
                "note": note_clean,
            }
        )
        self._save(visits)


def validate_date(input):
    """This function takes a string as input and validates whether it
    is in a date format and whether the date exists (e.g. March 35th is
    not allowed), returning a boolean.
    Input: String, hopefully a date
    Output: True or False"""
    try:
        datetime.strptime(input, "%m/%d/%y")
        return True
    except ValueError:
        return False


def main_menu():
    """This function prints the main menu of the program and solicits
    input from the user. The function returns the choice to the user"""

    while True:

        print("-------------------------------------")
        print("      County Tracker MAIN MENU")
        print("-------------------------------------")
        print("\n1. Log a Visit")
        print("2. View Statistics")
        print("3. Exit")
        print("\nHere you can choose to record a new visit to a county or")
        print("view statistics about all of the visits that have been made.")
        print("If you are done using this tool, you can input 3 to exit")
        print("the program.")

        menu_choice = input("\nPlease enter your selection: ")

        if menu_choice == "1" or menu_choice == "2" or menu_choice == "3":
            return menu_choice

        print("\nYou have entered an invalid choice.")
        print("Please enter 1-3 as your input.\n")


def log_visit():
    """This function allows the user to add a county visit to the
    logs.  Function takes no input and returns a success code"""

    date_validation = False

    print("\n--------------------------------------")
    print("    County Tracker Log a New Visit")
    print("--------------------------------------")
    print("\nNow we are going to record a new visit to a county (or parish,")
    print("or borough depending on the state) you haven't visited before.")
    print("The tool will record the name of the county, the state it resides,")
    print("and when you visited. As an optional item, you may add a note")
    print("about the visit. If you do not wish to add a note, simply press")
    print("the enter key when you get to that input.\n")

    county_name = input("Please input the county name: ")
    county_state = input("Please provide the county's state: ")

    while date_validation is False:
        date_visit = input(
            "Please enter the date of your visit (using the "
            "format MM/DD/YY): "
        )
        date_validation = validate_date(date_visit)
        if date_validation is False:
            print(
                "You have input an invalid date or did not use the "
                "MM/DD/YY format."
            )

    opt_note = input("(Optional) You can add a note about this visit: ")

    try:
        store.add_visit(
            county=county_name,
            state=county_state,
            date=date_visit,
            note=opt_note or None
        )
        print("Your visit was saved.")
        return True
    except ValueError as exc:
        print(f"Not saved: {exc}")
        return False


def view_visits():
    """List all saved visits in a readable way."""
    visits = store.list_visits()
    if not visits:
        print("\nNo visits have been recorded yet.\n")
        return

    print("\n----------------------------------------")
    print(" Your Recorded County Visits")
    print("----------------------------------------")
    for i, v in enumerate(visits, start=1):
        county = v.get("county", "")
        state = v.get("state", "")
        date = v.get("date", "")
        note = v.get("note", "")
        line = f"{i}. {county}, {state} on {date}"
        if note:
            line += f" — {note}"
        print(line)
    print()  # trailing newline


store = VisitStore(Path("county_visits.json"))
store.ensure_file()


def main():
    """Top-level program loop."""
    while True:
        choice = main_menu()
        if choice == "1":
            # Log a visit (uses your existing prompts and date validation)
            log_visit()
        elif choice == "2":
            # View visits / basic stats placeholder
            view_visits()
        else:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
