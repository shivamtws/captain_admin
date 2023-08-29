from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    
def ready(self):
        from myapp.management.commands.run_bot import Command
        Command().handle()