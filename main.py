import app.interfaces.cli.menu as cli
import app.application.users.user_manager as users_manager


user = users_manager.user_prompt()
if user:
    cli.current_user = user.login
    cli.menu_0()
else:
    print('Wprowadzono błędne dane logowania!')