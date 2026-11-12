from drafter import *
from dataclasses import dataclass
from datetime import date
from typing import Any  # ADVANCED: type hint only (see documentation block, item 2)
import matplotlib.pyplot as plt  # ADVANCED: draws the progression graph (see item 1)


# =========================================================
# DOCUMENTATION OF ADVANCED TECHNIQUES
# =========================================================
# The techniques below go beyond what was covered in the course.
# Each one is summarized here and explained again in a comment
# right where it is used in the code.
#
#
# 1. typing.Any and list[Any]
#    "Any" is a type hint meaning "any type of value is allowed."
#    It is used for lists that mix strings and Drafter components
#    (Header, TextBox, Button, ...) because no single type describes
#    all of them. Type hints do not change how the code runs.
#
# 2. Union type hint: Exercise | None
#    The "|" means "or." find_exercise returns an Exercise if one is
#    found, or None if it is not, so its return type is
#    "Exercise or None." Callers check "is None" before using it.
#
# 3. try / except (in save_workout)
#    Code inside "try" runs normally. If it causes one of the listed
#    errors, Python jumps to the "except" block instead of crashing
#    the website. It is used to safely convert the "sets" dropdown
#    text (like "3") into an integer.
#
# 4. List comprehensions and star-unpacking (*)
#    - A list comprehension builds a list in a single expression:
#      [expression for item in sequence]. progress_graph uses one to
#      build one line of text per logged workout.
#    - A * in front of a list, inside another list or a function call,
#      "unpacks" it so its items are placed individually instead of
#      nested as one list. It is used in progress_graph (each workout
#      line becomes its own item of the page content) and in
#      log_workout (Div(*make_rep_fields(3)) passes each rep field to
#      Div as a separate argument).
#
# 5. Fragments, on_change, and Div(id=...) (live updates)
#    Normally clicking a Button loads a whole new Page. A Fragment
#    replaces only one part of the current page. The "sets" SelectBox
#    has on_change="update_rep_fields", so choosing a new number of
#    sets automatically calls that route. The route returns a Fragment
#    whose target="#rep_fields" matches the id given to the Div in
#    log_workout, so only the rep boxes are swapped out.
#
# 6. Custom CSS (DARK_THEME_CSS, LIGHT_THEME_CSS, and css=)
#    CSS is the language that controls colors and styling on web
#    pages. The two theme strings hold CSS rules, and the css=
#    argument of Page/Fragment applies them. "!important" makes a
#    rule override Drafter's default styling.
#
# 7. Dates (from datetime import date)
#    date.today() returns today's date. It is converted to text with
#    str() so each WorkoutEntry remembers when it was logged.
#
# 8. Extra TextBox options and default parameter values
#    TextBox(..., "number", min=1, step=1, required=True) is the same
#    TextBox with extra keyword arguments that make the browser
#    only accept numbers, enforce a minimum, and require a value.
#    In save_workout, "reps_1: int = 0" gives a parameter a default
#    value, used if the browser does not send that field (for example
#    when fewer than 5 sets are selected).


# =========================================================
# CONSTANTS
# =========================================================

MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Arms",
    "Legs", "Core", "Other"
]

SET_OPTIONS = ["1", "2", "3", "4", "5"]


# =========================================================
# WEBSITE THEMES
# =========================================================

# ADVANCED TECHNIQUE (custom CSS): these multi-line strings contain CSS
# rules that restyle the page (background, text, inputs, buttons).
# The matching theme is applied through the css= argument in make_page.
DARK_THEME_CSS = """
html, body {
    background-color: #121826 !important;
    color: #f8fafc !important;
    min-height: 100%;
}

body, body * {
    color: #f8fafc !important;
}

body p, body span, body div, body label,
body h1, body h2, body h3, body li,
body td, body th {
    color: #f8fafc !important;
}

input, select, textarea {
    background-color: #263449 !important;
    color: #ffffff !important;
    border: 1px solid #64748b !important;
}

input::placeholder {
    color: #cbd5e1 !important;
}

button {
    background-color: #334155 !important;
    color: #ffffff !important;
    border: 1px solid #64748b !important;
    border-radius: 6px;
    padding: 8px 14px;
}

a {
    color: #93c5fd !important;
}

hr {
    border-color: #64748b !important;
}
"""


