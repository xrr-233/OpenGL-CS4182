from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
from TextureLoader import load_texture
from ObjLoader import ObjLoader
import glfw
import pyrr
import math
import numpy as np

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

lastX = WINDOW_WIDTH / 2
lastY = WINDOW_HEIGHT / 2
first_mouse = True
left, right, forward, backward = False, False, False, False

scene_index = 1
scene_1_angle = 0
scene_1_acc = 1
scene_2_angle = 0
scene_2_dis = 3
scene_2_acc = 0
scene_3_dis = 0
scene_4_dis = 1
scene_4_acc = 0.05
scene_5_dis = 1
scene_6_dis = 0
scene_7_dis = 0
scene_7_acc = 0.3
scene_7_decay = 0.5
scene_8_dis = 0
scene_8_acc = 0.3
scene_8_decay = 0.5
scene_9_x = 1
scene_9_y = 3
scene_9_z = 0
scene_9_roll = 0
scene_9_pitch = 3
scene_9_yaw = -math.pi / 2
scene_10_dis_x = 0
scene_10_dis_y = -10
scene_10_dis_z = 0
scene_10_step = 1

vertex_src = """
# version 330

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;
layout(location = 2) in vec2 a_texture;
layout(location = 3) in vec3 a_normal;

uniform mat4 model; // combined translation and rotation
uniform mat4 view;
uniform mat4 projection;

out vec3 fragPos;
out vec3 Normal;
out vec3 v_color;
out vec2 v_texture;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    fragPos = vec3(view * vec4(a_position, 1.0));
    Normal = mat3(transpose(inverse(view))) * a_normal;
    v_color = a_color;
    v_texture = a_texture;
    
    //v_texture = 1 - a_texture;                      // Flips the texture vertically and horizontally
    //v_texture = vec2(a_texture.s, 1 - a_texture.t); // Flips the texture vertically
}
"""

fragment_src = """
# version 330

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float     shininess;
};  

struct Light {
    vec3 position;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

in vec3 fragPos;
in vec3 Normal;
in vec3 v_color;
in vec2 v_texture;

out vec4 out_color;

uniform int switcher; // 切换材质与颜色
uniform sampler2D s_texture;
uniform vec3 viewPos;
uniform Material material;
uniform Light light;

void main()
{
    
    if (switcher == 0){
        out_color = texture(s_texture, v_texture);
    }
    else if (switcher == 1){
        // Ambient
        vec3 ambient = light.ambient * vec3(texture(material.diffuse, v_texture));
        
        // Diffuse 
        vec3 norm = normalize(Normal);
        vec3 lightDir = normalize(light.position - fragPos);
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, v_texture));
        
        // Specular
        vec3 viewDir = normalize(viewPos - fragPos);
        vec3 reflectDir = reflect(-lightDir, norm);  
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
        vec3 specular = light.specular * spec * vec3(texture(material.specular, v_texture));
        
        out_color = vec4(ambient + diffuse + specular, 1.0f);
    }
}
"""

