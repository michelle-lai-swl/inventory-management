"""
Tests for restocking API endpoints.
"""
from datetime import datetime, timezone


class TestRestockingRecommendations:
    """Test suite for GET /api/restocking/recommendations."""

    def test_get_recommendations_default_budget(self, client):
        """Test getting recommendations with the default budget returns items with correct structure."""
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        first = data[0]
        assert "item_sku" in first
        assert "item_name" in first
        assert "current_demand" in first
        assert "forecasted_demand" in first
        assert "demand_gap" in first
        assert "trend" in first
        assert "unit_cost" in first
        assert "recommended_quantity" in first
        assert "line_total" in first

    def test_recommendations_exclude_decreasing_demand(self, client):
        """MTR-304 has demand_gap < 0 and must never appear in recommendations."""
        response = client.get("/api/restocking/recommendations?budget=50000")
        assert response.status_code == 200

        data = response.json()
        skus = [item["item_sku"] for item in data]
        assert "MTR-304" not in skus

    def test_recommendations_increasing_items_appear_first(self, client):
        """Items with trend='increasing' must be ranked before 'stable' items."""
        response = client.get("/api/restocking/recommendations?budget=50000")
        assert response.status_code == 200

        data = response.json()
        assert len(data) > 0

        # Find the last increasing item and the first non-increasing item
        last_increasing_idx = -1
        first_non_increasing_idx = len(data)
        for i, item in enumerate(data):
            if item["trend"] == "increasing":
                last_increasing_idx = i
            elif last_increasing_idx == -1:
                # We haven't seen any increasing items yet; first item is not increasing
                first_non_increasing_idx = i
                break

        # All increasing items must come before any non-increasing item
        assert last_increasing_idx < first_non_increasing_idx

    def test_recommendations_budget_constraint(self, client):
        """A $8 budget is below the cheapest unit cost ($8.75 for FLT-405); must return empty."""
        response = client.get("/api/restocking/recommendations?budget=8")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_recommendations_all_have_positive_demand_gap(self, client):
        """Every recommendation must have a strictly positive demand_gap."""
        response = client.get("/api/restocking/recommendations?budget=50000")
        assert response.status_code == 200

        data = response.json()
        assert len(data) > 0

        for item in data:
            assert item["demand_gap"] > 0

    def test_recommendations_line_total_within_budget(self, client):
        """The cumulative line_total of all recommendations must not exceed the budget."""
        budget = 5000
        response = client.get(f"/api/restocking/recommendations?budget={budget}")
        assert response.status_code == 200

        data = response.json()
        total = sum(item["line_total"] for item in data)
        assert total <= budget

    def test_recommendations_line_total_matches_qty_times_cost(self, client):
        """Each item's line_total must equal recommended_quantity * unit_cost."""
        response = client.get("/api/restocking/recommendations?budget=50000")
        assert response.status_code == 200

        for item in response.json():
            expected = round(item["recommended_quantity"] * item["unit_cost"], 2)
            assert abs(item["line_total"] - expected) < 0.01


class TestRestockingOrders:
    """Test suite for POST /api/restocking/orders."""

    def _sample_items(self):
        return [
            {
                "item_sku": "WDG-001",
                "item_name": "Industrial Widget Type A",
                "quantity": 10,
                "unit_cost": 45.00
            }
        ]

    def test_create_restocking_order_returns_201(self, client):
        """POST with valid items returns 201 and a well-formed order."""
        response = client.post(
            "/api/restocking/orders",
            json={"items": self._sample_items()}
        )
        assert response.status_code == 201

        order = response.json()
        assert order["status"] == "Submitted"
        assert order["customer"] == "Internal Restocking"
        assert order["order_number"].startswith("ORD-")
        assert "id" in order
        assert "order_date" in order
        assert "expected_delivery" in order
        assert isinstance(order["total_value"], (int, float))
        assert order["total_value"] > 0

    def test_create_restocking_order_14_day_delivery(self, client):
        """Expected delivery must be exactly 14 days after order_date."""
        response = client.post(
            "/api/restocking/orders",
            json={"items": self._sample_items()}
        )
        assert response.status_code == 201

        order = response.json()
        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = datetime.fromisoformat(order["expected_delivery"])
        delta_days = (expected_delivery - order_date).days
        assert delta_days == 14

    def test_create_restocking_order_total_value(self, client):
        """total_value must equal sum of quantity * unit_cost across all items."""
        items = [
            {"item_sku": "WDG-001", "item_name": "Widget A", "quantity": 5, "unit_cost": 45.00},
            {"item_sku": "FLT-405", "item_name": "Oil Filter", "quantity": 20, "unit_cost": 8.75},
        ]
        response = client.post("/api/restocking/orders", json={"items": items})
        assert response.status_code == 201

        expected_total = round(5 * 45.00 + 20 * 8.75, 2)
        assert abs(response.json()["total_value"] - expected_total) < 0.01

    def test_create_restocking_order_appears_in_orders(self, client):
        """After placing a restocking order, GET /api/orders must include a Submitted order."""
        client.post(
            "/api/restocking/orders",
            json={"items": self._sample_items()}
        )

        orders_response = client.get("/api/orders")
        assert orders_response.status_code == 200

        submitted = [o for o in orders_response.json() if o["status"] == "Submitted"]
        assert len(submitted) > 0

    def test_create_restocking_order_empty_items_returns_400(self, client):
        """POST with an empty items list must return 400."""
        response = client.post("/api/restocking/orders", json={"items": []})
        assert response.status_code == 400
        assert "detail" in response.json()
