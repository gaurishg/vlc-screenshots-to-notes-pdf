from PIL import Image, ImageDraw, ImageFont
import os, shutil
import time
from create_dir_tree import DirectoryObject, create_directory_tree
from move_scr import DONE, BASE_DIR_PATH
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import Bookmark

FONT_HEIGHT = 10
FONT_WIDTH = 10
IMAGE_EXTENSIONS = [".jpg", ".png"]
TEXT_POS = (0, 0)
TEMP_FOLDER = os.path.join(BASE_DIR_PATH, "temp")
PYTHON_FILE_PATH = os.path.abspath(os.path.dirname(__file__))


def add_one(counter_list: list[tuple[int, int]]):
    """
        Increment counter by one at every place
    """
    for index in range(len(counter_list)):
        counter_list[index] = (counter_list[index][0] + 1, counter_list[index][1])


def make_pdf_and_add_bookmarks(
        dir_object: DirectoryObject, 
        pdf_writer: PdfWriter, 
        image_exts: list[str] | None = None, 
        list_of_sizes: list[tuple[int, int]] | None = None, 
        parent_dir: str | None = None, 
        parent_bookmark: Bookmark | None = None, 
        make_pdf:bool = True, 
        start_page_number: int=0) -> int:
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
        return 0

    if not make_pdf:
        parent_bookmark = pdf_writer.add_outline_item(title=dir_object.name(), page_number=start_page_number, parent=parent_bookmark)

    CUR_DIR_PATH = os.path.join(parent_dir, dir_object.name())
    
    total_number_of_photos = dir_object.get_number_of_files(file_extension=image_exts)
    list_of_sizes.append((0, total_number_of_photos))

    number_of_photos_in_this_folder = dir_object.get_number_of_files(level=0, file_extension=image_exts)
    list_of_sizes.append((0, number_of_photos_in_this_folder))

    image_objects_in_this_folder: list[Image.Image] = []
    dir_objects_in_this_folder = [im for im in dir_object.get_files() if any([im.name().lower().endswith(ext.lower()) for ext in image_exts])]
    if dir_objects_in_this_folder:
        # Line below should have worked but it was throwing error
        # images_in_this_folder = [Image.open(os.path.join(CUR_DIR_PATH, im.name()) for im in images_in_this_folder)]
        if make_pdf:
            for dir_obj in dir_objects_in_this_folder:
                img_path = os.path.join(CUR_DIR_PATH, dir_obj.name())
                image_objects_in_this_folder.append(Image.open(img_path))
            
            image_draws_in_this_folder = [ImageDraw.Draw(im) for im in image_objects_in_this_folder]

            for image, imagedraw in zip(image_objects_in_this_folder, image_draws_in_this_folder):
                add_one(list_of_sizes)
                text = ""
                for count, n_files in list_of_sizes:
                    text += f"{count}/{n_files}\n"
                font = ImageFont.truetype(os.path.join(PYTHON_FILE_PATH, "RobotoFont", "Roboto-Black.ttf"), 20)
                bounding_box_of_text = imagedraw.multiline_textbbox(xy=(0, 0), text=text, font=font)
                imagedraw.rectangle(xy=bounding_box_of_text, fill=(255, 255, 255, 10))
                imagedraw.multiline_text(xy=TEXT_POS, text=text, fill=(0, 0, 0), font=font)
                filename = os.path.join(TEMP_FOLDER, f"{list_of_sizes[0][0]}.pdf")
                image.save(filename, "PDF")
                pdf_file = PdfReader(filename)
                pdf_writer.add_page(pdf_file.pages[0])
                # pdf_writer.appendPagesFromReader(pdf_file)
    start_page_number += len(image_objects_in_this_folder)
        
    list_of_sizes.pop()

    for folder in dir_object.get_folders():
        start_page_number += make_pdf_and_add_bookmarks(folder, pdf_writer=pdf_writer, image_exts=image_exts, list_of_sizes=list_of_sizes, parent_dir=CUR_DIR_PATH, parent_bookmark=parent_bookmark, start_page_number=start_page_number, make_pdf=make_pdf)
    list_of_sizes.pop()

    return len(image_objects_in_this_folder)


def main():
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.makedirs(TEMP_FOLDER)
    
    IMAGE_DIR_TREE: DirectoryObject = create_directory_tree(os.path.join(BASE_DIR_PATH, DONE))
    print(IMAGE_DIR_TREE)
    print("Total image files in the folder", IMAGE_DIR_TREE.get_number_of_files(file_extension=[".png", ".jpG"]))


    TEMP_PDF_NAME = f'output-{time.strftime("%Y%m%d%H%M%S")}.pdf'
    print("Pdf filename", TEMP_PDF_NAME)
    pdf_writer = PdfWriter()

    # First create the PDF with the page numbers
    make_pdf_and_add_bookmarks(dir_object=IMAGE_DIR_TREE, pdf_writer=pdf_writer, image_exts=IMAGE_EXTENSIONS, list_of_sizes=None,
    parent_dir=None, parent_bookmark=None, make_pdf=True)

    # Now add bookmarks
    make_pdf_and_add_bookmarks(dir_object=IMAGE_DIR_TREE, pdf_writer=pdf_writer, image_exts=IMAGE_EXTENSIONS, list_of_sizes=None,
    parent_dir=None, parent_bookmark=None, make_pdf=False, start_page_number=0)

    with open(TEMP_PDF_NAME, "wb") as f_handle:
        pdf_writer.write(f_handle) # type: ignore

    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)


if __name__ == '__main__':
    main()
    