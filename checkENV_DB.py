import subprocess
import torch
import chromadb
import asyncpg
import asyncio
import requests
import redis

async def check_postgres():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            database='knowledge_base_v2',
            user='kb_admin',
            password='1234567890'
        )

        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'documents_metadata_v2'
            )
        """)

        if table_exists:
            result = await conn.fetchval("SELECT COUNT(*) FROM documents_metadata_v2")
            print(f"SUCCESS PostgreSQL: Connected, {result} documents found")
        else:
            print("WARNING PostgreSQL: Connected but documents_metadata_v2 table not found")

        await conn.close()
    except Exception as e:
        print(f"ERROR PostgreSQL: {e}")

def check_gpu():
    try:
        # nvidia-smi
        print("NVIDIA-SMI:")
        subprocess.run(["nvidia-smi"], check=False)

        # Torch CUDA
        print("\nTorch CUDA:")
        print("Torch version:", torch.__version__)
        print("CUDA available:", torch.cuda.is_available())
        print("CUDA version:", torch.version.cuda)
        print("Device count:", torch.cuda.device_count())
        if torch.cuda.is_available():
            print("GPU name:", torch.cuda.get_device_name(0))
    except Exception as e:
        print(f"ERROR Torch/GPU: {e}")

def check_packages():
    try:
        import huggingface_hub
        import transformers
        import sentence_transformers

        print("\nPackage versions:")
        print("huggingface_hub:", huggingface_hub.__version__)
        print("transformers:", transformers.__version__)
        print("sentence-transformers:", sentence_transformers.__version__)
        print("chromadb (client):", chromadb.__version__)
    except Exception as e:
        print(f"ERROR Package import: {e}")

def check_chromadb():
    try:
        # Client
        client = chromadb.HttpClient(
            host="localhost",
            port=8001,
            tenant="default_tenant",
            database="default_database"
        )
        collections = client.list_collections()
        print(f"SUCCESS ChromaDB client connected, {len(collections)} collections found")

        # Server version
        resp = requests.get("http://localhost:8001/api/v2/version")
        if resp.status_code == 200:
            print("ChromaDB server version:", resp.text)
        else:
            print("WARNING Could not fetch server version")
    except Exception as e:
        print(f"ERROR ChromaDB: {e}")

def check_redis():
    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)

        # Test ping
        pong = r.ping()
        if pong:
            print("SUCCESS Redis: Connected (PING -> PONG)")

        # Test set/get
        r.set("test:hello", "world")
        value = r.get("test:hello")
        print(f"Redis test key: test:hello -> {value}")

        # Count keys
        keys = r.keys("*")
        print(f"Redis keys count: {len(keys)}")
    except Exception as e:
        print(f"ERROR Redis: {e}")

if __name__ == "__main__":
    print("=== Environment Check Tool ===\n")
    check_gpu()
    check_packages()
    asyncio.run(check_postgres())
    check_chromadb()
    check_redis()
    print("\nDone.")
