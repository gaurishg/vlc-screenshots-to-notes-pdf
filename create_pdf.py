from PIL import Image, ImageDraw, ImageFont
import os, shutil, glob
import time
from create_dir_tree import DirectoryObject, FileOrFolder, create_directory_tree
from move_scr import DONE, BASE_DIR_PATH, PIC_EXTENSION_WITH_DOT
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import Bookmark

FONT_HEIGHT = 10
FONT_WIDTH = 10
IMAGE_EXTENSIONS = [".jpg"]
TEXT_POS = (0, 0)
TEMP_FOLDER = os.path.join(BASE_DIR_PATH, "temp")

def add_one(counter_list: list[list[int, int]]):
    """
        Increment counter by one at every place
    """
    for index in range(len(counter_list)):
        counter_list[index][0] += 1


def make_pdf_and_add_bookmarks(dir_object: DirectoryObject, pdf_writer: PdfFileWriter, image_exts: list[str] = None, list_of_sizes: list[list[int, int]] = None, parent_dir: str = None, parent_bookmark: Bookmark=None, make_pdf:bool = True, start_page_number: int=0) -> None:
    """
        Modifies all images in place and adds the text regarding page numbers
        make_pdf = True if you want to make pdf and False if pdf is already there and you just wanted to add bookmarks to it
    """
    if image_exts is None:
        image_exts = IMAGE_EXTENSIONS
    
    if parent_dir is None:
        parent_dir = BASE_DIR_PATH

    if list_of_sizes is None:
        list_of_sizes = []
    
    if dir_object.is_file():
        return

    if not make_pdf:
        parent_bookmark = pdf_writer.addBookmark(title=dir_object.name(), pagenum=start_page_number, parent=parent_bookmark)

    CUR_DIR_PATH = os.path.join(parent_dir, dir_object.name())
    
    total_number_of_files = dir_object.get_number_of_files(file_extension=image_exts)
    list_of_sizes.append([0, total_number_of_files])

    number_of_files_in_this_folder = dir_object.get_number_of_files(level=0, file_extension=image_exts)
    list_of_sizes.append([0, number_of_files_in_this_folder])

    images_in_this_folder = [im for im in dir_object.get_files() if any([im.name().lower().endswith(ext.lower()) for ext in image_exts])]
    if images_in_this_folder:
        # Line below should have worked but it was throwing error
        # images_in_this_folder = [Image.open(os.path.join(CUR_DIR_PATH, im.name()) for im in images_in_this_folder)]
        if make_pdf:
            for index in range(len(images_in_this_folder)):
                im = images_in_this_folder[index]
                img_path = os.path.join(CUR_DIR_PATH, im.name())
                images_in_this_folder[index] = Image.open(img_path)
            
            image_draws_in_this_folder = [ImageDraw.Draw(im) for im in images_in_this_folder]

            for image, imagedraw in zip(images_in_this_folder, image_draws_in_this_folder):
                add_one(list_of_sizes)
                text = ""
                for count, n_files in list_of_sizes:
                    text += f"{count}/{n_files}\n"
                font = ImageFont.truetype(r"RobotoFont\Roboto-Black.ttf", 20)
                bounding_box_of_text = imagedraw.multiline_textbbox(xy=(0, 0), text=text, font=font)
                imagedraw.rectangle(xy=bounding_box_of_text, fill=(255, 255, 255, 10))
                imagedraw.multiline_text(xy=TEXT_POS, text=text, fill=(0, 0, 0), font=font)
                filename = os.path.join(TEMP_FOLDER, f"{list_of_sizes[0][0]}.pdf")
                image.save(filename, "PDF")
                pdf_file = PdfFileReader(filename)
                pdf_writer.addPage(pdf_file.getPage(0))
                # pdf_writer.appendPagesFromReader(pdf_file)
        else:
            start_page_number += len(images_in_this_folder)
        
    list_of_sizes.pop()

    for folder in dir_object.get_folders():
        make_pdf_and_add_bookmarks(folder, pdf_writer=pdf_writer, image_exts=image_exts, list_of_sizes=list_of_sizes, parent_dir=CUR_DIR_PATH, parent_bookmark=parent_bookmark, start_page_number=list_of_sizes[0][0], make_pdf=make_pdf)
    list_of_sizes.pop()



if __name__ == '__main__':
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.makedirs(TEMP_FOLDER)
    
    IMAGE_DIR_TREE: DirectoryObject = create_directory_tree(os.path.join(BASE_DIR_PATH, DONE))
    print(IMAGE_DIR_TREE)
    print("Total image files in the folder", IMAGE_DIR_TREE.get_number_of_files(file_extension=[".png", ".jpG"]))


    TEMP_PDF_NAME = f'output-{time.strftime("%Y%m%d%H%M%S")}.pdf'
    print("Pdf filename", TEMP_PDF_NAME)
    pdf_writer = PdfFileWriter()

    # First create the PDF with the page numbers
    make_pdf_and_add_bookmarks(dir_object=IMAGE_DIR_TREE, pdf_writer=pdf_writer, image_exts=IMAGE_EXTENSIONS, list_of_sizes=None,
    parent_dir=None, parent_bookmark=None, make_pdf=True)

    # Now add bookmarks
    make_pdf_and_add_bookmarks(dir_object=IMAGE_DIR_TREE, pdf_writer=pdf_writer, image_exts=IMAGE_EXTENSIONS, list_of_sizes=None,
    parent_dir=None, parent_bookmark=None, make_pdf=False, start_page_number=0)

    with open(TEMP_PDF_NAME, "wb") as f_handle:
        pdf_writer.write(f_handle)

    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    