class Window:
    def __init__(self, width, height, name):
        if not glfw.init():
            raise Exception("glfw cannot be initialized!")

        self._win = glfw.create_window(width, height, name, None, None)

        if(not self._win):
            glfw.terminate()
            raise Exception("glfw window cannot be created!")

        glfw.set_window_pos(self._win, 500, 200)
        glfw.set_window_size_callback(self._win, self.window_resize) # 调整窗口时重新渲染
        glfw.set_cursor_pos_callback(self._win, self.mouse_look_clb) # set the mouse position callback
        glfw.set_cursor_enter_callback(self._win, self.mouse_enter_clb) # set the mouse enter callback
        glfw.set_key_callback(self._win, self.key_input_clb)
        glfw.make_context_current(self._win)

    def window_resize(self, window, width, height):
        glViewport(0, 0, width, height)
        projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

    # the mouse position callback function
    def mouse_look_clb(self, window, xpos, ypos):
        global first_mouse, lastX, lastY, scene_index

        if first_mouse:
            lastX = xpos
            lastY = ypos
            first_mouse = False

        xoffset = xpos - lastX
        yoffset = lastY - ypos

        lastX = xpos
        lastY = ypos

        if(scene_index == 10):
            cam.process_mouse_movement(xoffset, yoffset)

    # the mouse enter callback function
    def mouse_enter_clb(self, window, entered):
        global first_mouse

        if not entered:
            first_mouse = True

    def key_input_clb(self, window, key, scancode, action, mode):
        global left, right, forward, backward
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        if key == glfw.KEY_W and action == glfw.PRESS:
            forward = True
        elif key == glfw.KEY_W and action == glfw.RELEASE:
            forward = False
        if key == glfw.KEY_S and action == glfw.PRESS:
            backward = True
        elif key == glfw.KEY_S and action == glfw.RELEASE:
            backward = False
        if key == glfw.KEY_A and action == glfw.PRESS:
            left = True
        elif key == glfw.KEY_A and action == glfw.RELEASE:
            left = False
        if key == glfw.KEY_D and action == glfw.PRESS:
            right = True
        elif key == glfw.KEY_D and action == glfw.RELEASE:
            right = False

    def main_loop(self):
        while(not glfw.window_should_close(self._win)):
            global scene_index, model

            glfw.poll_events()
            if(scene_index == 10):
                cam.do_movement()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            if(scene_index == 0):
                #view = pyrr.matrix44.create_look_at(pyrr.Vector3([10, 10, 0]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))
                pass
            if(scene_index == 1):
                global scene_1_angle, scene_1_acc
                scene_1_angle += scene_1_acc
                if(scene_1_angle < 7211.5 and scene_1_acc < 20):
                    scene_1_acc += 0.25
                if(scene_1_angle > 7211.5):
                    scene_1_acc -= 0.25
                if(scene_1_angle == 7999):
                    scene_1_angle = 8000
                rot_x = pyrr.Matrix44.from_x_rotation(math.pi * 0.5 * scene_1_angle / 1000) # 建立一个rotation的4*4矩阵
                rot_y = pyrr.Matrix44.from_y_rotation(math.pi * 0.75 * scene_1_angle / 1000)
                # glUniformMatrix4fv(rotation_loc, 1, GL_FALSE, rot_x * rot_y)
                # glUniformMatrix4fv(rotation_loc, 1, GL_FALSE, rot_x @ rot_y)
                rotation = pyrr.matrix44.multiply(rot_x, rot_y)
                model = pyrr.matrix44.multiply(rotation, cube_translation)
                # model = pyrr.matrix44.multiply(model, scale) # 正交用
                view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, -3]))
                if(scene_1_angle > 8000):
                    model = cube_translation
                    scene_index += 1
                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                glBindVertexArray(VAO[0])
                glBindTexture(GL_TEXTURE_2D, textures[0])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
            if(scene_index == 2):
                global scene_2_angle, scene_2_dis, scene_2_acc
                scene_2_angle += scene_2_acc * math.pi / 180
                scene_2_dis -= scene_2_acc / 360
                if(scene_2_acc <= 2):
                    scene_2_acc += 0.0625
                view = pyrr.matrix44.create_look_at(pyrr.Vector3([scene_2_dis * math.sin(scene_2_angle), 0, scene_2_dis * math.cos(scene_2_angle)]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))
                if(scene_2_dis <= 1):
                    scene_index += 1
                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                glBindVertexArray(VAO[0])
                glBindTexture(GL_TEXTURE_2D, textures[0])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
            if(scene_index == 3):
                global scene_3_dis
                view = pyrr.matrix44.create_look_at(pyrr.Vector3([1, scene_3_dis, 0]), pyrr.Vector3([0, scene_3_dis, 0]), pyrr.Vector3([0, 1, 0]))
                if(scene_3_dis < 3):
                    scene_3_dis += 0.05
                else:
                    scene_index += 1

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        scene_3_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 0, z]))
                        model = scene_3_translation
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[0])
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        scene_3_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        model = scene_3_translation
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[1])
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
            if(scene_index == 4):
                global scene_4_dis, scene_4_acc

                view = pyrr.matrix44.create_look_at(pyrr.Vector3([1, 3, 0]), pyrr.Vector3([0, 3, 0]), pyrr.Vector3([0, 1, 0]))
                if (scene_4_dis < 11):
                    scene_4_dis += scene_4_acc
                    if(scene_4_dis - int(scene_4_dis) >= 0.775):
                        scene_4_acc -= 0.005
                    else:
                        scene_4_acc = 0.05

                else:
                    scene_index += 1

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        if(x <= -10 and z <= 0):
                            if(math.fabs(x) + math.fabs(z) >= 19 + scene_4_dis):
                                scene_4_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, scene_4_dis, z]))
                            elif(math.fabs(x) + math.fabs(z) >= 21):
                                scene_4_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, math.fabs(x) + math.fabs(z) - 19, z]))
                            else:
                                scene_4_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        else:
                            scene_4_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        model = scene_4_translation
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[1])
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
            if(scene_index == 5):
                global scene_5_dis
                view = pyrr.matrix44.create_look_at(pyrr.Vector3([1, 3, 0]), pyrr.Vector3([0, 3, 0]), pyrr.Vector3([0, 1, 0]))
                if (scene_5_dis > 0):
                    scene_5_dis -= 0.01
                else:
                    scene_index += 1

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        if((x == -5 and (z == -3 or z == 3)) or (x == -6 and z == 0)):
                            scene_5_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, scene_5_dis, z]))
                        elif(x <= -10 and z <= 0 and math.fabs(x) + math.fabs(z) >= 21):
                            scene_5_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, math.fabs(x) + math.fabs(z) - 19, z]))
                        else:
                            scene_5_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        model = scene_5_translation
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[1])
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
            if(scene_index == 6):
                global scene_6_dis
                view = pyrr.matrix44.create_look_at(pyrr.Vector3([1, 3, 0]), pyrr.Vector3([0, 3, 0]), pyrr.Vector3([0, 1, 0]))
                if (scene_6_dis < 2):
                    scene_6_dis += 0.01
                else:
                    scene_index += 1

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        if(x == -5 and (z == -3 or z == 3)):
                            scene_6_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, scene_6_dis, z]))
                            glBindVertexArray(VAO[0])
                            glBindTexture(GL_TEXTURE_2D, textures[5])
                        elif (x == -6 and z == 0):
                            scene_6_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, scene_6_dis, z]))
                            glBindVertexArray(VAO[0])
                            glBindTexture(GL_TEXTURE_2D, textures[6])
                        elif(x <= -10 and z <= 0 and math.fabs(x) + math.fabs(z) >= 21):
                            glBindVertexArray(VAO[0])
                            glBindTexture(GL_TEXTURE_2D, textures[1])
                            scene_6_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, math.fabs(x) + math.fabs(z) - 19, z]))
                        else:
                            glBindVertexArray(VAO[0])
                            glBindTexture(GL_TEXTURE_2D, textures[1])
                            scene_6_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        model = scene_6_translation
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
            if(scene_index == 7):
                global scene_7_dis, scene_7_acc, scene_7_decay
                view = pyrr.matrix44.create_look_at(pyrr.Vector3([1, 3, 0]), pyrr.Vector3([0, 3, 0]), pyrr.Vector3([0, 1, 0]))
                if(scene_7_decay > 0):
                    scene_7_dis += scene_7_acc
                    scene_7_acc -= 0.01
                    if(scene_7_acc < -0.3):
                        scene_7_acc = 0.3
                        scene_7_decay -= 0.125
                else:
                    scene_index += 1

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        if(x <= -10 and z <= 0 and math.fabs(x) + math.fabs(z) >= 21):
                            scene_7_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, math.fabs(x) + math.fabs(z) - 19, z]))
                        else:
                            scene_7_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[1])
                        model = scene_7_translation
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

                scene_7_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-6, 2, 0]))
                glBindVertexArray(VAO[0])
                glBindTexture(GL_TEXTURE_2D, textures[6])
                model = scene_7_translation
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

                rotation = pyrr.Matrix44.from_y_rotation(glfw.get_time())
                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2 + scene_7_decay * scene_7_dis, -3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))
                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2 + scene_7_decay * scene_7_dis, 3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))
            if(scene_index == 8):
                global scene_8_dis, scene_8_acc, scene_8_decay
                view = pyrr.matrix44.create_look_at(pyrr.Vector3([1, 3, 0]), pyrr.Vector3([0, 3, 0]), pyrr.Vector3([0, 1, 0]))
                if (scene_8_decay > 0):
                    scene_8_dis += scene_8_acc
                    scene_8_acc -= 0.01
                    if (scene_8_acc < -0.3):
                        scene_8_acc = 0.3
                        scene_8_decay -= 0.125
                else:
                    scene_index += 1

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        if (x <= -10 and z <= 0 and math.fabs(x) + math.fabs(z) >= 21):
                            scene_7_translation = pyrr.matrix44.create_from_translation(
                                pyrr.Vector3([x, math.fabs(x) + math.fabs(z) - 19, z]))
                        else:
                            scene_7_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[1])
                        model = scene_7_translation
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

                rotation = pyrr.Matrix44.from_y_rotation(glfw.get_time())

                diamond_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-6, 2 + scene_8_decay * scene_8_dis, 0]))
                diamond_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.6, 0.6, 0.6]))
                model = pyrr.matrix44.multiply(rotation, diamond_scale)
                model = pyrr.matrix44.multiply(model, diamond_translation)
                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                glBindVertexArray(VAO[2])
                glBindTexture(GL_TEXTURE_2D, textures[3])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(diamond_indices))
                # glDrawElements(GL_TRIANGLES, len(diamond_indices), GL_UNSIGNED_INT, None)
                # glUniform1i(switcher_loc, 0)
                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2, -3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))
                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2, 3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))
            if(scene_index == 9):
                global scene_9_x, scene_9_y, scene_9_z, scene_9_roll, scene_9_pitch, scene_9_yaw
                view = pyrr.matrix44.create_look_at(pyrr.Vector3([scene_9_x, scene_9_y, scene_9_z]), pyrr.Vector3([10 * math.sin(scene_9_yaw) - 5, scene_9_pitch, 10 * math.cos(scene_9_yaw)]), pyrr.Vector3([math.sin(scene_9_roll), math.cos(scene_9_roll), 0]))
                if(scene_9_x > -5 and scene_9_yaw == -math.pi / 2):
                    scene_9_x -= 0.1
                    scene_9_pitch += 0.05
                elif(scene_9_x < -5 and scene_9_yaw > -math.pi):
                    scene_9_x += 0.02 * math.sin(scene_9_yaw)
                    scene_9_y += 0.01
                    scene_9_z += 0.02 * math.cos(scene_9_yaw)
                    scene_9_roll += math.pi / 900
                    scene_9_yaw -= math.pi / 180 * 0.3
                    scene_9_pitch -= 0.01
                elif(scene_9_yaw > -math.pi * 2):
                    scene_9_x += 0.01 * math.sin(scene_9_yaw)
                    scene_9_y -= 0.005
                    scene_9_z += 0.01 * math.cos(scene_9_yaw)
                    scene_9_roll -= math.pi / 1800
                    scene_9_pitch = 3
                    scene_9_yaw -= math.pi / 180 * 0.3
                elif(scene_9_z < 7):
                    view = pyrr.matrix44.create_look_at(pyrr.Vector3([scene_9_x, scene_9_y, scene_9_z]), pyrr.Vector3(
                        [-5, scene_9_pitch, scene_9_z + 15]), pyrr.Vector3([0, 1, 0]))
                    scene_9_x = -5
                    scene_9_y = 3
                    scene_9_z += 0.05
                    scene_9_pitch = 3
                    scene_9_yaw = -math.pi * 2
                elif(scene_9_yaw > -math.pi * 3):
                    glUniform1i(switcher_loc, 1)
                    glUniform3f(glGetUniformLocation(shader, "light.ambient"), 0.0, 0.0, 0.0)
                    glUniform3f(glGetUniformLocation(shader, "light.diffuse"), 0.0, 0.0, 0.0)
                    glUniform3f(glGetUniformLocation(shader, "light.specular"), 0.0, 0.0, 0.0)
                    view = pyrr.matrix44.create_look_at(pyrr.Vector3([scene_9_x, scene_9_y, scene_9_z]), pyrr.Vector3(
                        [-5 + math.sin(scene_9_yaw), scene_9_pitch, 15 * math.cos(scene_9_yaw) + 7]), pyrr.Vector3([0, 1, 0]))
                    scene_9_x = -5
                    scene_9_y = 3
                    scene_9_z = 7
                    scene_9_pitch = 3
                    scene_9_yaw -= math.pi / 180 * 0.5
                else:
                    scene_index += 1

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        if (x <= -10 and z <= 0 and math.fabs(x) + math.fabs(z) >= 21):
                            scene_7_translation = pyrr.matrix44.create_from_translation(
                                pyrr.Vector3([x, math.fabs(x) + math.fabs(z) - 19, z]))
                        else:
                            scene_7_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[1])
                        model = scene_7_translation
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

                rotation = pyrr.Matrix44.from_y_rotation(glfw.get_time())

                diamond_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-6, 2, 0]))
                diamond_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.6, 0.6, 0.6]))
                model = pyrr.matrix44.multiply(rotation, diamond_scale)
                model = pyrr.matrix44.multiply(model, diamond_translation)
                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                glBindVertexArray(VAO[2])
                glBindTexture(GL_TEXTURE_2D, textures[3])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(diamond_indices))

                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2, -3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))

                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2, 3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))

                if(not (scene_9_x > -5 and scene_9_yaw == -math.pi / 2)):
                    chibi_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-1, 1.5, 0]))
                    chibi_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.3, 0.3, 0.3]))
                    chibi_rotate = pyrr.matrix44.create_from_y_rotation(math.pi / 2)
                    model = pyrr.matrix44.multiply(chibi_scale, chibi_rotate)
                    model = pyrr.matrix44.multiply(model, chibi_translation)
                    glBindVertexArray(VAO[4])
                    glBindTexture(GL_TEXTURE_2D, textures[7])
                    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                    glDrawArrays(GL_TRIANGLES, 0, len(chibi_indices))
            if (scene_index == 10):
                # scene_index += 1
                global scene_10_dis_x, scene_10_dis_y, scene_10_dis_z, scene_10_step
                glUniform1i(switcher_loc, 1)
                glUniform3f(glGetUniformLocation(shader, "light.position"), scene_10_dis_x, scene_10_dis_y, scene_10_dis_z)
                if(scene_10_dis_y < 3):
                    scene_10_dis_y += 0.1
                elif(int(scene_10_step) == 1):
                    scene_10_dis_x -= 0.005
                    scene_10_step += 0.005
                elif(int(scene_10_step) == 2):
                    scene_10_dis_z -= 0.05
                    scene_10_step += 0.005
                elif(int(scene_10_step) == 3):
                    scene_10_dis_z += 0.1
                    scene_10_step += 0.005
                elif(int(scene_10_step) == 4):
                    scene_10_dis_z -= 0.05
                    scene_10_step += 0.005
                glUniform3f(glGetUniformLocation(shader, "light.ambient"), 0.05, 0.05, 0.05)
                glUniform3f(glGetUniformLocation(shader, "light.diffuse"), 0.9, 0.9, 0.9)
                glUniform3f(glGetUniformLocation(shader, "light.specular"), 0.9, 0.9, 0.9)

                view = cam.get_view_matrix()
                model = quad_translation

                glBindVertexArray(VAO[1])
                glBindTexture(GL_TEXTURE_2D, textures[2])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawElements(GL_TRIANGLES, len(quad_indices), GL_UNSIGNED_INT, None)

                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                for x in range(-20, 1):
                    for z in range(-10, 11):
                        if (x <= -10 and z <= 0 and math.fabs(x) + math.fabs(z) >= 21):
                            scene_7_translation = pyrr.matrix44.create_from_translation(
                                pyrr.Vector3([x, math.fabs(x) + math.fabs(z) - 19, z]))
                        else:
                            scene_7_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, 1, z]))
                        glBindVertexArray(VAO[0])
                        glBindTexture(GL_TEXTURE_2D, textures[1])
                        model = scene_7_translation
                        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

                rotation = pyrr.Matrix44.from_y_rotation(glfw.get_time())

                diamond_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-6, 2, 0]))
                diamond_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.6, 0.6, 0.6]))
                model = pyrr.matrix44.multiply(rotation, diamond_scale)
                model = pyrr.matrix44.multiply(model, diamond_translation)
                glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
                glBindVertexArray(VAO[2])
                glBindTexture(GL_TEXTURE_2D, textures[3])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(diamond_indices))

                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2, -3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))

                star_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-5, 2, 3]))
                star_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.5, 0.5, 0.5]))
                model = pyrr.matrix44.multiply(rotation, star_scale)
                model = pyrr.matrix44.multiply(model, star_translation)
                glBindVertexArray(VAO[3])
                glBindTexture(GL_TEXTURE_2D, textures[4])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(star_indices))

                chibi_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-1, 1.5, 0]))
                chibi_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.3, 0.3, 0.3]))
                chibi_rotate = pyrr.matrix44.create_from_y_rotation(math.pi / 2)
                model = pyrr.matrix44.multiply(chibi_scale, chibi_rotate)
                model = pyrr.matrix44.multiply(model, chibi_translation)
                glBindVertexArray(VAO[4])
                glBindTexture(GL_TEXTURE_2D, textures[7])
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
                glDrawArrays(GL_TRIANGLES, 0, len(chibi_indices))

            # glRotatef(2, 0, 1, 0)
            # glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

            glfw.swap_buffers(self._win)
        glfw.terminate()

