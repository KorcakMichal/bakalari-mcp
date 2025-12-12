from urllib import response
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
import logging
from client import Client
from datetime import datetime
import pytz
import formatter

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("bakalari")

mcp.description = "Bakalari MCP Server, an interface to the Bakalari school information system, if user refers to messages he may refer to komens messages."

client = Client(os.getenv("BK_PWD"), os.getenv("BK_USER"), os.getenv("BK_API_BASE"))


def current_time():
    prague_tz = pytz.timezone("Europe/Prague")
    current_time = datetime.now(prague_tz)
    return current_time.strftime("%Y-%m-%d %H:%M:%S")


# region table


@mcp.tool()
def get_permanent_timetable():
    """Get permanent timetable from Bakalari."""
    return client.get_permanent_timetable()


@mcp.tool()
def get_actual_timetable():
    """Get actual timetable from Bakalari."""
    res = formatter.dict_to_table_actual_timetable(client.get_actual_timetable())
    return res + f"\nCurrent time is {current_time()}"


# endregion table

# region events


@mcp.tool()
def get_events():
    """Get events from Bakalari."""
    return client.get_events()


@mcp.tool()
def get_events_my():
    """Get my events from Bakalari."""
    return client.get_events_my()


@mcp.tool()
def get_events_public():
    """Get public events from Bakalari."""
    return client.get_events_public()


# endregion events

# region homework


@mcp.tool()
def get_homeworks():
    """Get homeworks from Bakalari."""
    return client.get_homeworks()


@mcp.tool()
def get_homeworks_count_actual():
    """Get count of actual homeworks from Bakalari."""
    return client.get_homeworks_count_actual()


# endregion homework

# region marks


@mcp.tool()
def get_marks():  # NOTE: sometimes misuderstood by agent
    """Get marks from Bakalari."""
    return client.get_marks()


@mcp.tool()
def get_marks_count_new():
    """Get count of new marks from Bakalari. Needed for new mark notifications."""
    return client.get_marks_count_new()


@mcp.tool()
def get_marks_final():
    """Get final marks from Bakalari. Be Careful when calculating averages. Be sure if user wants to only half year or whole year marks. Probably only from second."""
    return client.get_marks_final()


@mcp.tool()
def get_marks_measures():
    """Get marks pedagogical measures from Bakalari."""
    return client.get_marks_measures()


# not needed agent do it alone and automatically
# @mcp.tool()
# def post_marks_what_if(data):
#    """Post marks what if to Bakalari."""
#    return client.post_marks_what_if(data)


# endregion marks

# region payments

# vynechání naše škola nepoužívá
'''
@mcp.tool()
def get_payments_classfund():
    """Get class fund payments from Bakalari."""
    return client.get_payments_classfund()


@mcp.tool()
def get_payments_classfund_paymentsinfo():
    """Get class fund payments info from Bakalari."""
    return client.get_payments_classfund_paymentsinfo()


@mcp.tool()
def get_payments_classfund_summary():
    """Get class fund summary from Bakalari."""
    return client.get_payments_classfund_summary()
'''

# endregion payments

# region subject


@mcp.tool()
def get_subjects():
    """Get subjects from Bakalari."""
    return client.get_subjects()


@mcp.tool()
def get_subjects_themes_id(id):
    """Get topics of lessons of some subject from Bakalari."""
    return client.get_subjects_themes_id(id)


@mcp.tool()
def get_substitutions():
    """Get substitutions from Bakalari."""
    return client.get_substitutions()


# endregion subject

# region user and absence


@mcp.tool()
def get_absence_student():
    """Get student absences from Bakalari."""
    return client.get_absence_student()


@mcp.tool()
def get_user():
    """Get user from Bakalari."""
    return client.get_user()


# endregion user and absence

# region komens


# region received messages
@mcp.tool()
def get_komens_messages_received():
    """Get komens messages received from Bakalari."""

    return client.post_komens_messages_received()


@mcp.tool()
def get_komens_messages_received_id(id):
    """Get komens messages received by ID from Bakalari."""
    return client.get_komens_messages_received_id(id)


@mcp.tool()
def get_komens_messages_received_unread():
    """Get number of unread messages received from Bakalari."""
    return client.get_komens_messages_received_unread()


# endregion received messages


# region sent messages
@mcp.tool()
def get_komens_messages_sent_id(id):
    """Get messages sent by ID from Bakalari."""
    return client.get_komens_messages_sent_id(id)


@mcp.tool()
def get_komens_messages_sent():  # otestovat, musí se poslat zpráva prvně někomu
    """Get komens messages sent from Bakalari."""
    return client.post_komens_messages_sent()


# endregion sent messages


# region post messages
# TODO: otestovat všechny post nástroje, a připravit data structures
@mcp.tool()
def post_komens_message(data):
    """Post komens message to Bakalari."""
    return client.post_komens_message(data)


@mcp.tool()
def post_komens_message_mark_as_read(id):
    """Post komens message mark as read to Bakalari."""
    return client.post_komens_message_mark_as_read(id)


@mcp.tool()
def post_komens_message_types_edit(id):
    """Post komens message types edit to Bakalari."""
    return client.post_komens_message_types_edit(id)


@mcp.tool()
def post_komens_message_types_reply(id):
    """Post komens message types reply to Bakalari."""
    return client.post_komens_message_types_reply(id)


@mcp.tool()
def post_komens_messages_apology(id):
    """Post komens messages apology to Bakalari."""
    return client.post_komens_messages_apology(id)


# endregion post messages


# region other messeges tools
@mcp.tool()
def get_komens_message_types():
    """Get komens message types which can be used in Bakalari."""
    return client.get_komens_message_types()


@mcp.tool()
def get_komens_message_by_id(id):
    """Get komens message from Bakalari."""
    return client.get_komens_message_by_id(id)


@mcp.tool()
def get_komens_attachment_by_id(id):
    """Get komens attachment from Bakalari."""
    return client.get_komens_attachment_by_id(id)


@mcp.tool()
def get_komens_messages_rating():
    """Get komens messages rating from Bakalari."""
    return client.get_komens_messages_rating()


# endregion other messeges tools

# endregion komens


@mcp.prompt()
def welcome_message():
    return """Jsi napomocný agent pro studenty, kteří používají školní informační systém Bakalari. Používej dostupné nástroje k získání informací o rozvrhu, známkách, absencích, domácích úkolech a dalších funkcích systému Bakalari. Odpovídej jasně a stručně na dotazy uživatelů a poskytuj přesné informace založené na datech získaných z Bakalari."""


if __name__ == "__main__":
    mcp.run(transport="sse")
