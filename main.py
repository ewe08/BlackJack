import os
import sys
import pygame

buttons = []

pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


FPS = 50
clock = pygame.time.Clock()


class Button:
    def create_button(self, surface, x, y, length, height, width, text, text_color):
        surface = self.write_text(surface, text, text_color, length, height, x, y)
        self.rect = pygame.Rect(x, y, length, height)
        return surface

    def write_text(self, surface, text, text_color, length, height, x, y):
        font_size = int(length // len(text))
        myFont = pygame.font.SysFont("gabriola", font_size)
        myText = myFont.render(text, 1, text_color)
        surface.blit(myText, (
            (x + length / 2) - myText.get_width() / 2, (y + height / 2) - myText.get_height() / 2))
        return surface

    def pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False


class Menu:
    def __init__(self):
        for label in ['Start', 'Quit']:
            self.new_button(label)
        self.main()

    # Update the display and show the button
    def update_display(self):
        fon = pygame.transform.scale(load_image('background\\menu_table.png'), (width, height))
        screen.blit(fon, (0, 0))
        fon = pygame.transform.scale(load_image('background\\diamond.png'), (width // 2, height))
        screen.blit(fon, (315, 0))

        x = 525
        y = 100
        for btn in buttons:
            btn[0].create_button(screen, x, y, 200, 100, 0, btn[1], (0, 0, 0))
            y += 200

    # Run the loop
    def main(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in buttons:
                        if btn[0].pressed(event.pos) and btn[1] == 'Quit':
                            terminate()
                self.update_display()
                pygame.display.flip()

    def new_button(self, text):
        buttons.append((Button(), text))


if __name__ == '__main__':
    menu = Menu()
