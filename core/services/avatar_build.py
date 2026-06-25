from django.conf import settings
from django.templatetags.static import static

from core.helpers import AvatarBuildOptions


def get_avatar_svg_url(user_id: int, **params):
    try:
        custom_url = settings.AVATAR_API_BASE_URL + f"?seed={user_id}"
        build_options = AvatarBuildOptions(**params)
        for key, value in vars(build_options).items():
                custom_url += f"&{key}={value if value is not None else ''}"
        return custom_url
    except Exception as e:
        print(str(e))
        return static('avatar/base.svg')
