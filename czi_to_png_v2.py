import os
import argparse
from pylibCZIrw import czi
import matplotlib.image
from skimage.transform import resize
#TODO
# >>> ADAPT TO 5x/z-stack FILES
def sequence_conversion(file_name, file_prefix):
    #expected input "MM 437 LH C10.czi" or "MM 437 LH C1.czi"
    # or MM 437 LH C11_Final.czi or MM 437 LH C11_Full Tissue.czi or MM 437 LH C11 (large).czi
    keys = {'A':1,'B':2,'C':3,'D':4} #go up to E
    postfix = file_name[len(file_prefix):len(file_prefix)+4].strip().replace('.','')
    postfix_keynumber = keys[postfix[0]]
    postfix_numbers = int(postfix[1:])*10
    if postfix_numbers >= 100:
        new_postfix = '0' + str(postfix_keynumber + postfix_numbers)
    else:
        new_postfix = '0' + '0' + str(postfix_keynumber + postfix_numbers)
    if file_name[len(file_prefix)+4:].strip() == '.czi': #the case of nothing after "C##"
        new_prefix = file_prefix
    else:
        new_prefix = file_prefix + '_' + file_name[len(file_prefix)+4:].strip().replace('.czi','').replace('czi','')

    return new_prefix, new_postfix

def czi_to_image(czi_image_path, output_dir, downsize_factor, file_prefix):
    file_name = czi_image_path.split('/')[-1]
    #Load CZI

    with czi.open_czi(czi_image_path) as czi_image:
        print("\nResizing and saving image channels for file: " + file_name)
        #for each channel in czi file
        image_data = czi_image.metadata["ImageDocument"]["Metadata"]["Information"]["Image"]["Dimensions"]["Channels"]["Channel"]
        bounding_box = czi_image.total_bounding_rectangle[2:]
        for i in range(len(image_data)):#INSTEAD OF czi_dims, maybe just get shape of image_data
            channel_name = image_data[i]["@Name"].replace(" ","").replace("-","").replace("/","-")
            print("Resizing and saving image for channel: " + channel_name)
            frame = czi_image.read(plane={'C': i, 'Z': 0, 'T': 0})

            img = resize(frame[..., 0], (bounding_box[1] // downsize_factor, bounding_box[0] // downsize_factor), anti_aliasing=True)
            #img = resize(frame[..., 0], (449, 699), anti_aliasing=True)

            #prefix, postfix = sequence_conversion(file_name, file_prefix)
            postfix = file_name[len(file_prefix):len(file_prefix)+4].strip().replace('.','')
            #if sub-folder of channel name exists then save
            #else create sub-folder and save
            if os.path.exists(output_dir + channel_name):
                matplotlib.image.imsave(output_dir + channel_name + '/' + file_prefix + '_' + channel_name + "_" +  postfix + '.png', img)
            else:
                os.makedirs(output_dir + channel_name)
                matplotlib.image.imsave(output_dir + channel_name + '/' + file_prefix + '_' + channel_name + "_" + postfix + '.png', img)


def run(czi_dir, output_dir, file_prefix, downsize_factor):
    files = []
    file_exceptions = []
    exceptions = []


    for dirpath, dirnames, filenames in os.walk(czi_dir): #filtering only for files that match our prefix
        for filename in filenames:
            if filename[:len(file_prefix)].strip() == file_prefix:
                files.append(os.path.join(dirpath, filename))
    #replace each file directory for the file name
    for file in files:
        try:
            czi_to_image(file, output_dir, downsize_factor, file_prefix)
        except Exception as e:
            print("Failed to convert file: ", file)
            file_exceptions.append(file)
            exceptions.append(e)
    print("Finished converting files: " + str(len(files)))
    print("Failed files: " + str(len(file_exceptions)))
    for i in range(len(exceptions)):
        print(25 * '_')
        print("File Exceptions: ")
        print(file_exceptions[i])
        print(exceptions[i])
        print(25 * '_')

def main():
    parser = argparse.ArgumentParser(
        description="The output filenames for this script are those adapted for Tward et al histsetup.py"
                    "Please use an input folder with files that you've hand selected."
                    "**Z-stacks are not adapted, i.e. do not work yet."
    )

    parser.add_argument(
        '-i', '--input',
        help="Input directory containing files to process",
        required=True
    )

    parser.add_argument(
        '-o', '--output',
        help="Output directory for processed files",
        required=True
    )

    parser.add_argument(
        '-d', '--downsize',
        help="Downsize factor for output images",
        required=True

    )

    parser.add_argument(
        '-p', '--prefix',
        help='Prefix to filter input directory files i.e. "MM 437 LH" ',
        default=""
    )

    args = parser.parse_args()

    #FUTURE -- ADD OPTION TO SELECT ONLY ONE CHANNEL.
    input_dir = args.input
    output_dir = args.output
    prefix = args.prefix
    downsize_factor = int(args.downsize)
    print("################")
    print("Running with inputs: ")
    print("Input dir: " + input_dir)
    print("Output dir: " + output_dir)
    print("Downscaling factor: " + str(downsize_factor))
    print("Prefix: " + prefix)
    print("################")
    run(input_dir, output_dir, prefix, downsize_factor)

if __name__ == '__main__':
    main()