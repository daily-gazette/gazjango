from gazjango.misc.exceptions import RelationshipMismatch

class PollException(Exception):
    "Something went wrong with a poll."

class NotVoting(PollException):
    "The poll is not currently accepting votes."

class PollMismatch(PollException, RelationshipMismatch):
    "The option and poll specified don't agree."

class PermissionDenied(PollException):
    "You aren't allowed to vote in this poll."

class AlreadyVoted(PollException):
    "You've already voted in this poll."
