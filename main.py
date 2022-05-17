from email.policy import default
import click
from PIL import Image
import glob
import os
import logger as l
import searcher


@click.group()
def main():
    pass


# python3 main.py download
@main.command()
@click.option('-p', '--pattern', default='ak47', help="Search pattern ('ak47', 'mp5')")
@click.option('-w', '--webdriver', default='gecko', help="Webdriver ('gecko', 'chrome')")
@click.option('-s', '--size', default='medium', help="Image size which specified manually ('large', 'medium', 'icon')")
@click.option('-n', '--number', default=10, help="Number of images to download")
@click.option('-c', '--csplit', default=False, help="Enable splitting download images into pattern classes in download folder")
@click.option('-p', '--unique', default=True, help="Enable unique images name using hash lib")
@click.option('-p', '--path', default='./downloaded', help="")
@click.option('-g', '--gui', count=True)
@click.option('-t', '--threads', default=1, help='Number of threads')
@click.option('-u', '--unverified', default=False, help='Disable unverified HTTPS request (InsecureRequestWarning, up to you)')
def download(pattern, webdriver, size, number, path, gui, csplit, unique, threads, unverified):
    
    l.logI(f"Perform search for '{number}' with pattern '{pattern}' using '{webdriver}' webdriver.", bold=True)

    searcher.crawl(webdriver=webdriver, pattern=pattern, path=path, number_of_images=number, headless_mode = not gui, unique_img_name = unique, csplit = csplit, unverified = unverified, threads = threads)

    l.logI('Done!', bold=True)
    pass


# python3 main.py resize
@main.command()
@click.option('-s', '--size', default='512, 512', help="New size of images (value , value)")
@click.option('-p', '--path', default='./downloaded/', help="Path to downloaded images")
@click.option('-n', '--newdir', default='./resized/', help="Path to resized images")
def resize(size, path, newdir):

    size = size.strip().split(',')
    size = (int(size[0]) , int(size[1]))

    if not os.path.exists(newdir):
        os.makedirs(newdir)
    
    img_path_list = glob.glob(str(path) + '*.*')
    extensions = list()
    extensions = [im[-3:] for im in img_path_list]
    extensions = list(dict.fromkeys(extensions))

    l.logI(f'Found { len(img_path_list) } images with { extensions } extensions')

    if (len(img_path_list) > 0):
        l.logI('Start formatting images to ' + str(size[0]) + 'x' + str(size[1]))
        img_done = 0

        for filepath in img_path_list:
            image = Image.open(filepath)
            path, filename = os.path.split(filepath)
            
            new_filename = str(size[0]) + 'x' + str(size[1]) + '-'
            new_filename += filename
            l.logS(f'Resizing {filename}, saved to ' + str(newdir + new_filename))
            new_image = image.resize(size, Image.ANTIALIAS)
            new_image.save(newdir + new_filename)
            img_done += 1
    
        l.logI(f'Resized { img_done } from { len(img_path_list) } images', bold=True)
        l.logI('Done!', bold=True)
    
    else:
        l.logE(f'Images in {img_path_list} not found!')
    pass



# python3 main.py aug
@main.command()
@click.option('-p', '--path', default='./resized/', help="Path to resized images")
@click.option('-n', '--newdir', default='./augmented/', help="Path to resized images")
def aug(path, newdir):

    if not os.path.exists(newdir):
        os.makedirs(newdir)
    
    img_path_list = glob.glob(str(path) + '*.*')
    extensions = list()
    extensions = [im[-3:] for im in img_path_list]
    extensions = list(dict.fromkeys(extensions))

    l.logI(f'Found { len(img_path_list) } images with { extensions } extensions')

    if (len(img_path_list) > 0):
        l.logI('Start augmentating images...')
        img_done = 0

        for filepath in img_path_list:
            image = Image.open(filepath)
            path, filename = os.path.split(filepath)
            new_filename = 'augmented-'
            new_filename += filename
            l.logS(f'Augmenting {filename}, saved to ' + str(newdir + new_filename))
            new_image = image.transpose(Image.FLIP_LEFT_RIGHT)
            new_image.save(newdir + new_filename)
            img_done += 1
    
        l.logI(f'Augmented { img_done } from { len(img_path_list) } images', bold=True)
        l.logI('Done!', bold=True)
    
    else:
        l.logE(f'Images in {img_path_list} not found!')
    pass



# python3 main.py arrange
@main.command()
@click.option('-p', '--path', default='./augmented/', help="Path to source dataset")
@click.option('-d', '--dpath', default='./arranged/', help="New path for arranged images")
def arrange(path, dpath):

    l.logI('Start arranging', bold=True)

    # Create image folder if needed
    if not os.path.exists(dpath):
        os.makedirs(dpath)
    
    img_path_list = glob.glob(str(path) + '*.*')
    extensions = list()
    extensions = [im[-3:] for im in img_path_list]
    extensions = list(dict.fromkeys(extensions))

    l.logI(f'Found { len(img_path_list) } images with { extensions } extensions')

    digits = [0, 0, 0, 0, 0, 0]
    num = 1

    if (len(img_path_list) > 0):
        for filepath in img_path_list:
            image = Image.open(filepath)
            path, filename = os.path.split(filepath)


            x = [int(a) for a in str(num)]
            for i in range(-1, -1*(len(x) + 1), -1):
                if (x[i] != 0):
                    digits[i] = x[i]
                else:
                    digits[i] = 0

            dig = str(digits)
            dig = dig.replace(',', '')
            dig = dig.replace('[', '')
            dig = dig.replace(']', '')
            dig = dig.replace(" ", "")
            
            new_filename = dig

            new_filename += filename[-4:]
            l.logS(f'Arranging {filepath}, saved to ' + str(dpath + new_filename))
            new_image = image
            new_image.save(dpath + new_filename)

            num += 1
        
        l.logI('Done!', bold=True)
        
    else:
        l.logE(f'Images in {img_path_list} not found!')
    pass



if __name__ == '__main__':
    main()