class Camera:
    def __init__(self):
        self.camera_pos = pyrr.Vector3([-5.0, 3.0, 7.0])
        self.camera_front = pyrr.Vector3([0.0, 0.0, -1.0])
        self.camera_up = pyrr.Vector3([0.0, 1.0, 0.0])
        self.camera_right = pyrr.Vector3([1.0, 0.0, 0.0])

        self.mouse_sensitivity = 0.25
        self.yaw = 0
        self.pitch = 0

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if constrain_pitch:
            if self.pitch > 45:
                self.pitch = 45
            if self.pitch < -45:
                self.pitch = -45

        self.update_camera_vectors()

    def update_camera_vectors(self):
        front = pyrr.Vector3([0.0, 0.0, 0.0])
        front.x = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front.y = math.sin(math.radians(self.pitch))
        front.z = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)) * -1

        self.camera_front = pyrr.vector.normalise(front)
        self.camera_right = pyrr.vector.normalise(pyrr.vector3.cross(self.camera_front, pyrr.Vector3([0.0, 1.0, 0.0])))
        self.camera_up = pyrr.vector.normalise(pyrr.vector3.cross(self.camera_right, self.camera_front))

        # Camera method for the WASD movement

    def do_movement(self):
        if left:
            cam.process_keyboard("LEFT", 0.05)
        if right:
            cam.process_keyboard("RIGHT", 0.05)
        if forward:
            cam.process_keyboard("FORWARD", 0.05)
        if backward:
            cam.process_keyboard("BACKWARD", 0.05)

    def process_keyboard(self, direction, velocity):
        if direction == "FORWARD":
            self.camera_pos += self.camera_front * velocity
        if direction == "BACKWARD":
            self.camera_pos -= self.camera_front * velocity
        if direction == "LEFT":
            self.camera_pos -= self.camera_right * velocity
        if direction == "RIGHT":
            self.camera_pos += self.camera_right * velocity

