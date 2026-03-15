import app.interfaces.cli.menu as cli
import app.application.users.user_manager as users_manager


if users_manager.user_prompt():
    cli.menu_0()
else:
    print('Wprowadzono błędne dane logowania!')