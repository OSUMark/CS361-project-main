# Mark Brugger
# CS 361
# Spring 2026
# County Project - Monolith for Sprint 1

from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional


# Canonical full names for display
USPS_CODE_TO_STATE_NAME: Dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}

STATE_TOTALS: Dict[str, int] = {
    "AL": 67, "AK": 29, "AZ": 15, "AR": 75, "CA": 58, "CO": 64, "CT": 8,
    "DE": 3, "FL": 67, "GA": 159, "HI": 5, "ID": 44, "IL": 102, "IN": 92,
    "IA": 99, "KS": 105, "KY": 120, "LA": 64, "ME": 16, "MD": 24, "MA": 14,
    "MI": 83, "MN": 87, "MS": 82, "MO": 115, "MT": 56, "NE": 93, "NV": 17,
    "NH": 10, "NJ": 21, "NM": 33, "NY": 62, "NC": 100, "ND": 53, "OH": 88,
    "OK": 77, "OR": 36, "PA": 67, "RI": 5, "SC": 46, "SD": 66, "TN": 95,
    "TX": 254, "UT": 29, "VT": 14, "VA": 133, "WA": 39, "WV": 55,
    "WI": 72, "WY": 23, "DC": 1,
}

USA_TOTAL = sum(STATE_TOTALS.values())  # expected 3,143 (50 states + DC)


STATE_NAME_TO_CODE: Dict[str, str] = {
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

    # Full names to 2-letter codes
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
    """This function takes a state (two letter code or full name) as input
    and returns the two letter state code as output."""
    if not isinstance(s, str):
        raise ValueError("State must be a string.")

    # Normalize spaces and punctuation for matching
    cleaned = " ".join(s.replace(".", " ").replace(",", " ").split()).upper()

    if len(cleaned) == 2 and cleaned.isalpha():
        code = STATE_NAME_TO_CODE.get(cleaned)
        if code:
            return code

    code = STATE_NAME_TO_CODE.get(cleaned)
    if code:
        return code

    raise ValueError(
        f"The state: {s!r} was not recognized. "
        "\nPlease use the two letter code (e.g., OK) "
        "\nor full name (e.g., Oklahoma).\n"
        )


def normalize_county_display(name: str) -> str:
    """This function takes a county name as input and attempts to
    remove extra spaces and give it a consistent capitalization format.
    The fixed name is returned as output.
    """
    if not isinstance(name, str):
        raise ValueError("County must be a string.")
    return " ".join(name.split()).title()


def normalize_date_format(date_str: str) -> str:
    """Return date as MM/DD/YY with leading zeros (e.g., 03/05/17)."""

    dt = datetime.strptime(date_str, "%m/%d/%y")
    return dt.strftime("%m/%d/%y")


class VisitStore:
    """Store county visits in a JSON file at the given path.

    - Accepts state as two letter code or full name, stores as two letter code.
    - County/state duplicates are rejected (case-insensitive county).
    - File is created on first use; corrupted JSON is backed up.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    def ensure_file(self) -> None:
        """Create the JSON file if it doesn't already exist."""
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

    def load(self) -> List[dict]:
        """Load visits as a list. If corrupted, back it up and start fresh."""
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            backup = self.path.with_suffix(self.path.suffix + ".bak")
            try:
                self.path.replace(backup)
            except Exception:
                pass
            self.path.write_text("[]\n", encoding="utf-8")
            return []

    def save(self, visits: List[dict]) -> None:
        """Save list of visits back to the file."""
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(visits, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        tmp.replace(self.path)

    def list_visits(self) -> List[dict]:
        """Return all stored visits."""
        return self.load()

    def add_visit(
        self,
        county: str,
        state: str,          # can be two letter or full name
        date: str,
        note: Optional[str] = None,
    ) -> None:
        """Append a new visit if (county, state) not already present."""
        visits = self.load()

        # Normalize inputs
        county_norm = normalize_county_display(county)
        state_code = normalize_state_to_code(state)
        date_clean = normalize_date_format(date)

        note_clean = None
        if isinstance(note, str) and note.strip():
            note_clean = note.strip()

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
                f"in state '{state_code}' already exists.\n"
            )

        visits.append(
            {
                "county": county_norm,
                "state": state_code,
                "date": date_clean,
                "note": note_clean,
            }
        )
        self.save(visits)


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
    input from the user. It returns the user's choice."""

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

    while True:

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
                    "\nYou have input an invalid date or did not use the "
                    "MM/DD/YY format.\n"
                )

        opt_note = input("(Optional) You can add a note about this visit: ")

        print("You entered:\n")
        print("County: ", county_name)
        print("State: ", county_state)
        print("Date: ", date_visit)
        print("Note: ", opt_note)

        print("\nIs this information correct?")
        print("1. Yes, save it")
        print("2. No, re-enter the information\n")
        confirmation = input("My selection: ")

        if confirmation == "1":
            try:
                store.add_visit(
                    county=county_name,
                    state=county_state,
                    date=date_visit,
                    note=opt_note or None
                )
                print("\nThank you, your county visit has been recorded.")
                print("Now we will return you to the main menu.\n")
                return True
            except ValueError as exc:
                print(f"\nThis visit was not saved because:\n{exc}")
                return False

        elif confirmation != "2":
            print(
                "\nYou have entered an invalid option. "
                "Please select 1 or 2.\n"
            )

        date_validation = False


