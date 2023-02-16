# Import requrired modules
import requests
import os
from PIL import Image
from IPython.display import IFrame

#URL
url='https://scontent-lga3-2.xx.fbcdn.net/v/t39.30808-6/313403958_179274318011155_5560488167210662420_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=ydXlxLvSmYUAX8fnXA7&_nc_ht=scontent-lga3-2.xx&oh=00_AfAHjjVqypAPFFcAfaXTX10Il_i-CfKBA3Kk5GmBQDUEmQ&oe=63F1F8F7'

#Make a get requests
r=requests.get(url)

#Export the Image
#Specify the file path and name
path=os.path.join(os.getcwd(),'image.png')

#Save the Image
with open(path,'wb') as f:
    f.write(r.content)

#View the Image
Image.open(path)
