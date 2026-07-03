import pytest
from web.companies.models import Company

@pytest.fixture
def company():
    return Company.objects.create(
        name="Test Company"
    )
