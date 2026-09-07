"""Create responsive WebP derivatives; keep every supplied source untouched."""
from pathlib import Path
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'app/shared/static/images'
TARGET=ROOT/'app/site/static/images'
FILES={'basic':'planbo_basic.png','standard':'plano_standard.png','premium':'plano_premium.png',
       'interior-1':'interior_beaultiful1.png','interior-2':'interior_beaultiful2.png','interior-3':'interior_beaultiful3.png',
       'kitchen':'interior_gallery3.jfif','bedroom':'interior_gallery8.jfif','exterior':'chale_exterior.jpg'}

def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    for name,filename in FILES.items():
        with Image.open(SOURCE/filename) as source:
            source=ImageOps.exif_transpose(source).convert('RGB')
            for width in (480,960,1440):
                image=source.copy()
                image.thumbnail((width,round(width*source.height/source.width)),Image.Resampling.LANCZOS)
                image.save(TARGET/f'{name}-{width}.webp',format='WEBP',quality=84,method=6)
    print('Created responsive images:',len(FILES)*3)

if __name__=='__main__': main()
