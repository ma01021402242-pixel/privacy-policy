# دعوة زفاف — أحمد & حور

بطاقة دعوة زفاف بتصميم كلاسيكي (ورد مائي + أخضر زيتوني + ذهبي)، مكتوبة بالكامل بالـ HTML/SVG.

| الملف | الاستخدام |
|---|---|
| `wedding-invitation.png` | أعلى جودة للطباعة أو التعديل (2382 × 4020) |
| `wedding-invitation.jpg` | للإرسال على واتساب / فيسبوك (1588 × 2680) |
| `wedding-invitation.pdf` | للطباعة — صفحة A4 واحدة |
| `wedding-invitation.html` | النسخة الأصلية، تُفتح على أي متصفح وتعمل بدون إنترنت |

## التفاصيل المكتوبة على البطاقة

- **العروسان:** أحمد & حور
- **التاريخ:** يوم السبت، الأول من أغسطس ٢٠٢٦
- **الساعة:** التاسعة مساءً
- **المكان:** قاعة جراند سولو — بعد كوبري الفحص

## Rebuilding

The published `wedding-invitation.html` is fully self-contained: the Amiri /
Aref Ruqaa / Reem Kufi / Cormorant Garamond webfonts are base64-inlined and
every ornament is procedurally generated SVG, so it renders identically
offline and on any device.

```sh
cd src
python3 embed_fonts.py   # downloads the Google Fonts subsets -> fonts.css
python3 ornaments.py     # regenerates the botanical SVGs -> ornaments/
python3 build.py         # assembles -> wedding-invitation.html
```

Export the shareable image and the print-ready PDF with headless Chromium:

```sh
chrome --headless --force-device-scale-factor=3 --window-size=900,1470 \
       --screenshot=raw3x.png file://$PWD/wedding-invitation.html   # then crop to the card
chrome --headless --no-pdf-header-footer \
       --print-to-pdf=wedding-invitation.pdf file://$PWD/wedding-invitation.html
```

To change the names, date, time or venue, edit `src/invitation.template.html`
and re-run `build.py`. The card is a fixed 794 × 1340 px canvas; print CSS scales it down onto a
single A4 sheet, and it shrinks to fit narrow phone screens automatically.
