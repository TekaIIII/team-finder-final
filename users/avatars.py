from hashlib import sha256
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


def sdelat_avu(imya, pochta):
    razm = 256
    pal = (
        ("#DDE8E1", "#284B3A"),
        ("#E2E8F4", "#304A70"),
        ("#F1E5D8", "#6A4329"),
        ("#EAE1F1", "#543663"),
        ("#F2DFE3", "#733E4A"),
        ("#DFECEC", "#285454"),
    )

    pochta = pochta.strip().lower()
    kod = sha256(pochta.encode("utf-8")).digest()
    nom_cveta = kod[0] % len(pal)
    fon, ton = pal[nom_cveta]

    imya = imya.strip()
    if imya:
        buk = imya[0].upper()[:1]
    else:
        buk = "?"

    put = settings.BASE_DIR / "static" / "fonts" / "DejaVuSans-Bold.ttf"
    shr = ImageFont.truetype(str(put), size=120)
    img = Image.new("RGB", (razm, razm), color=fon)
    ris = ImageDraw.Draw(img)

    ram = ris.textbbox((0, 0), buk, font=shr)
    # textbbox учитывает отступы буквы внутри шрифта.
    shir_buk = ram[2] - ram[0]
    vys_buk = ram[3] - ram[1]
    x = (razm - shir_buk) // 2 - ram[0]
    y = (razm - vys_buk) // 2 - ram[1]
    ris.text((x, y), buk, font=shr, fill=ton)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue())
