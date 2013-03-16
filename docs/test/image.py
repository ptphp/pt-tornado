import Image
import StringIO
f = open('D:\Dhole\Workspace\game110\cn\game110/static/upload/1361564251.jpg',"rb")

im = Image.open(StringIO.StringIO(f.read())) #@UndefinedVariable
print im.size
print im.mode
print im.format
im.show()