LIGHT_THEME_CSS = """
html, body {
    background-color: #ffffff !important;
    color: #222222 !important;
    min-height: 100%;
}

body, body * {
    color: #222222 !important;
}

input, select, textarea {
    background-color: #ffffff !important;
    color: #222222 !important;
    border: 1px solid #cccccc !important;
}

button {
    background-color: #eeeeee !important;
    color: #222222 !important;
    border: 1px solid #cccccc !important;
    border-radius: 6px;
    padding: 8px 14px;
}

a {
    color: #2255aa !important;
}
"""


# =========================================================
# DATACLASSES
# =========================================================

@dataclass
class Exercise:
    """
    Stores the basic information about an exercise.

    name: Exercise name.
    muscle_group: Muscle group targeted by the exercise.
    """
    name: str
    muscle_group: str


@dataclass
class WorkoutEntry:
    """
    Stores one completed workout session.

    exercise_name: Name of the exercise performed.
    weight: Weight lifted during the workout.
    reps: List of reps completed in each set.
    workout_date: Date of the workout.
    """
    exercise_name: str
    weight: float
    reps: list[int]
    workout_date: str


@dataclass
class State:
    """
    Stores all information used throughout the website.

    exercises: Available exercises.
    history: Previously logged workouts.
    streak: Total number of logged workouts.
    filter: Current muscle group filter.
    dark_theme: Whether dark mode is enabled.
    selected_exercise: Currently selected exercise.
    message: Feedback displayed to the user.
    """
    exercises: list[Exercise]
    history: list[WorkoutEntry]
    streak: int
    filter: str
    dark_theme: bool
    selected_exercise: str
    message: str


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def get_theme_css(state: State) -> str:
    """Return the CSS that matches the user's selected theme."""
    if state.dark_theme:
        return DARK_THEME_CSS
    else:
        return LIGHT_THEME_CSS


def make_page(state: State, content: list[Any]) -> Page:
    """
    Creates a page using the user's selected theme.

    All website routes use this function to keep the
    appearance consistent throughout navigation.
    """

    if state.dark_theme:
        # ADVANCED TECHNIQUE (css= argument): applies the theme's CSS
        # string to the whole page.
        return Page(state, content, css=DARK_THEME_CSS)

    else:
        return Page(state, content, css=LIGHT_THEME_CSS)


# ADVANCED TECHNIQUE (union type hint): "Exercise | None" means this
# function returns either an Exercise or None. Callers must check
# "is None" before using the result.
def find_exercise(state: State, name: str) -> Exercise | None:
    """
    Searches for an exercise by name.

    Returns the Exercise object if found.
    Returns None if the exercise does not exist.
    """

    for exercise in state.exercises:

        if exercise.name == name:
            return exercise

    return None


def get_exercise_names(state: State) -> list[str]:
    """
    Creates a list of exercise names for dropdown menus.
    """

    names: list[str] = []

    for exercise in state.exercises:
        names.append(exercise.name)

    return names


def get_max_weight(state: State, exercise_name: str) -> float:
    """
    Finds the highest weight ever recorded for an exercise.

    Iterates through workout history and compares the
    weights of matching exercises.
    """

    maximum = 0.0

    for entry in state.history:

        if entry.exercise_name == exercise_name:

            if entry.weight > maximum:
                maximum = entry.weight

    return maximum


def get_exercise_history(state: State, exercise_name: str) -> list[WorkoutEntry]:
    """
    Returns all workout entries for a selected exercise.
    """

    matching_entries: list[WorkoutEntry] = []

    for entry in state.history:

        if entry.exercise_name == exercise_name:
            matching_entries.append(entry)

    return matching_entries


def get_reps_description(reps: list[int]) -> str:
    """
    Converts a list of reps into readable text.

    Example: [10, 8, 8] becomes '10, 8, 8'.
    """

    description = ""

    for index in range(len(reps)):

        description += str(reps[index])

        if index < len(reps) - 1:
            description += ", "

    return description


