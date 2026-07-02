from nephthys.transcripts.transcript import Transcript


class Beest(Transcript):
    """Transcript for Treasure Hunt"""

    program_name: str = "Treasure Hunt"
    program_owner: str = "U091DE0M4NB"

    help_channel: str = "C0BFN7GSEC8"
    ticket_channel: str = "C0BFNKAB5EC"
    team_channel: str = "C0B426SMB27"

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0BEV79HD7T"
    first_ticket_create: str = f"""
Heya! I'm an automation that assigns helpers to your question! First off, have you read the <{faq_link}|faq>, it answers a lot of common questions!
if your question has been answered, please hit the button below to mark it as resolved
"""
    ticket_create: str = f"someone should be along to help you soon but in the meantime i suggest you read the faq <{faq_link}|here> to make sure your question hasn't already been answered. if it has been, please hit the button below to mark it as resolved :D"
    resolve_ticket_button: str = "i get it now"
    ticket_resolve: str = f"<@{{user_id}}> has marked this as resolved - make a new post in <#{help_channel}> if this was a mistake"

    not_allowed_channel: str = f"heya, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
