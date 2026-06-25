from enum import Enum

class ColorOptions(str, Enum):
    YELLOW = "fafad2"
    LIGHT_GRAY = "d3d3d3"
    GRAY = "a9a9a9"
    DARK_GRAY = "323232"
    BLACK = "191919"
    OLIVE = "989789"
    LIGHT_BLUE = "5bc0de"
    BLUE = "428bca"
    DARK_BLUE = "03396c"
    BLUE_GRAY = "697b94"
    BLUE_GRAY_OPAQUE = "43677d"
    TURQUOISE = "009bbd"
    ROYAL_BLUE = "2663a3"
    PETROLEUM_BLUE = "477c90"
    LIGHT_GREEN = "88d8b0"
    GREEN = "44c585"
    DARK_GREEN = "00b159"
    DARK_GREEN_BLUE = "588387"
    MUSHROOM_GREEN = "5f705c"
    LIME_GREEN = "91cb15"
    GREEN_FLAG = "3d8a6b"
    LIGHT_RED = "ff6f69"
    RED = "d11141"
    DARK_RED = "ae0001"
    DARK_PINK = "a04b5d"
    VIVID_RED = "bd1700"
    PINK = "cc6192"
    BRICK_RED = "a62116"
    LIGHT_PINK_OPAQUE = "d29985"
    PINK_OPAQUE = "c98276"
    PINK_VIVID = "e35d6a"
    LIGHT_YELLOW = "ffeead"
    YELLOW_DARK = "ffd969"
    BEIGE_DARK = "cab188"
    LIGHT_BEIGE = "ffdbac"
    BROWN_GRAY = "876658"
    BROWN_DARK = "603a14"
    BROWN = "83623b"
    BROWN_RED = "611c17"
    BROWN_DARK_BLACK = "28150a"
    BROWN_SEPIA = "2e1e05"
    BROWN_LIGHT = "cb9e6e"
    BROWN_GOLD = "b68655"
    BROWN_MEDIUM = "a26d3d"
    BROWN_TERRACOTA = "8d5524"
    PURPLE = "614f8a"

class BeardOptions(str, Enum):
    VARIANT01 = "variant01"
    VARIANT02 = "variant02"
    VARIANT03 = "variant03"
    VARIANT04 = "variant04"
    VARIANT05 = "variant05"
    VARIANT06 = "variant06"
    VARIANT07 = "variant07"
    VARIANT08 = "variant08"

class ClothesOptions(str, Enum):
    VARIANT01 = "variant01"
    VARIANT02 = "variant02"
    VARIANT03 = "variant03"
    VARIANT04 = "variant04"
    VARIANT05 = "variant05"
    VARIANT06 = "variant06"
    VARIANT07 = "variant07"
    VARIANT08 = "variant08"
    VARIANT09 = "variant09"
    VARIANT10 = "variant10"

class EyeOptions(str, Enum):
    VARIANT01 = "variant01"
    VARIANT02 = "variant02"
    VARIANT03 = "variant03"
    VARIANT04 = "variant04"
    VARIANT05 = "variant05"
    VARIANT06 = "variant06"
    VARIANT07 = "variant07"
    VARIANT08 = "variant08"
    VARIANT09 = "variant09"
    VARIANT10 = "variant10"
    VARIANT11 = "variant11"
    VARIANT12 = "variant12"

class GlassesOptions(str, Enum):
    DARK01 = "dark01"
    DARK02 = "dark02"
    DARK03 = "dark03"
    DARK04 = "dark04"
    DARK05 = "dark05"
    DARK06 = "dark06"
    DARK07 = "dark07"
    LIGHT01 = "light01"
    LIGHT02 = "light02"
    LIGHT03 = "light03"
    LIGHT04 = "light04"
    LIGHT05 = "light05"
    LIGHT06 = "light06"
    LIGHT07 = "light07"

class HairOptions(str, Enum):
    LONG01 = "long01"
    LONG02 = "long02"
    LONG03 = "long03"
    LONG04 = "long04"
    LONG05 = "long05"
    LONG06 = "long06"
    LONG07 = "long07"
    LONG08 = "long08"
    LONG09 = "long09"
    LONG10 = "long10"
    LONG11 = "long11"
    LONG12 = "long12"
    LONG13 = "long13"
    LONG14 = "long14"
    LONG15 = "long15"
    LONG16 = "long16"
    LONG17 = "long17"
    LONG18 = "long18"
    LONG19 = "long19"
    LONG20 = "long20"
    LONG21 = "long21"
    LONG22 = "long22"
    SHORT01 = "short01"
    SHORT02 = "short02"
    SHORT03 = "short03"
    SHORT04 = "short04"
    SHORT05 = "short05"
    SHORT06 = "short06"
    SHORT07 = "short07"
    SHORT08 = "short08"
    SHORT09 = "short09"
    SHORT10 = "short10"
    SHORT11 = "short11"
    SHORT12 = "short12"
    SHORT13 = "short13"
    SHORT14 = "short14"
    SHORT15 = "short15"
    SHORT16 = "short16"
    SHORT17 = "short17"
    SHORT18 = "short18"
    SHORT19 = "short19"
    SHORT20 = "short20"
    SHORT21 = "short21"