# ADVANCED TECHNIQUE (list[Any]): the list mixes strings, Headers, and
# TextBoxes, so "Any" is used as a type hint for "any kind of value."
def make_rep_fields(number_of_sets: int) -> list[Any]:
    """
    Dynamically creates rep textboxes.

    Selecting 2 sets creates 2 textboxes.
    Selecting 5 sets creates 5 textboxes.

    The minimum allowed value is 1 rep.
    """

    content: list[Any] = [
        Header("Reps Completed in Each Set", level=2)
    ]

    for set_number in range(1, number_of_sets + 1):

        content.append("Set " + str(set_number) + ":")

        content.append(
            TextBox(
                "reps_" + str(set_number),
                0,
                "number",
                min=1,
                step=1,
                required=True
            )
        )

    return content


# =========================================================
# ROUTE 1: MAIN MENU
# =========================================================

@route
def index(state: State) -> Page:
    """
    Displays the main menu and workout statistics.
    """

    return make_page(state, [

        Header("WORKOUT TRACKER"),

        "Track your workouts and monitor your progress!",

        HorizontalRule(),

        Header("Your Statistics", level=2),

        "Total workout entries: " + str(state.streak),

        "Exercises created: " + str(len(state.exercises)),

        HorizontalRule(),

        Header("Navigation", level=2),

        Button("Edit Exercises", "view_exercises"),

        Button("Log a Workout", "log_workout"),

        Button("View Progression", "view_progression"),

        Button("Settings", "settings_page"),

        HorizontalRule(),

        state.message
    ])


# =========================================================
# ROUTE 2: VIEW EXERCISES
# =========================================================

@route
def view_exercises(state: State) -> Page:
    """
    Displays the user's saved exercises.
    """

    content: list[Any] = [

        Header("EDIT EXERCISES"),

        "Manage your exercise list below.",

        HorizontalRule()
    ]

    if len(state.exercises) == 0:

        content.append("You have not created any exercises yet.")

    else:

        for exercise in state.exercises:

            content.append(
                exercise.name + " - " + exercise.muscle_group
            )

    content.extend([

        HorizontalRule(),

        Button("Add Exercise", "add_exercise"),

        Button("Edit Exercise", "edit_exercise"),

        Button("Remove Exercise", "remove_exercise"),

        Button("Back to Main Menu", "index"),

        state.message
    ])

    return make_page(state, content)


# =========================================================
# ROUTE 3: ADD EXERCISE
# =========================================================

@route
def add_exercise(state: State) -> Page:
    """
    Displays the form for creating a new exercise.
    """

    return make_page(state, [

        Header("ADD AN EXERCISE"),

        "Exercise Name:",

        TextBox("exercise_name"),

        "Muscle Group:",

        SelectBox("muscle_group", MUSCLE_GROUPS),

        Button("Create Exercise", "save_exercise"),

        Button("Back", "view_exercises")
    ])


@route
def save_exercise(state: State,
                  exercise_name: str,
                  muscle_group: str) -> Page:
    """
    Creates a new exercise after validating its name.
    """

    exercise_name = exercise_name.strip()

    if exercise_name == "":

        state.message = "Error: Exercise name cannot be blank."

    elif find_exercise(state, exercise_name) is not None:

        state.message = "Error: This exercise already exists."

    else:

        state.exercises.append(
            Exercise(exercise_name, muscle_group)
        )

        state.message = exercise_name + " was successfully added!"

    return view_exercises(state)


# =========================================================
# ROUTE 4: EDIT EXERCISE
# =========================================================

@route
def edit_exercise(state: State) -> Page:
    """
    Displays a form for modifying an existing exercise.
    """

    if len(state.exercises) == 0:

        state.message = "Create an exercise before editing."

        return view_exercises(state)

    return make_page(state, [

        Header("EDIT AN EXERCISE"),

        "Choose the exercise:",

        SelectBox("old_name", get_exercise_names(state)),

        "Enter the new exercise name:",

        TextBox("new_name"),

        "Select the muscle group:",

        SelectBox("new_group", MUSCLE_GROUPS),

        Button("Save Changes", "save_edit"),

        Button("Back", "view_exercises")
    ])


