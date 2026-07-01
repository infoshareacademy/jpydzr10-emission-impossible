from django.db import connection, transaction


class DatabaseUserAuditMiddleware:
    """
    Middleware ustawiające ID użytkownika w sesji PostgreSQL.
    Dzięki temu trigger bazodanowy wie, kto wykonał operację CRUD.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SET LOCAL app.current_user_id = %s;", [str(request.user.id)]
                    )
                response = self.get_response(request)
            return response

        return self.get_response(request)
