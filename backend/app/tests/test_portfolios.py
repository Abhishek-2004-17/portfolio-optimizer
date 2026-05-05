from fastapi.testclient import TestClient


class TestPortfolioCRUD:
    """Full CRUD cycle for portfolios."""

    def test_create_portfolio(self, client: TestClient):
        response = client.post(
            "/api/portfolios",
            json={
                "name": "Test Portfolio",
                "description": "A test portfolio",
                "base_currency": "USD",
                "initial_capital": 10000.00,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Portfolio"
        assert data["description"] == "A test portfolio"
        assert data["base_currency"] == "USD"
        assert data["initial_capital"] == 10000.00
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_portfolio_minimal(self, client: TestClient):
        response = client.post(
            "/api/portfolios",
            json={
                "name": "Minimal",
                "initial_capital": 5000.00,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["base_currency"] == "USD"
        assert data["description"] is None

    def test_create_portfolio_invalid_capital(self, client: TestClient):
        response = client.post(
            "/api/portfolios",
            json={
                "name": "Bad Capital",
                "initial_capital": -100,
            },
        )
        assert response.status_code == 422

    def test_create_portfolio_empty_name(self, client: TestClient):
        response = client.post(
            "/api/portfolios",
            json={
                "name": "",
                "initial_capital": 1000,
            },
        )
        assert response.status_code == 422

    def test_list_portfolios_empty(self, client: TestClient):
        response = client.get("/api/portfolios")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_portfolios_with_data(self, client: TestClient):
        for i in range(3):
            client.post(
                "/api/portfolios",
                json={
                    "name": f"Portfolio {i}",
                    "initial_capital": 1000.00 * (i + 1),
                },
            )

        response = client.get("/api/portfolios")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_portfolios_pagination(self, client: TestClient):
        for i in range(5):
            client.post(
                "/api/portfolios",
                json={
                    "name": f"P {i}",
                    "initial_capital": 1000.00,
                },
            )

        response = client.get("/api/portfolios?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_portfolio(self, client: TestClient):
        create_resp = client.post(
            "/api/portfolios",
            json={
                "name": "Get Me",
                "initial_capital": 5000.00,
            },
        )
        portfolio_id = create_resp.json()["id"]

        response = client.get(f"/api/portfolios/{portfolio_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Me"
        assert data["assets"] == []

    def test_get_portfolio_not_found(self, client: TestClient):
        response = client.get("/api/portfolios/9999")
        assert response.status_code == 404

    def test_update_portfolio(self, client: TestClient):
        create_resp = client.post(
            "/api/portfolios",
            json={
                "name": "Original",
                "description": "Original desc",
                "initial_capital": 5000.00,
            },
        )
        portfolio_id = create_resp.json()["id"]

        response = client.put(
            f"/api/portfolios/{portfolio_id}",
            json={"name": "Updated", "description": "Updated desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["description"] == "Updated desc"

    def test_update_portfolio_not_found(self, client: TestClient):
        response = client.put(
            "/api/portfolios/9999",
            json={"name": "Updated"},
        )
        assert response.status_code == 404

    def test_delete_portfolio(self, client: TestClient):
        create_resp = client.post(
            "/api/portfolios",
            json={
                "name": "Delete Me",
                "initial_capital": 1000.00,
            },
        )
        portfolio_id = create_resp.json()["id"]

        response = client.delete(f"/api/portfolios/{portfolio_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_resp = client.get(f"/api/portfolios/{portfolio_id}")
        assert get_resp.status_code == 404

    def test_delete_portfolio_not_found(self, client: TestClient):
        response = client.delete("/api/portfolios/9999")
        assert response.status_code == 404


class TestPortfolioAssetCRUD:
    """Full CRUD cycle for portfolio assets."""

    def _create_portfolio(self, client: TestClient) -> int:
        resp = client.post(
            "/api/portfolios",
            json={
                "name": "Asset Test Portfolio",
                "initial_capital": 10000.00,
            },
        )
        return resp.json()["id"]

    def test_add_asset(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        response = client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={
                "ticker": "AAPL",
                "weight": 0.3,
                "shares": 10.0,
                "purchase_price": 150.00,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert data["weight"] == 0.3
        assert data["shares"] == 10.0
        assert data["purchase_price"] == 150.00
        assert "id" in data
        assert "added_at" in data

    def test_add_asset_duplicate_ticker(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "AAPL", "weight": 0.5},
        )

        response = client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "AAPL", "weight": 0.3},
        )
        assert response.status_code == 422

    def test_add_asset_invalid_weight(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        response = client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "AAPL", "weight": 1.5},
        )
        assert response.status_code == 422

    def test_add_asset_portfolio_not_found(self, client: TestClient):
        response = client.post(
            "/api/portfolios/9999/assets",
            json={"ticker": "AAPL"},
        )
        assert response.status_code == 404

    def test_list_assets(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        for ticker in ["AAPL", "GOOG", "MSFT"]:
            client.post(
                f"/api/portfolios/{portfolio_id}/assets",
                json={"ticker": ticker, "weight": 0.33},
            )

        response = client.get(f"/api/portfolios/{portfolio_id}/assets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        tickers = {a["ticker"] for a in data}
        assert tickers == {"AAPL", "GOOG", "MSFT"}

    def test_list_assets_portfolio_not_found(self, client: TestClient):
        response = client.get("/api/portfolios/9999/assets")
        assert response.status_code == 404

    def test_update_asset(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        create_resp = client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "AAPL", "weight": 0.3, "shares": 10.0},
        )
        asset_id = create_resp.json()["id"]

        response = client.put(
            f"/api/portfolios/{portfolio_id}/assets/{asset_id}",
            json={"weight": 0.5, "shares": 20.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["weight"]) == 0.5
        assert float(data["shares"]) == 20.0

    def test_update_asset_not_found(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        response = client.put(
            f"/api/portfolios/{portfolio_id}/assets/9999",
            json={"weight": 0.5},
        )
        assert response.status_code == 404

    def test_delete_asset(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        create_resp = client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "AAPL", "weight": 0.3},
        )
        asset_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/portfolios/{portfolio_id}/assets/{asset_id}"
        )
        assert response.status_code == 204

        # Verify asset is gone
        list_resp = client.get(f"/api/portfolios/{portfolio_id}/assets")
        assert len(list_resp.json()) == 0

    def test_delete_asset_not_found(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        response = client.delete(
            f"/api/portfolios/{portfolio_id}/assets/9999"
        )
        assert response.status_code == 404

    def test_portfolio_with_assets_includes_assets(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "AAPL", "weight": 0.6},
        )
        client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "GOOG", "weight": 0.4},
        )

        response = client.get(f"/api/portfolios/{portfolio_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["assets"]) == 2

    def test_delete_portfolio_cascades_assets(self, client: TestClient):
        portfolio_id = self._create_portfolio(client)

        client.post(
            f"/api/portfolios/{portfolio_id}/assets",
            json={"ticker": "AAPL", "weight": 0.5},
        )

        response = client.delete(f"/api/portfolios/{portfolio_id}")
        assert response.status_code == 204