@route
def save_edit(state: State,
              old_name: str,
              new_name: str,
              new_group: str) -> Page:
    """
    Updates an exercise's name and muscle group.

    Historical entries are also updated so the user
    does not lose their previous workout progression.
    """

    new_name = new_name.strip()

    exercise = find_exercise(state, old_name)

    if new_name == "":

        state.message = "Error: Exercise name cannot be blank."

    elif new_name != old_name and find_exercise(state, new_name):

        state.message = "Error: That exercise name is already in use."

    elif exercise is None:

        state.message = "Error: Exercise could not be found."

    else:

        exercise.name = new_name

        exercise.muscle_group = new_group

        for entry in state.history:

            if entry.exercise_name == old_name:
                entry.exercise_name = new_name

        state.message = "Exercise successfully updated!"

    return view_exercises(state)


# =========================================================
# ROUTE 5: REMOVE EXERCISE
# =========================================================

@route
def remove_exercise(state: State) -> Page:
    """
    Displays a dropdown for selecting an exercise to remove.
    """

    if len(state.exercises) == 0:

        state.message = "There are no exercises to remove."

        return view_exercises(state)

    return make_page(state, [

        Header("REMOVE AN EXERCISE"),

        "Select the exercise you want to delete:",

        SelectBox("exercise_name", get_exercise_names(state)),

        Button("Remove Selected Exercise", "confirm_remove"),

        Button("Back", "view_exercises")
    ])


@route
def confirm_remove(state: State,
                   exercise_name: str) -> Page:
    """
    Removes an exercise and its corresponding workout history.
    """

    exercise = find_exercise(state, exercise_name)

    if exercise is None:

        state.message = "Exercise could not be found."

    else:

        state.exercises.remove(exercise)

        remaining_history: list[WorkoutEntry] = []

        for entry in state.history:

            if entry.exercise_name != exercise_name:
                remaining_history.append(entry)

        state.history = remaining_history

        state.message = exercise_name + " was removed."

    return view_exercises(state)


# =========================================================
# ROUTE 6: LOG WORKOUT
# =========================================================

@route
def log_workout(state: State) -> Page:
    """
    Displays the workout logging form.

    Users choose an exercise, enter weight, select sets,
    and enter the reps completed in each set.
    """

    if len(state.exercises) == 0:

        state.message = "Create an exercise before logging workouts."

        return view_exercises(state)

    return make_page(state, [

        Header("LOG A WORKOUT"),

        "Choose an exercise:",

        SelectBox(
            "exercise_name",
            get_exercise_names(state)
        ),

        HorizontalRule(),

        "Weight lifted (lbs):",

        TextBox(
            "weight",
            0.0,
            "number",
            min=0,
            step=0.5,
            required=True
        ),

        "Number of sets:",

        SelectBox(
            "sets",
            SET_OPTIONS,
            "3",
            # ADVANCED TECHNIQUE (live update): on_change calls the
            # update_rep_fields route whenever the selection changes,
            # without reloading the whole page.
            on_change="update_rep_fields"
        ),

        # ADVANCED TECHNIQUE (Div id + star-unpacking): the * unpacks the
        # list returned by make_rep_fields so each item becomes its own
        # argument to Div. The id lets the Fragment in update_rep_fields
        # find this Div (target="#rep_fields") and replace its contents.
        Div(
            *make_rep_fields(3),
            id="rep_fields"
        ),

        HorizontalRule(),

        # Display validation messages here.
        state.message,

        Button("Save Workout", "save_workout"),

        Button("Back to Main Menu", "index")
    ])


# =========================================================
# ROUTE 7: UPDATE REP TEXTBOXES
# =========================================================

@route
def update_rep_fields(state: State, sets: str) -> Fragment:
    """Update the number of rep input boxes when the set count changes."""

    number_of_sets = int(sets)

    # ADVANCED TECHNIQUE (Fragment): instead of a whole new Page, this
    # returns only the new rep boxes. target="#rep_fields" tells Drafter
    # to replace the Div with id="rep_fields" on the log_workout page.
    # css= keeps the current theme applied to the new boxes.
    return Fragment(
        state,
        make_rep_fields(number_of_sets),
        target="#rep_fields",
        css=get_theme_css(state)
    )


