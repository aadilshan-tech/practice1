# from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User

# class Command(BaseCommand):
#     help = "Create default superuser"

#     def handle(self, *args, **kwargs):
#         username = "aadilshan"
#         email = "aadilshan5065@gmail.com"
#         password = "Rasheed@5065"

#         if not User.objects.filter(username=username).exists():
#             User.objects.create_superuser(
#                 username=username,
#                 email=email,
#                 password=password
#             )
#             self.stdout.write("Superuser created")
#         else:
#             self.stdout.write("Superuser already exists")
