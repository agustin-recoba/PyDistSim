import png
from numpy import Inf, ones, sign, sqrt, uint8, vstack
from numpy.random import rand

from pydistsim.conf import settings
from pydistsim.logger import logger


class Environment:
    """
    Environment abstract base class.

    This class represents an abstract base class for environments in the PyDistSim framework.
    """

    def __new__(self, **kwargs):
        """Return an instance of the default Environment.

        This method returns an instance of the default Environment subclass specified in the settings.

        :param kwargs: Additional keyword arguments to be passed to the subclass constructor.
        :return: An instance of the default Environment subclass.
        """
        for cls in self.__subclasses__():
            if cls.__name__ == settings.ENVIRONMENT:
                return super().__new__(cls, **kwargs)
        # if self is not Environment class (as in pickle.load_newobj) return
        # instance of self
        return super().__new__(self)

    def is_space(self, xy):
        """Check if the given coordinates represent a valid space in the environment.

        This method should be implemented by subclasses to determine whether the given coordinates
        represent a valid space in the environment.

        :param xy: The coordinates to check.
        :return: True if the coordinates represent a valid space, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError

    def are_visible(self, xy1, xy2):
        """Check if two coordinates are visible to each other in the environment.

        This method should be implemented by subclasses to determine whether the two given coordinates
        are visible to each other in the environment.

        :param xy1: The first set of coordinates.
        :param xy2: The second set of coordinates.
        :return: True if the coordinates are visible to each other, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError

    def find_random_pos(self, n=100):
        """
        Returns a random position in the environment.

        :param n: The maximum number of iterations to find a free space.
        :type n: int
        :return: The random position found.
        :rtype: tuple
        """
        raise NotImplementedError


class Environment2D(Environment):
    """
    Base class for 2D environment.
    The Environment2D allows to define map and scale of 2D environment.
    """

    def __init__(self, path="", scale=None, shape=None):
        """
        Initialize the Environment object.

        :param path: Optional. The path to an image file to load as the environment. If not provided, a default environment will be created.
        :param scale: Optional. The scale factor for the environment image. If not provided, the default scale factor will be used.
        :param shape: Optional. The shape of the environment. If not provided, the default shape will be used.
        """
        shape = shape if shape else settings.ENVIRONMENT2D_SHAPE
        if path:
            try:
                r = png.Reader(path)
                planes = r.read()[3]["planes"]
                self.image = vstack(map(uint8, r.asDirect()[2]))[:, ::planes]
                self.image = self.image[::-1, :]  # flip-up-down
                assert (r.height, r.width) == self.image.shape
            except OSError:
                logger.exception(
                    "Can't open {} creating new default environment.", path
                )

                self.image = uint8(ones(shape) * 255)
        else:
            self.image = uint8(ones(shape) * 255)

        self.dim = 2
        scale = not scale and 1 or int(scale)
        if scale > 1:
            raise NotImplementedError

    def __deepcopy__(self, memo):
        dup = Environment2D()
        dup.image = self.image.copy()
        return dup

    def is_space(self, xy):
        """
        Returns true if selected space (x,y) is space. If point xy
        is exactly on the edge or crossing check surrounding pixels.

        :param xy: A tuple representing the coordinates (x, y) of the space to check.
        :type xy: tuple
        :return: True if the selected space is a space, False otherwise.
        :rtype: bool
        """
        x, y = xy
        h, w = self.image.shape
        if x < 0 or x > w or y < 0 or y > h:
            return False
        check = True
        points = [xy]
        if xy[0] % 1 == 0:
            points.append([xy[0] - 1, xy[1]])
        if xy[1] % 1 == 0:
            points.append([xy[0], xy[1] - 1])
        if xy[0] % 1 == 0 and xy[1] % 1 == 0:
            points.append([xy[0] - 1, xy[1] - 1])
        try:
            for p in points:
                check = check and self.image[int(p[1]), int(p[0])] != 0
        except IndexError:
            check = False
        return check

    def are_visible(self, xy0, xy1):
        """
        Returns true if there is line of sight between source (x0,y0) and
        destination (x1,y1).

        :param xy0: Tuple representing the coordinates of the source point (x0, y0).
        :type xy0: tuple
        :param xy1: Tuple representing the coordinates of the destination point (x1, y1).
        :type xy1: tuple
        :return: True if there is line of sight between the source and destination points, False otherwise.
        :rtype: bool

        This is a floating point version of the Bresenham algorithm that does not spread on diagonal pixels.
        """
        x = x0 = xy0[0]
        y = y0 = xy0[1]
        x1 = xy1[0]
        y1 = xy1[1]
        d = sqrt(pow(x1 - x0, 2) + pow(y1 - y0, 2))
        incrE = (x1 - x0) / d  # incrE is cos in direction of x axis
        incrN = (y1 - y0) / d  # incrN is sin in direction of y axis

        # check if pixel (x,y) is target pixel (x1,y1) or
        # if float (x,y) is on N or E edge then check also W or S neighbor
        while not (
            (int(x) == int(x1) or (x % 1 == 0 and int(x) - 1 == int(x1)))
            and (int(y) == int(y1) or (y % 1 == 0 and int(y) - 1 == int(y1)))
        ):
            if incrE > 0:
                dx = 1 - x % 1
            else:
                dx = x % 1 == 0 and 1.0 or x % 1
            if incrN > 0:
                dy = 1 - y % 1
            else:
                dy = y % 1 == 0 and 1.0 or y % 1

            # check whether the path will hit first E/W or N/S pixel edge
            # by calculating length of paths
            if incrE != 0:
                cx = abs(dx / incrE)
            else:
                cx = Inf
            if incrN != 0:
                cy = abs(dy / incrN)
            else:
                cy = Inf

            # if path needed to hit N/S edge is longer than E/W
            if cx < cy:
                x = round(x + sign(incrE) * dx)  # spread on E
                y = y + cx * incrN
            else:
                x = x + cy * incrE
                y = round(y + sign(incrN) * dy)  # spread on N

            # logger.debug('x = {}, y = {}', str(x), str(y))
            if not self.is_space([x, y]):
                return False
        return True

    def find_random_pos(self, n=100):
        """
        Returns a random position in the environment.

        :param n: The maximum number of iterations to find a free space.
        :type n: int
        :return: The random position found.
        :rtype: tuple
        """
        n_init = n
        while n > 0:
            pos = rand(self.dim) * tuple(reversed(self.image.shape))
            if self.is_space(pos):
                break
            n -= 1
        logger.debug("Random position found in {} iterations.", (n_init - n))
        return pos