# =========================================================
# ROUTE 8: SAVE WORKOUT
# =========================================================

@route
def save_workout(state: State,
                 exercise_name: str,
                 weight: float,
                 sets: str,
                 reps_1: int = 0,
                 reps_2: int = 0,
                 reps_3: int = 0,
                 reps_4: int = 0,
                 reps_5: int = 0) -> Page:
    """
    Validates and saves a completed workout.

    IMPORTANT:
    HTML minimum values are not sufficient by themselves.
    This route independently checks all submitted values
    before adding anything to workout history.
    """

    # Validate exercise selection.
    if find_exercise(state, exercise_name) is None:

        state.message = "Error: Invalid exercise selection."

        return log_workout(state)

    # Validate weight.
    if weight < 0:

        state.message = (
            "Error: Negative weights are not allowed. "
            "Enter zero or a positive number."
        )

        return log_workout(state)

    # Convert the dropdown selection into an integer.
    # ADVANCED TECHNIQUE (try / except): the code under "try" runs
    # normally. If int() fails with a ValueError or TypeError, Python
    # skips to the "except" block below instead of crashing the site.
    try:

        number_of_sets = int(sets)

    except (ValueError, TypeError):

        state.message = "Error: Invalid number of sets."

        return log_workout(state)

    # Validate number of sets.
    if number_of_sets < 1 or number_of_sets > 5:

        state.message = "Error: Select between 1 and 5 sets."

        return log_workout(state)

    # Store the rep inputs.
    all_reps: list[int] = [
        reps_1,
        reps_2,
        reps_3,
        reps_4,
        reps_5
    ]

    # Only save reps corresponding to selected sets.
    selected_reps: list[int] = []

    for index_number in range(number_of_sets):

        selected_reps.append(all_reps[index_number])

    # Validate every selected rep input.
    for rep_count in selected_reps:

        if rep_count < 1:

            state.message = (
                "Error: Reps must be at least 1 "
                "for every selected set."
            )

            return log_workout(state)

    # Check previous personal record.
    previous_max = get_max_weight(
        state,
        exercise_name
    )

    # Create a new workout entry.
    new_entry = WorkoutEntry(
        exercise_name,
        weight,
        selected_reps,
        # ADVANCED TECHNIQUE (datetime): date.today() gets today's date;
        # str() turns it into text such as "2026-11-12".
        str(date.today())
    )

    # Save workout.
    state.history.append(new_entry)

    state.streak += 1

    # Check for a new personal record.
    if weight > previous_max:

        state.message = (
            "NEW PERSONAL RECORD! "
            + exercise_name
            + ": "
            + str(weight)
            + " lbs!"
        )

    else:

        state.message = "Workout successfully logged!"

    return index(state)


# =========================================================
# ROUTE 9: VIEW PROGRESSION
# =========================================================

@route
def view_progression(state: State) -> Page:
    """
    Displays the progression page.
    """

    if len(state.exercises) == 0:

        state.message = "Add an exercise before viewing progression."

        return view_exercises(state)

    return make_page(state, [

        Header("WORKOUT PROGRESSION"),

        "Select an exercise to view its progress:",

        SelectBox(
            "exercise_name",
            get_exercise_names(state)
        ),

        Button(
            "Generate Progress Graph",
            "progress_graph"
        ),

        HorizontalRule(),

        Button("Clear Graph Selection", "clear_graph"),

        Button("Back to Main Menu", "index"),

        state.message
    ])


# =========================================================
# ROUTE 10: GENERATE PROGRESSION GRAPH
# =========================================================

