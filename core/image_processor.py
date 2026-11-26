from PIL import Image, ImageEnhance, ImageFilter

def process_image(image, pixel_size=3, colors=32, scanlines=True, crt=True, rgb_split=False):
    img = image.convert("RGBA")
    w, h = img.size
    small = img.resize(
        (max(1, w // pixel_size), max(1, h // pixel_size)),
        Image.Resampling.LANCZOS
    )
    small = small.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors)
    img = small.convert("RGBA").resize((w, h), Image.Resampling.NEAREST)

    if crt:
        rgb = ImageEnhance.Contrast(img.convert("RGB")).enhance(1.06)
        rgb = ImageEnhance.Color(rgb).enhance(0.94)
        rgb = rgb.filter(ImageFilter.UnsharpMask(radius=.5, percent=45, threshold=3))
        img = rgb.convert("RGBA")

    if scanlines:
        px = img.load()
        for y in range(1, h, 3):
            for x in range(w):
                r, g, b, a = px[x, y]
                px[x, y] = (int(r*.84), int(g*.84), int(b*.84), a)

    if rgb_split and w > 4:
        r, g, b, a = img.split()
        r = r.transform(r.size, Image.AFFINE, (1,0,-1,0,1,0))
        b = b.transform(b.size, Image.AFFINE, (1,0,1,0,1,0))
        img = Image.merge("RGBA", (r,g,b,a))
    return img