def count_visited_by_state(usps_code: str) -> int:
    """Return the number of unique (county, state)
    visits stored for the state."""
    visits = store.list_visits()
    code = usps_code.upper()
    return sum(1 for v in visits if str(v.get("state", "")).upper() == code)


def percent(n: int, d: int) -> int:
    """Round to nearest integer percent (e.g., 22/64 -> 34%)."""
    if d <= 0:
        return 0
    return round((n / d) * 100)


def press_any_key():
    input("\nPress Enter to return to the View Statistics Menu...")


def show_state_statistics():
    print("\n-------------------------------------")
    print(" County Tracker View Statistics Menu")
    print("-------------------------------------")
    print("\nYou have selected to look up statistics for a specific state.")
    print("Please enter the state below.  It is acceptable to use the")
    print("full name or its postal abbreviation (e.g. Montana or MT")
    print("are both acceptable inputs).\n")

    while True:
        user_state = input("Please input your state: ").strip()

        try:
            code = normalize_state_to_code(user_state)
        except ValueError as exc:
            print(f"\n{exc}")
            continue

        total = STATE_TOTALS.get(code)

        visited = count_visited_by_state(code)
        name = USPS_CODE_TO_STATE_NAME.get(code, code)
        pct = percent(visited, total)

        print(f"\n\nFor your selected state of {name}:\n")
        print(f"There are {total} counties in the state.")
        print(f"You have visited {visited} of them.")
        print(f"{name} is {pct}% finished.")

        press_any_key()
        return


def _show_usa_statistics():
    print("\n-------------------------------------")
    print(" County Tracker View Statistics Menu")
    print("-------------------------------------")
    print("\nYou have selected to look up statistics for the entire USA.\n")

    visits = store.list_visits()
    visited_usa = sum(
        1 for v in visits
        if str(v.get("state", "")).upper() in STATE_TOTALS
    )
    total_usa = USA_TOTAL
    pct = percent(visited_usa, total_usa)

    print("For the United States of America:\n")
    print(f"There are {total_usa} counties in the country.")
    print(f"You have visited {visited_usa} of them.")
    print(f"The USA is {pct}% finished.")

    press_any_key()


def view_statistics_menu():
    """Interactive statistics menu loop (state, USA, return)."""

    print("You have the ability to look up statistics for an individual")
    print("state or the entire country. The program will display the")
    print("number of counties that have been visited in the state or")
    print("country and the total number of counties in that location.")
    print("Then it will display the percentage that has been completed.\n")

    while True:
        print("\n-------------------------------------")
        print(" County Tracker View Statistics Menu")
        print("-------------------------------------")
        print("1. Display Statistics for a state")
        print("2. Display Statistics for the USA")
        print("3. Return to Main Menu\n")

        selection = input("Please enter your selection: ").strip()
        if selection == "1":
            show_state_statistics()
        elif selection == "2":
            _show_usa_statistics()
        elif selection == "3":
            return
        else:
            print("\nYou have entered an invalid choice.")
            print("Please enter 1-3 as your input.\n")


store = VisitStore(Path("county_visits.json"))
store.ensure_file()


def main():
    print("Welcome to Mark's County Tracker!\n")
    print("This tool will allow you to keep track of your visits to")
    print("counties/parishes/boroughs in the United States. More than")
    print("just a list of counties, this program will generate helpful")
    print("information on what is left to explore, as well as statistics")
    print("based on state and county. Come inside and we will have fun")
    print("with this unique hobby!\n")

    input("Press any key to continue...\n")

    while True:
        choice = main_menu()
        if choice == "1":
            log_visit()
        elif choice == "2":
            view_statistics_menu()
        else:
            print("\nThank you for exploring the County Tracker.")
            print("Please come again when you have more time!")
            break


if __name__ == "__main__":
    main()
