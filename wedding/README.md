# دعوة زفاف — أحمد & حور

بطاقة دعوة زفاف بتصميم كلاسيكي (ورد مائي + أخضر زيتوني + ذهبي)، مكتوبة بالكامل بالـ HTML/SVG.

| الملف | الاستخدام |
|---|---|
| `wedding-invitation.png` | أعلى جودة للطباعة أو التعديل (2382 × 4020) |
| `wedding-invitation.jpg` | للإرسال على واتساب / فيسبوك (1588 × 2680) |
| `wedding-invitation.pdf` | للطباعة — صفحة A4 واحدة |
| `wedding-invitation.html` | النسخة الأصلية، تُفتح على أي متصفح وتعمل بدون إنترنت |

## التصميم الثاني — «القوس» (`design-b/`)

نسخة مختصرة بشكل مختلف: خلفية زيتوني غامق وقوس عاجي في النص، والكلام أقل
(الأسماء + التاريخ + المكان بس). مقاسها ١٠٨٠ × ١٣٥٠ يعني مظبوطة للإنستجرام
والواتساب. نفس الملفات: `.png` بجودة عالية و `.jpg` و `.pdf`.

## التصميم الثالث — «الزخرفة» (`design-c/`)

طابع إسلامي هندسي بدل الورد: نجوم ثمانية وزخرفة عربية، بألوان نبيتي وذهبي على
ورق كريمي. الآية هي بطلة التصميم — ﴿وَمِنْ آيَاتِهِ أَنْ خَلَقَ لَكُم مِّنْ أَنفُسِكُمْ أَزْوَاجًا
لِّتَسْكُنُوا إِلَيْهَا وَجَعَلَ بَيْنَكُم مَّوَدَّةً وَرَحْمَةً﴾ — سورة الروم، الآية ٢١ — جوّه إطار
مزخرف في أعلى البطاقة. المقاس ١٠٨٠ × ١٥٠٠.

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
python3 ornaments.py     # botanical SVGs for the framed design  -> ornaments/
python3 build.py         # assembles -> wedding-invitation.html
python3 ornaments_b.py   # botanical SVGs for the arch design    -> ornaments_b/
python3 build_b.py       # assembles -> wedding-invitation-b.html
python3 ornaments_c.py   # geometric SVGs for the arabesque design -> ornaments_c/
python3 build_c.py       # assembles -> wedding-invitation-c.html
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
