import sys
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001/"

print(f"Smoke Test : {url}")

try:
    with urlopen(url, timeout=10) as response:
        status = response.status
        print(f"Code HTTP : {status}")

        if status == 200:
            print("RESULTAT : PASSED")
            sys.exit(0)

        print("RESULTAT : FAILED")
        sys.exit(1)

except (URLError, HTTPError, TimeoutError) as error:
    print(f"Erreur : {error}")
    print("RESULTAT : FAILED")
    sys.exit(1)
