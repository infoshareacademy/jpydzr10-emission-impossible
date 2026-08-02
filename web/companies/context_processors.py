from companies.models import Companies


def global_user_companies(request):
    """
    Dostarcza listę spółek (do których użytkownik ma dostęp)
    dla globalnych komponentów, takich jak pływający widget AI.
    """
    if not request.user.is_authenticated:
        return {}

    user = request.user
    if user.role == "admin" or user.is_superuser:
        companies = Companies.objects.all().order_by("name")
    else:
        companies = (
            Companies.objects.filter(
                user_permissions__user=user, user_permissions__can_read=True
            )
            .distinct()
            .order_by("name")
        )

    return {"global_companies": companies}
