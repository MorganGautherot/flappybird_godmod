from typing import List

import pygame

HitMaskType = List[List[bool]]


def clamp(n: float, minn: float, maxn: float) -> float:
    """Clamps a number between two values"""
    return max(min(maxn, n), minn)


def pixel_collision(
    rect1: pygame.Rect,
    rect2: pygame.Rect,
    hitmask1: HitMaskType,
    hitmask2: HitMaskType,
) -> bool:
    """Checks if two objects collide

    Args:
       rect1(pygame.Rect): storing rectangular coordonate for object 1
       rect2(pygame.Rect): storing rectangular coordonate for object 2
       hitmask1(HitMaskType): heatmask for object 1
       hitmask2(HitMaskType): heatmask for object 2

    Returns:
       bool: True if the object 1 and 2 collide false otherwise
    """
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def get_hit_mask(image: pygame.Surface) -> HitMaskType:
    """returns a hit mask using an image's alpha

    Args:
       image(pygame.Surface): storing rectangular coordonate of the object

    Returns:
       HitMaskType: Return the hitmask of the object
    """
    return list(
        (
            list((bool(image.get_at((x, y))[3]) for y in range(image.get_height())))
            for x in range(image.get_width())
        )
    )


def collision(bird, pipes: List) -> bool:
    """Check the collision between bird and pipes
    Args:
       bird: bird to be checked
       pipes: list of the pipes to be checked
    Returns:
       bool: Return true if the bird collides with pipes
    """
    for pipe in pipes:
        if pixel_collision(bird.rect, pipe.rect, bird.hit_mask, pipe.hit_mask):
            return True
    return False
