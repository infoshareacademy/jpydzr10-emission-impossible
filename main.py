import app.interfaces.cli.menu as cli
import app.application.users.users as users


if users.user_prompt():
    cli.menu_0()
else:
    print('Wprowadzono błędne dane logowania!')