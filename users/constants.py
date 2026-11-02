from enum import StrEnum

AVATAR_SIZE = 256
AVATAR_FONT_SIZE = 120
AVATAR_FONT_NAME = "DejaVuSans-Bold.ttf"
DEFAULT_AVATAR_PREFIX = "bukva_"


class AvatarColor(StrEnum):
    PALE_GREEN = "#DDE8E1"
    DARK_GREEN = "#284B3A"
    PALE_BLUE = "#E2E8F4"
    DARK_BLUE = "#304A70"
    PALE_SAND = "#F1E5D8"
    DARK_BROWN = "#6A4329"
    PALE_PURPLE = "#EAE1F1"
    DARK_PURPLE = "#543663"
    PALE_ROSE = "#F2DFE3"
    DARK_ROSE = "#733E4A"
    PALE_TEAL = "#DFECEC"
    DARK_TEAL = "#285454"


AVATAR_PALETTE = (
    (AvatarColor.PALE_GREEN, AvatarColor.DARK_GREEN),
    (AvatarColor.PALE_BLUE, AvatarColor.DARK_BLUE),
    (AvatarColor.PALE_SAND, AvatarColor.DARK_BROWN),
    (AvatarColor.PALE_PURPLE, AvatarColor.DARK_PURPLE),
    (AvatarColor.PALE_ROSE, AvatarColor.DARK_ROSE),
    (AvatarColor.PALE_TEAL, AvatarColor.DARK_TEAL),
)
