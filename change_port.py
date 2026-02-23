with open("app.py", "r") as f:
    content = f.read()
content = content.replace("PORT = 8080", "PORT = 8081")
with open("app.py", "w") as f:
    f.write(content)
print("Port changed to 8081")