class HatOptions(str, Enum):
    VARIANT01 = "variant01"
    VARIANT02 = "variant02"
    VARIANT03 = "variant03"
    VARIANT04 = "variant04"
    VARIANT05 = "variant05"
    VARIANT06 = "variant06"
    VARIANT07 = "variant07"
    VARIANT08 = "variant08"
    VARIANT09 = "variant09"
    VARIANT10 = "variant10"

class MouthOptions(str, Enum):
    HAPPY01 = "happy01"
    HAPPY02 = "happy02"
    HAPPY03 = "happy03"
    HAPPY04 = "happy04"
    HAPPY05 = "happy05"
    HAPPY06 = "happy06"
    HAPPY07 = "happy07"
    HAPPY08 = "happy08"
    HAPPY09 = "happy09"
    HAPPY10 = "happy10"
    HAPPY11 = "happy11"
    HAPPY12 = "happy12"
    SAD01 = "sad01"
    SAD02 = "sad02"
    SAD03 = "sad03"
    SAD04 = "sad04"
    SAD05 = "sad05"
    SAD06 = "sad06"
    SAD07 = "sad07"
    SAD08 = "sad08"
    SAD09 = "sad09"
    SAD10 = "sad10"


class AvatarBuildOptions():
    def __validate_color(self, color):
        if color is not None and color not in ColorOptions:
            return ColorOptions.LIGHT_BEIGE.value
        return color

    def __validate_beard_variant(self, variant):
        if variant is not None and variant not in BeardOptions:
            return None
        return variant
    
    def __validate_clothes_variant(self, variant):
        if variant is not None and variant not in ClothesOptions:
            return ClothesOptions.VARIANT03.value
        return variant
    
    def __validate_eyes_variant(self, variant):
        if variant is not None and variant not in EyeOptions:
            return EyeOptions.VARIANT07.value
        return variant
    
    def __validate_glasses_variant(self, variant):
        if variant is not None and variant not in GlassesOptions:
            return None
        return variant
    
    def __validate_hair_variant(self, variant):
        if variant is not None and variant not in HairOptions:
            return HairOptions.SHORT07.value
        return variant
    
    def __validate_hat_variant(self, variant):
        if variant is not None and variant not in HatOptions:
            return None
        return variant
    
    def __validate_mouth_variant(self, variant):
        if variant is not None and variant not in MouthOptions:
            return MouthOptions.HAPPY08.value
        return variant

    def __init__(self, **kwargs):
        self.accessoriesProbability = 0
        self.clothesProbability = 100
        self.eyesProbability = 100
        self.glassesProbability = 100
        self.hairProbability = 100
        self.hatProbability = 100
        self.mouthProbability = 100
        self.beardProbability = 100

        self.clothesVariant = self.__validate_clothes_variant(kwargs.get('clothesVariant', ClothesOptions.VARIANT01.value))
        self.eyesVariant = self.__validate_eyes_variant(kwargs.get('eyesVariant', EyeOptions.VARIANT07.value))
        self.glassesVariant = self.__validate_glasses_variant(kwargs.get('glassesVariant', None))
        self.hairVariant = self.__validate_hair_variant(kwargs.get('hairVariant', HairOptions.SHORT07.value))
        self.hatVariant = self.__validate_hat_variant(kwargs.get('hatVariant', None))
        self.mouthVariant = self.__validate_mouth_variant(kwargs.get('mouthVariant', MouthOptions.HAPPY08.value))
        self.beardVariant = self.__validate_beard_variant(kwargs.get('beardVariant', None))

        self.hairColor = self.__validate_color(kwargs.get('hairColor', ColorOptions.PURPLE.value))
        self.clothingColor = self.__validate_color(kwargs.get('clothingColor', ColorOptions.BLUE.value))
        self.eyesColor = self.__validate_color(kwargs.get('eyesColor', ColorOptions.BLUE.value))
        self.glassesColor = self.__validate_color(kwargs.get('glassesColor', None))
        self.hatColor = self.__validate_color(kwargs.get('hatColor', None))
        self.mouthColor = self.__validate_color(kwargs.get('mouthColor', ColorOptions.LIGHT_RED.value))
        self.skinColor = self.__validate_color(kwargs.get('skinColor', ColorOptions.LIGHT_BEIGE.value))
