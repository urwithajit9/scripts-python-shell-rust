import os


from parsera import Parsera

url = "https://africaoilgasreport.com/"
elements = {
    "Title": "News title",
    "Publication Date": "Date of news publication",
    "Comments": "Number of comments",
}

scrapper = Parsera()
result = scrapper.run(url=url, elements=elements)

print(result)
