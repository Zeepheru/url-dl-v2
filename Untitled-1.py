s = r"asdasdsdsdsdsdsadsdsds C:\\users\\asdsadsd\\asdsdsdsd"

print(s.encode("utf-8","ignore")       # To bytes, required by 'unicode-escape' ###Note: Changed to utf8 for non latin character support, in a sense
                .decode('unicode-escape') # Perform the actual octal-escaping decode
                .encode('latin1',"ignore")         # 1:1 mapping back to bytes
                .decode("utf-8",'ignore'))