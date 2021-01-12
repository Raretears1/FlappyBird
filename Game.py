import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Окно игры, картинка,нижняя часть
S_HEIGHT = 750
S_WIDTH = 864

screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
pygame.display.set_caption("No name")

ground = pygame.image.load('ground1.png')
bg = pygame.image.load('bg_main.png')
restart_button = pygame.image.load('restart.png')
game_over_img = pygame.image.load('game_over.png')

# Игровые переменные
ground_scroll = 0
# скорость прокрутки
scroll_speed = 4
# начало игры, стартовый клик
start_click = False
# конец игры из-за колюзии с землей
game_over = False
# размер окна между трубами
pipe_window = 160
# скорость появления труб в милисекундах
pipe_scoll = 1650
# проверка когда была запуженна последняя труба
last_pipe = pygame.time.get_ticks()


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # создаю лист который будет содержать мои неподвижные обьекты по которым я буду быстро проходить,
        # тема же создавая анимацию
        self.images = []
        # создаю индекс чтоб отслеживать какую именно пнг показывать показывать
        self.index = 0
        # создаю каунтер для скорости показа
        self.counter = 0
        # через фор заполняю список птицами
        for change_bird in range(1, 4):
            birds = pygame.image.load(f'bird{change_bird}.png')
            self.images.append(birds)  # добавляю все три птицы в список
        self.image = self.images[self.index]  # устанавливаю по индексу первую птицу
        # создаю прямоугольник из обьекта птицы который создастграницы этого пнг
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        #     новая переменная обозначает скорость птицы, то есть силу тяжести вниз
        self.gravity = 0
        #     будет проверкой на зажатие мыши
        self.triger = False

    def update(self):
        if game_over == False:  # Пока не будет колюзии с землей птица будет двигаться

            if start_click == True:
                # анимация полета и падения, создание гравитации
                self.gravity += 0.5  # увеличиваю скорость падения с каждой итерацией
                if self.rect.bottom < 600:
                    self.rect.y += int(self.gravity)  # добовляю ее к координатам прямоугольника(птицы)
                if self.gravity > 8:  # ограничиваю скорость птицы, после сталкновения с землей
                    self.gravity = 8

            # анимация прыжков
            # через функцию, достаю по индексу левую кнопку мыши
            if pygame.mouse.get_pressed()[0] == 1 and self.triger == False:
                self.triger = True
                self.gravity = -9
            if pygame.mouse.get_pressed()[0] == 0:
                self.triger = False

            # анимация крыльев
            self.counter += 1

            handle_bit = 5
            # когда скорость будет больше, чтоб она не росла я сбрасываю ее до 0 а потом обновляю
            if self.counter > handle_bit:
                self.counter = 0
                self.index += 1
            #     делаю проверку на превышение пнг в моем списке
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]

            # Поворот птицы
            self.image = pygame.transform.rotate(self.images[self.index], self.gravity * -3)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()

        # позиции вверхней=1 и нижней=-1, функцие переворота обьектов
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_window / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_window / 2)]

    def update(self):  # делаем движение труб в левую сторону
        self.rect.x -= scroll_speed
        if self.rect.right < 0:  # для удаление труб за кадром
            self.kill()


class Restart():

    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        click = False

        # установка позиции миши на кнопке
        position = pygame.mouse.get_pos()

        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] == 1:
                click = True
        # нарисовать кнопку
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return click


pipe_group = pygame.sprite.Group()
# создаю группу птиц и передаю тем же координаты главной птицы(первого пнг)
bird_group = pygame.sprite.Group()

first_bird = Bird(100, int(S_HEIGHT / 2))

# добавляю в группу птиц те все пнг которые мне нужны
bird_group.add(first_bird)

button = Restart(S_WIDTH // 2 - 60, S_HEIGHT // 2 - 90, restart_button)
game_finish = Restart(170, S_HEIGHT // 2 - 40, game_over_img)

is_run = True
while is_run:

    clock.tick(fps)

    # задний фон
    screen.blit(bg, (0, 0))

    # Птица
    bird_group.draw(screen)
    bird_group.update()

    # Трубы
    pipe_group.draw(screen)

    # прокручивание земли и нарисовка
    screen.blit(ground, (ground_scroll, 600))

    # проверка колюзии с трубами, через ф-цию колюзии между группами
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or first_bird.rect.top < 0:
        game_over = True
        start_click = False

    # проверка колюзии с землей
    if first_bird.rect.bottom >= 600:
        game_over = True
        start_click = False

    if game_over == False and start_click == True:  # Пока не случилось колюзии, то есть удара об землю,
        # земля будет крутиться и пока не будет клика трубы не появяться
        # создаю новые трубы, только когда игра будет запущенна
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_scoll:
            pipe_height = random.randint(-130, 130)
            bottom_pipe = Pipe(S_WIDTH, int(S_HEIGHT / 2) + pipe_height, -1)
            top_pipe = Pipe(S_WIDTH, int(S_HEIGHT / 2) + pipe_height, 1)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        # механика прокручивания
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # проверка на окончание игры и сброса ее
    if game_over == True:
        if button.draw() == True:
            pipe_group.empty()
            first_bird.rect.x = 100
            first_bird.rect.y = int(S_HEIGHT / 2)
            game_over = False

    if game_over == True:
        game_finish.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_run = False
        #     Устанавливаю начало полета на нажатие миши И проверка на конец игры
        if event.type == pygame.MOUSEBUTTONDOWN and start_click == False and game_over == False:
            start_click = True
    pygame.display.update()

pygame.quit()