@route
def progress_graph(state: State,
                   exercise_name: str) -> Page:
    """
    Generates a Matplotlib graph showing weight progression.

    X-axis: Workout session.
    Y-axis: Weight lifted in pounds.
    """

    matching_entries = get_exercise_history(
        state,
        exercise_name
    )

    if len(matching_entries) == 0:

        state.message = "No workout history exists for this exercise."

        return make_page(state, [

            Header("WORKOUT PROGRESSION"),

            state.message,

            Button("Choose Another Exercise", "view_progression"),

            Button("Back to Main Menu", "index")
        ])

    # Collect weights and dates.
    weights: list[float] = []

    workout_dates: list[str] = []

    for entry in matching_entries:

        weights.append(entry.weight)

        workout_dates.append(entry.workout_date)

    # Find the maximum weight.
    maximum_weight = get_max_weight(
        state,
        exercise_name
    )

    # Generate graph.
    # ADVANCED TECHNIQUE (matplotlib): plt.figure() starts a blank graph,
    # plt.plot() draws the weights as a line with circle markers, and the
    # remaining plt.* calls add a title, axis labels, grid, and legend.
    plt.figure(figsize=(8, 5))

    plt.plot(
        range(1, len(weights) + 1),
        weights,
        marker="o",
        label="Weight lifted"
    )

    plt.title(exercise_name + " - Weight Progression")

    plt.xlabel("Workout Number")

    plt.ylabel("Weight (lbs)")

    plt.xticks(range(1, len(weights) + 1))

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    return make_page(state, [

        Header("YOUR PROGRESSION"),

        "Exercise: " + exercise_name,

        "Personal Record: " + str(maximum_weight) + " lbs",

        "Total Sessions: " + str(len(matching_entries)),

        # Drafter component that displays the graph drawn above with plt.
        MatPlotLibPlot(),

        Header("Workout History", level=2),

        # ADVANCED TECHNIQUES (list comprehension + star-unpacking):
        # [text for i in range(...)] builds one line of text per workout.
        # The * unpacks that list so each line becomes its own item in
        # this Page's content instead of one nested list.
        *[
            "Workout " + str(i + 1)
            + ": " + workout_dates[i]
            + " | " + str(weights[i]) + " lbs"
            + " | Reps: " + get_reps_description(
                matching_entries[i].reps
            )
            for i in range(len(weights))
        ],

        Button("Choose Another Exercise", "view_progression"),

        Button("Clear Graph", "clear_graph"),

        Button("Back to Main Menu", "index")
    ])


# =========================================================
# ROUTE 11: CLEAR GRAPH
# =========================================================

@route
def clear_graph(state: State) -> Page:
    """
    Clears the current graph selection without deleting history.
    """

    state.selected_exercise = ""

    state.message = "Graph selection cleared."

    return view_progression(state)


# =========================================================
# ROUTE 12: SETTINGS
# =========================================================

@route
def settings_page(state: State) -> Page:
    """
    Displays website settings.

    Users can enable dark mode or clear workout history.
    """

    return make_page(state, [

        Header("SETTINGS"),

        "Dark Theme:",

        CheckBox(
            "dark_theme",
            state.dark_theme
        ),

        Button("Save Settings", "save_settings"),

        HorizontalRule(),

        Header("Workout Data", level=2),

        "Total recorded workouts: " + str(len(state.history)),

        Button("Clear Workout History", "clear_history"),

        Button("Back to Main Menu", "index")
    ])


# =========================================================
# ROUTE 13: SAVE SETTINGS
# =========================================================

@route
def save_settings(state: State,
                  dark_theme: bool) -> Page:
    """
    Saves the user's theme preference.

    All subsequent pages use the updated theme.
    """

    state.dark_theme = dark_theme

    if state.dark_theme:

        state.message = "Dark mode enabled!"

    else:

        state.message = "Light mode enabled!"

    return settings_page(state)


# =========================================================
# ROUTE 14: CLEAR WORKOUT HISTORY
# =========================================================

@route
def clear_history(state: State) -> Page:
    """
    Deletes workout history but preserves the exercise list.
    """

    state.history = []

    state.streak = 0

    state.selected_exercise = ""

    state.message = "All workout history has been cleared."

    return settings_page(state)


# =========================================================
# START WEBSITE
# =========================================================

set_site_information(
    author="Your Name",
    description=(
        "A workout tracker that lets users manage exercises, log workouts, "
        "and view their workout progression over time."
    ),
    sources="Drafter documentation and Matplotlib documentation.",
    planning="",
    links=[]
)


start_server(

    State(
        exercises=[],
        history=[],
        streak=0,
        filter="All",
        dark_theme=False,
        selected_exercise="",
        message="Welcome to your Workout Tracker!"
    ),

    site_title="Workout Tracker"
)
