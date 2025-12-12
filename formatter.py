import json
from prettytable import PrettyTable
from datetime import datetime

def dict_to_table_actual_timetable(json_data):
    """
    Converts the provided JSON data into a table in string format, including day and date information.

    Args:
        json_data (dict): The JSON data to be transformed.

    Returns:
        str: The formatted table as a string.
    """
    table = PrettyTable()
    table.field_names = ["Date", "Day", "Hour", "Begin Time", "End Time", "Group", "Subject", "Teacher", "Room", "Theme"]

    hours = {hour["Id"]: hour for hour in json_data["Hours"]}
    groups = {group["Id"]: group for group in json_data["Groups"]}
    subjects = {subject["Id"]: subject for subject in json_data["Subjects"]}
    teachers = {teacher["Id"]: teacher for teacher in json_data["Teachers"]}
    rooms = {room["Id"]: room for room in json_data["Rooms"]}

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in json_data["Days"]:
        day_name = days_of_week[day["DayOfWeek"] - 1]  # Convert DayOfWeek to day name
        current_date = datetime.fromisoformat(day["Date"]).strftime("%Y-%m-%d")
        for atom in day["Atoms"]:
            hour = hours.get(atom["HourId"], {})
            group = ", ".join(groups[g]["Name"] for g in atom["GroupIds"] if g in groups)  # Use full name of the group
            subject = subjects.get(atom["SubjectId"], {}).get("Name", "")  # Use full name of the subject
            teacher = teachers.get(atom["TeacherId"], {}).get("Name", "")  # Use full name of the teacher
            room = rooms.get(atom["RoomId"], {}).get("Abbrev", "")
            theme = atom.get("Theme", "")

            table.add_row([
                current_date,
                day_name,
                hour.get("Caption", ""),
                hour.get("BeginTime", ""),
                hour.get("EndTime", ""),
                group,
                subject,
                teacher,
                room,
                theme
            ])

    return table.get_string()

# Example usage
if __name__ == "__main__":
    with open("timetable.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        print(json_to_table_with_days_and_dates(data))