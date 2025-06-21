from paddleocr import PaddleOCR, draw_ocr
import os
from PIL import Image, ImageEnhance                                                                
import shutil
import re
import json
import time

ocr = PaddleOCR(use_angle_cls=True, lang='en') 

def image_text_scraper(img_path,saved_img_path):
    
    img_file = Image.open(img_path)
    img_file = img_file.convert("L")
    img_file.save("gray_scaled.png")
    result = ocr.ocr(img_path, cls=True)
    texts = []
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            texts.append(line[1][0])
    try:
        os.remove("gray_scaled.png")
    except:
        pass
    # draw result
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    font_path = os.path.join(os.path.dirname(__file__),"essentials",r"D:\Programming\Projects\SIH\Social_media_scraper\text_scraper\essentials\PaddleOCR\doc\fonts\latin.ttf")
    im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
    im_show = Image.fromarray(im_show)
    im_show.save(saved_img_path)
    # time.sleep(10)
    
    return result, texts

def image_folder_scraper(img_folder_fp, saved_img_folder_fp=None):

    if saved_img_folder_fp==None:
        saved_img_folder_fp = os.path.join(os.path.dirname(__file__),"scraped_text","last_scraped_images")
    
    if not os.path.exists(saved_img_folder_fp):
        os.makedirs(saved_img_folder_fp)
    else:
        # Empty the directory if it already exists
        for filename in os.listdir(saved_img_folder_fp):
            file_path = os.path.join(saved_img_folder_fp, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory
            except Exception as e:
                pass  # Silently pass on any exceptions

    imgs = os.listdir(img_folder_fp)
    imgs = sorted(imgs, key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)])
 
    raw_data = {}
    text_data = {}
    for img in imgs:
        if img == "data.json":
            continue
        try:
            img_path = os.path.join(img_folder_fp, img)
            saved_img_path = os.path.join(saved_img_folder_fp, img)
            raw_data[img] = image_text_scraper(img_path=img_path, saved_img_path=saved_img_path)[0]
            text_data[img] = image_text_scraper(img_path=img_path, saved_img_path=saved_img_path)[1]

            json_object = json.dumps(raw_data, indent=4)

            with open(os.path.join(saved_img_folder_fp,"raw_data.json"), "w") as outfile:
                outfile.write(json_object)

            json_object = json.dumps(text_data, indent=4)

            with open(os.path.join(saved_img_folder_fp,"text_data.json"), "w") as outfile:
                outfile.write(json_object)
        except:
            continue
    
    try:
        os.remove("gray_scaled.png")
    except:
        pass

    return raw_data

image_folder_scraper(img_folder_fp=r"D:\Programming\Projects\SIH\Social_media_scraper\X\Scraped_Data\elonmusk\media")