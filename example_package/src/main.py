import requests

def get():
    target = "https://techbookfest.org"
    response = requests.get(target)
    print(response.text)

if __name__=="__main__":
    get()
