import os
import sys
from dotenv import load_dotenv
from google import genai



def main():
    if len(sys.argv)==2:
        load_dotenv()
        api_key=os.environ.get("GEMINI_API_KEY")
        client=genai.Client(api_key=api_key)
        prompt=sys.argv[1]
        response=client.models.generate_content(model="gemini-2.0-flash-001",contents=prompt)
        print(response.text)
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    else:
        raise Exception("Prompt wasn't provided!")
        exit(1)

if __name__ == "__main__":
    main()