win = Window(WINDOW_WIDTH, WINDOW_HEIGHT, "MineCraft")
cam = Camera()

if __name__ == "__main__":
    cube_vertices = [-0.5, -0.5,  0.5, 0.25, 1 / 3,  0,  0, -1, # 右面
                      0.5, -0.5,  0.5, 0.25, 2 / 3,  0,  0, -1,
                      0.5,  0.5,  0.5, 0.50, 2 / 3,  0,  0, -1,
                     -0.5,  0.5,  0.5, 0.50, 1 / 3,  0,  0, -1,

                     -0.5, -0.5, -0.5, 1.00, 1 / 3,  0,  0,  1, # 左面
                      0.5, -0.5, -0.5, 1.00, 2 / 3,  0,  0,  1,
                      0.5,  0.5, -0.5, 0.75, 2 / 3,  0,  0,  1,
                     -0.5,  0.5, -0.5, 0.75, 1 / 3,  0,  0,  1,

                      0.5, -0.5, -0.5, 0.00, 2 / 3, -1,  0,  0, # 后面
                      0.5,  0.5, -0.5, 0.00,  1.00, -1,  0,  0,
                      0.5,  0.5,  0.5, 0.25,  1.00, -1,  0,  0,
                      0.5, -0.5,  0.5, 0.25, 2 / 3, -1,  0,  0,

                     -0.5,  0.5, -0.5, 0.00,  0.00,  1,  0,  0, # 前面
                     -0.5, -0.5, -0.5, 0.00, 1 / 3,  1,  0,  0,
                     -0.5, -0.5,  0.5, 0.25, 1 / 3,  1,  0,  0,
                     -0.5,  0.5,  0.5, 0.25,  0.00,  1,  0,  0,

                     -0.5, -0.5, -0.5, 0.00, 1 / 3,  0, -1,  0, # 下面
                      0.5, -0.5, -0.5, 0.00, 2 / 3,  0, -1,  0,
                      0.5, -0.5,  0.5, 0.25, 2 / 3,  0, -1,  0,
                     -0.5, -0.5,  0.5, 0.25, 1 / 3,  0, -1,  0,

                      0.5,  0.5, -0.5, 0.75, 2 / 3,  0,  1,  0, # 上面
                     -0.5,  0.5, -0.5, 0.75, 1 / 3,  0,  1,  0,
                     -0.5,  0.5,  0.5, 0.50, 1 / 3,  0,  1,  0,
                      0.5,  0.5,  0.5, 0.50, 2 / 3,  0,  1,  0]

    cube_indices = [0,  1,  2,  2,  3,  0,
                    4,  5,  6,  6,  7,  4,
                    8,  9, 10, 10, 11,  8,
                   12, 13, 14, 14, 15, 12,
                   16, 17, 18, 18, 19, 16,
                   20, 21, 22, 22, 23, 20]
    cube_vertices = np.array(cube_vertices, dtype=np.float32)
    cube_indices = np.array(cube_indices, dtype=np.uint32)

    quad_vertices = [0,  1, -3, 1.0, 0.0, 1, 0, 0,
                     0, -1, -3, 1.0, 1.0, 1, 0, 0,
                     0, -1,  3, 0.0, 1.0, 1, 0, 0,
                     0,  1,  3, 0.0, 0.0, 1, 0, 0]

    quad_indices = [0, 1, 2, 2, 3, 0]

    quad_vertices = np.array(quad_vertices, dtype=np.float32)
    quad_indices = np.array(quad_indices, dtype=np.uint32)

    diamond_indices, diamond_vertices = ObjLoader.load_model("../obj/diamond.obj", True)
    # diamond_colors = []
    # for i in range(int(len(diamond_vertices) / 8)):
        # print(diamond_colors)
        # diamond_colors.extend([0.6, 0.85, 0.9])
        # print(diamond_vertices[i * 8 : i * 8 + 3], diamond_colors[i * 3 : i * 3 + 3], diamond_vertices[i * 8 + 5 : i * 8 + 8])
    # diamond_colors = np.array(diamond_colors, dtype=np.float32)
    # print(len(diamond_vertices) / 8)
    star_indices, star_vertices = ObjLoader.load_model("../obj/starR.obj", True)
    chibi_indices, chibi_vertices = ObjLoader.load_model("../obj/chibi.obj", True)
    jeep_indices, jeep_vertices = ObjLoader.load_model("../obj/jeep.obj", True)

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

    VAO = glGenVertexArrays(5)
    VBO = glGenBuffers(5)
    EBO = glGenBuffers(5)

    ########## Cube ##########
    glBindVertexArray(VAO[0])
    glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
    glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO[0])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 8, ctypes.c_void_p(20))

    ########## Quad ##########
    glBindVertexArray(VAO[1])
    glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
    glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO[1])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, quad_indices.nbytes, quad_indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, quad_vertices.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, quad_vertices.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, quad_vertices.itemsize * 8, ctypes.c_void_p(20))

    ########## Diamond ##########
    glBindVertexArray(VAO[2])
    glBindBuffer(GL_ARRAY_BUFFER, VBO[2])
    glBufferData(GL_ARRAY_BUFFER, diamond_vertices.nbytes, diamond_vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO[2])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, diamond_indices.nbytes, diamond_indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, diamond_vertices.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, diamond_vertices.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, diamond_vertices.itemsize * 8, ctypes.c_void_p(20))

    ########## Star ##########
    glBindVertexArray(VAO[3])
    glBindBuffer(GL_ARRAY_BUFFER, VBO[3])
    glBufferData(GL_ARRAY_BUFFER, star_vertices.nbytes, star_vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO[3])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, star_indices.nbytes, star_indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, star_vertices.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, star_vertices.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, star_vertices.itemsize * 8, ctypes.c_void_p(20))

    ########## Chibi ##########
    glBindVertexArray(VAO[4])
    glBindBuffer(GL_ARRAY_BUFFER, VBO[4])
    glBufferData(GL_ARRAY_BUFFER, chibi_vertices.nbytes, chibi_vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO[4])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, chibi_indices.nbytes, chibi_indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, chibi_vertices.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, chibi_vertices.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, chibi_vertices.itemsize * 8, ctypes.c_void_p(20))

    ########## Texture ##########
    textures = glGenTextures(8)

    load_texture("../img/tex_dirt.png", textures[0])
    load_texture("../img/tex_grass.png", textures[1])
    load_texture("../img/tex_minecraft.png", textures[2])
    load_texture("../obj/diamond.png", textures[3])
    load_texture("../obj/star.png", textures[4])
    load_texture("../img/tex_gold.png", textures[5])
    load_texture("../img/tex_diamond.png", textures[6])
    load_texture("../obj/chibi.png", textures[7])

    glUseProgram(shader)
    glClearColor(0, 0.3, 0.3, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND) # png透明用
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    projection = pyrr.matrix44.create_perspective_projection_matrix(45, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100)
    # projection = pyrr.matrix44.create_orthogonal_projection_matrix(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1000, 1000) # 正交用， -1000和100代表前面边界和后面边界
    cube_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))
    # translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([400, 200, -3])) # 正交用
    quad_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-10, 5, 0]))

    model_loc = glGetUniformLocation(shader, "model")
    proj_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")
    switcher_loc = glGetUniformLocation(shader, "switcher") # 切换材质与颜色用

    # Set lights properties
    glUniform3f(glGetUniformLocation(shader, "light.position"), 0.0, 3.0, 0.0)

    # Set material properties
    glUniform1i(glGetUniformLocation(shader, "material.diffuse"), 0)
    glUniform1i(glGetUniformLocation(shader, "material.specular"), 1)
    glUniform1f(glGetUniformLocation(shader, "material.shininess"), 32.0)

    glUniform1i(switcher_loc, 0)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

    win.main_loop()