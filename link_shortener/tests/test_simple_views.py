import pytest
from link_shortener.server import create_app


def test_about_page():
    app = create_app()
    request, response = app.test_client.get('/links/about')
    assert response.status == 200


def test_about_page2():
    app = create_app()
    request, response = app.test_client.get('/links/about')
    assert response.status == 200
