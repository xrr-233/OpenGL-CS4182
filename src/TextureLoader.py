from OpenGL.GL import *
from PIL import Image

def load_texture(path, texture):
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # 设置材质属性（比如图片拉伸）
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)  # 设置过滤器（像jpg还是像bmp）
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    image = Image.open(path)
    if(path == "../obj/chibi.png"):
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

    if(path[-3:] == "jpg"):
        img_data = image.convert("RGB").tobytes()  # jpg用RGB
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    elif(path[-3:] == "png"):
        img_data = image.convert("RGBA").tobytes() # png用RGBA
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    return texture