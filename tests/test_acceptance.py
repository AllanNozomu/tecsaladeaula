import pytest


@pytest.mark.django_db
def test_is_admin_working(client):
    response = client.get('/admin/')
    assert response.status_code == 200
    assert 'Timtec Admin' in response.content
