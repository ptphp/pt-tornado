# 假设将/upload交给UploadHandler处理的话
02	 
03	import tornado.web
04	import tempfile
05	import Image
06	import time
07	import logging
08	 
09	     
10	class UploadHandler(tornado.web.RequestHandler):
11	     def post(self):
12	          if self.request.files == {} or 'mypicture' not in self.request.files:
13	               """ 看是否有文件且name为picture，跟HTML代码对应 """
14	               self.write('<script>alert("请选择图片")</script>')
15	               return
16	          # 有文件，判断是否为我们需要的格式
17	          # 常用的图片格式有：image/jpeg，image/bmp，image/pjpeg，image/gif，image/x-png，image/png
18	          image_type_list = ['image/gif', 'image/jpeg', 
19	                             'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
20	          send_file = self.request.files['mypicture'][0]
21	          if send_file['content_type'] not in image_type_list:
22	               self.write('<script>alert("仅支持jpg,jpeg,bmp,gif,png格式的图片！")</script>')
23	               return
24	          # 上述判断含有很大的上传漏洞，可以通过PIL来避免这些。
25	          # 限制上传文件的大小，通过len获取字节数
26	          if len(send_file['body']) > 4 * 1024 * 1024:
27	               self.write('<script>alert("请上传4M以下的图片");</script>') 
28	               return
29	          # 满足要求后，将图片存储。
30	          # 存储也就是将send_file['body']内容进行存储，type(send_file['body'])为str
31	          # 先将文件写入临时文件，然后再用PIL对这个临时文件进行处理。
32	          tmp_file = tempfile.NamedTemporaryFile(delete=True) #创建临时文件，当文件关闭时自动删除
33	          tmp_file.write(send_file['body'])  #写入临时文件
34	          tmp_file.seek(0)   #将文件指针指向文件头部，因为上面的操作将指针指向了尾部。
35	 
36	          #此时用PIL再处理进行存储，PIL打开不是图片的文件会出现IOERROR错误，这就可以识别后缀名虽然是图片格式，但内容并非是图片。
37	          try:
38	               image_one = Image.open( tmp_file.name )
39	          except IOError, error:
40	               logging.info(error)   # 进行日志记录，因为这些操作大多数是破坏者的做法。
41	               logging.info('+'*30 + '\n')
42	               logging.info(self.request.headers)
43	               tmp_file.close()
44	               self.write('<script>alert("图片不合法！")</script>')
45	               return
46	 
47	          # 判断图片尺寸，不在尺寸内拒绝操作
48	          if image_one.size[0] < 250 or image_one.size[1] < 250 or \
49	                image_one.size[0] > 2000 or image_one.size[1] > 2000:
50	                tmp_file.close()
51	                self.write('<script>alert("图片长宽在250px~2000px之间！")</script>')
52	                return
53	 
54	          
55	          # 进行存储。
56	          # 指定存储目录，产生新的文件名。
57	          # 获取文件格式，用PIL获得的format不一定正确，所以用原文件名获得
58	          image_path = "./static/picture/"
59	          image_format = send_file['filename'].split('.').pop().lower()
60	          tmp_name = image_path + str(int(time.time())) + image_format
61	          image_one.save(tmp_name)
62	 
63	          #关闭临时文件，关闭后临时文件自动删除
64	          tmp_file.close()
65	          self.write('<script>alert("文件上传成功，路径为：" + image_path[1:])</script>')
66	          return
