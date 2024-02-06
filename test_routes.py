import pytest, requests
from fastapi import status
from fastapi.testclient import TestClient
from routes import app

ENDPOINT = "http://127.0.0.1:8000"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def test_user():
    return {"username": "Safdar", "password": "tim1234"}


def test_login(client, test_user):
    response = client.post(ENDPOINT + "/token", data=test_user)
    assert response.status_code == status.HTTP_200_OK

    token = response.json()["access_token"]
    assert token is not None

    return token


def test_delete_post_failed(client, test_user):
    token = test_login(client, test_user)
    response = client.delete(ENDPOINT + "/delete/post/689", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_post_success(client, test_user):
    token = test_login(client, test_user)
    response = client.delete(ENDPOINT + "/delete/post/7", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK


def test_update_post_failed(client, test_user):
    token = test_login(client, test_user)
    post_body = {"title": "test_case", "content": "test_content"}
    response = client.put(ENDPOINT + "/update/post/689", json=post_body, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_post_success(client, test_user):
    token = test_login(client, test_user)
    post_body = {"title": "test_case", "content": "test_content"}
    response = client.put(ENDPOINT + "/update/post/8", json=post_body, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK


def test_search_post_failed(client, test_user):
    token = test_login(client, test_user)
    response = client.get(ENDPOINT + "/search/post/689", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_search_post_success(client, test_user):
    token = test_login(client, test_user)
    response = client.get(ENDPOINT + "/search/post/8", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK


def test_user_posts_failed(client, test_user):
    token = test_login(client, test_user)
    response = client.get(ENDPOINT + "/user/posts", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_user_posts_success(client, test_user):
    token = test_login(client, test_user)
    response = client.get(ENDPOINT + "/user/posts", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK


def test_insert_post_success(client, test_user):
    token = test_login(client, test_user)
    post_body = {"title": "test_case", "content": "test_content"}
    response = client.post(ENDPOINT + "/insert/post", json=post_body, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK


def test_insert_post_failed(client, test_user):
    token = test_login(client, test_user)
    post_body = {"title": "test_case", "content": "test_content"}
    response = client.post(ENDPOINT + "/insert/post", json=post_body, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_posts_success(client, test_user):
    token = test_login(client, test_user)
    response = client.get(ENDPOINT + "/posts", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK


def test_user_signup_success():
    temp_user = { "username": "strrrr", "email": "user@example.com", "password": "stringggggg" }
    response = requests.post(ENDPOINT + "/signup", json=temp_user)

    assert response.status_code == status.HTTP_200_OK


def test_user_signup_failed(client, test_user):
    token = test_login(client, test_user)
    temp_user = { "username": "Safdar", "email": "user@example.com", "password": "tim1234" }
    response = client.post(ENDPOINT + "/signup", json=temp_user, headers={"Authorization": f"Bearer {token}"})

    assert (response.status_code == status.HTTP_406_NOT_ACCEPTABLE)\
           or (response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY)


def test_reading_own_items_success(client, test_user):
    token = test_login(client, test_user)
    response = client.get(ENDPOINT + "/users/me/items", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == status.HTTP_200_OK
