# Mark Brugger
# CS 361
# Spring 2026
# County Project - Monolith for Sprint 1

def main_menu():
    """This function prints the main menu of the program and solicits
    input from the user. The function returns the choice to the user"""

    menu_choice = 0

    while menu_choice != 3:

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


main_select = main_menu()
print("The user selected", main_select)
