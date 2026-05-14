from dotenv import load_dotenv
import os
from google import genai
from schemawatch.diff_engine import detect_breaking_changes
from schemawatch.parser import load_openapi_file

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def explain_changes(changes):
    if not changes:
        return "No breaking changes detected."

    change_list = "\n".join(
        [f"[{c['severity'].upper()}] {c['message']}" for c in changes]
    )

    prompt = f"""You are an API expert. Explain these breaking API changes detected by SchemaWatch:

{change_list}

For each change:
1. Why is it dangerous?
2. How should a developer fix it?

Be concise and practical."""

    response = client.models.generate_content(
       model="gemma-4-26b-a4b-it",
        contents=prompt
    )
    return response.text


def main():
    changes = detect_breaking_changes(
        load_openapi_file("examples/old.yaml"),
        load_openapi_file("examples/new.yaml")
    )

    print("=== SchemaWatch detected changes ===")
    for c in changes:
        print(f"[{c['severity'].upper()}] {c['message']}")

    print("\n=== Gemma 4 Analysis ===")
    print(explain_changes(changes))


if __name__ == "__main__":
    main()