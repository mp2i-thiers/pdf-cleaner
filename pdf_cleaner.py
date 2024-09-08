import fitz  # PyMuPDF
from PIL import Image, ImageChops

# Setup: pip install PyMuPDF pdf2image pillow
# Crédits: Alex M. et le C
# Disclaimer: Vérifiez que le nombre de pages est cohérent à la fin, on sait jamais.

# Load the PDF
input_pdf = "ordi.pdf"
output_pdf = f"{input_pdf[:-4]}_cleaned.pdf"
doc = fitz.open(input_pdf)


#page_number_area: valeurs arbitraires pour récupérer le numéro de page en bas à droite
def get_page_number_region(image, page_number_area=(0.9, 0.97, 1, 1)):
    width, height = image.size
    # Crop the bottom-right corner of the page
    cropped_image = image.crop((int(page_number_area[0] * width),
                                int(page_number_area[1] * height),
                                int(page_number_area[2] * width),
                                int(page_number_area[3] * height)))
    return cropped_image


#compare les images pour savoir si le numéro de page a changé
def images_are_different(img1, img2):
    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is not None


#Load first page
page = doc.load_page(0)
pix = page.get_pixmap()
img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
previous_page_number_region = get_page_number_region(img)

final_pages = []

# On commence de la page 2
for page_number in range(1, len(doc)):
    page = doc.load_page(page_number)
    pix = page.get_pixmap()

    # Convert the page to an image
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    current_page_number_region = get_page_number_region(img)

    # Si le numéro a changé, on sauvegarde l'index de la page précédente
    if images_are_different(current_page_number_region, previous_page_number_region):
        final_pages.append(page_number - 1)
        previous_page_number_region = current_page_number_region

# On enregistre aussi la dernière page si elle n'est pas déjà dans la liste
if len(doc) - 1 not in final_pages:
    final_pages.append(len(doc) - 1)

# Sauvegarde du nouveau fichier avec seulement les pages dont les indexs sont dans final_pages
with fitz.open() as output_doc:
    for page_number in final_pages:
        output_doc.insert_pdf(doc, from_page=page_number, to_page=page_number)
    output_doc.save(output_pdf)

print(f"Saved final version of each page to {output_pdf}")
