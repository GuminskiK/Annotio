def test_create_api_key(logged_in_client):

    response = logged_in_client.post(
        "/apikeys",
        json={"name": "MyKey"},

    )

    assert response.status_code == 201
    assert "key" in response.json()

def test_delete_api_key(logged_in_client):

    create_response = logged_in_client.post("/apikeys", json={"name": "MyKey"})
    key_id = create_response.json()["id"]

    response = logged_in_client.delete(
        f"/apikeys/{key_id}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": "api key revoked"}

def test_get_my_keys(logged_in_client):

    logged_in_client.post("/apikeys", json={"name": "MyKey"})

    response = logged_in_client.get("/apikeys/me")

    assert response.status_code == 200
    assert "key_hint" in response.json()[0]
