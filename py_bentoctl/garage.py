import requests
import time


class GarageAdminClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str) -> requests.Response:
        resp = self.session.get(f"{self.base_url}{path}")
        resp.raise_for_status()
        return resp

    def post(self, path: str, data: dict | list | None = None) -> requests.Response:
        resp = self.session.post(f"{self.base_url}{path}", json=data or {})
        resp.raise_for_status()
        return resp

    def wait_until_ready(self, timeout: int = 60, poll_interval: int = 2) -> bool:
        """Wait for the admin API to become healthy."""
        elapsed = 0
        while elapsed < timeout:
            try:
                resp = self.session.get(f"{self.base_url}/health", timeout=2)
                if resp.status_code == 200:
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            time.sleep(poll_interval)
            elapsed += poll_interval
        return False

    def get_node_id(self) -> str:
        status = self.get("/v2/GetClusterStatus").json()
        return status["nodes"][0]["id"]

    def configure_layout(
        self, node_id: str, capacity_bytes: int = 100_000_000_000
    ) -> None:
        layout = self.get("/v2/GetClusterLayout").json()

        for role in layout.get("roles", []):
            if role["id"] == node_id:
                # Layout already configured, skip
                return

        # Layout needs configuration - use UpdateClusterLayout
        layout_update = {
            "remove": [],
            "update": {
                node_id: {"zone": "dc1", "capacity": capacity_bytes, "tags": []}
            },
        }
        resp = self.post("/v2/UpdateClusterLayout", layout_update)
        current_version = resp.json()["version"]
        self.post("/v2/ApplyClusterLayout", {"version": current_version})

    def create_access_key(self) -> tuple[str, str]:
        """Returns (access_key_id, secret_access_key)."""
        key_info = self.post("/v2/CreateKey").json()
        return key_info["accessKeyId"], key_info["secretAccessKey"]

    def list_buckets(self) -> list[dict]:
        return self.get("/v2/ListBuckets").json()

    def create_bucket(self, name: str) -> tuple[str, bool]:
        """Create bucket if it doesn't exist. Returns bucket ID."""
        for bucket in self.list_buckets():
            if name in bucket.get("globalAliases", []):
                return bucket["id"], False
        return self.post("/v2/CreateBucket", {"globalAlias": name}).json()["id"], True

    def grant_bucket_access(
        self,
        bucket_id: str,
        access_key_id: str,
        read: bool = True,
        write: bool = True,
        owner: bool = True,
    ) -> None:
        self.post(
            "/v2/AllowBucketKey",
            {
                "bucketId": bucket_id,
                "accessKeyId": access_key_id,
                "permissions": {"read": read, "write": write, "owner": owner},
            },
        )
