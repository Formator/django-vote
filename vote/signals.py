from django.dispatch import Signal

post_voted = Signal(providing_args=["sender", "user_id", "action", "instance"])
