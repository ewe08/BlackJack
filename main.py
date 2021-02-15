import sys
import pygame

buttons = []


def terminate():
    pygame.quit()
    sys.exit()


class Button:
    def create_button(self, surface, color, x, y, length, height, width, text, text_color):
        surface = self.draw_button(surface, color, length, height, x, y, width)
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

    def draw_button(self, surface, color, length, height, x, y, width):
        # for i in range(1, 10):
            # s = pygame.Surface((length + (i * 2), height + (i * 2)))
            # s.fill(color)
            # alpha = (255 / (i + 2))
            # if alpha <= 0:
                # alpha = 1
            # s.set_alpha(alpha)
            # pygame.draw.rect(s, color, (x - i, y - i, length + i, height + i), width)
            # surface.blit(s, (x - i, y - i))
        # pygame.draw.rect(surface, color, (x, y, length, height), 0)
        # pygame.draw.rect(surface, (190, 190, 190), (x, y, length, height), 1)
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
        background = [pygame.image.load('data/background/menu_table.png'),
                      pygame.image.load('data/background/diamond.png')]
        screen.blit(background[0], (0, 0))
        screen.blit(background[1], (280, 0))
        x = 525
        y = 100
        for btn in buttons:
            btn[0].create_button(screen, (239, 239, 239), x, y, 200, 100, 0, btn[1], (0, 0, 0))
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
    pygame.init()
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size)
    menu = Menu()
