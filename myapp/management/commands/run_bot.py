# # myapp/management/commands/run_bot.py

# from django.core.management.base import BaseCommand
# from myapp.bot import start, echo  # Import your handler functions
# from application import ApplicationBuilder, CommandHandler, MessageHandler, filters

# class Command(BaseCommand):
#     help = 'Run the bot'

#     def handle(self, *args, **options):
#         application = ApplicationBuilder().token(Bot_Token).build()

#         start_handler = CommandHandler('start', start)
#         echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
#         application.add_handler(start_handler)
#         application.add_handler(echo_handler)

#         self.stdout.write(self.style.SUCCESS('Running the bot...'))
#         application.run_polling()
