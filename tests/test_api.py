def test_healthz(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_create_and_get(client):
    resp = client.post("/todos", json={"title": "write tests"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["done"] is False

    assert client.get("/todos/1").json()["title"] == "write tests"


def test_create_rejects_empty_title(client):
    assert client.post("/todos", json={"title": ""}).status_code == 422


def test_list_with_done_filter(client):
    client.post("/todos", json={"title": "a"})
    client.post("/todos", json={"title": "b"})
    client.patch("/todos/1", json={"done": True})

    assert len(client.get("/todos").json()) == 2
    assert [t["title"] for t in client.get("/todos?done=true").json()] == ["a"]


def test_patch_and_delete(client):
    client.post("/todos", json={"title": "a"})
    assert client.patch("/todos/1", json={"title": "b"}).json()["title"] == "b"
    assert client.delete("/todos/1").status_code == 204
    assert client.get("/todos/1").status_code == 404


def test_bulk_create(client):
    resp = client.post("/todos/bulk", json=[{"title": "a"}, {"title": "b"}])
    assert resp.status_code == 201


def test_missing_returns_404(client):
    assert client.get("/todos/99").status_code == 404
    assert client.patch("/todos/99", json={"done": True}).status_code == 404
    assert client.delete("/todos/99").status_code == 404
