import os
import argparse
from pylibCZIrw import czi
import matplotlib.image
from skimage.transform import resize
from czitools.metadata_tools.dimension import CziDimensions
from czitools.metadata_tools.czi_metadata import CziScaling
from czitools.metadata_tools.channel import CziChannelInfo

#TODO
# >>> ADAPT TO 5x/z-stack FILES
# >>> ADAPT TO DO ANY CZI FILE WITHOUT DESIGNATING PREFIX BY JUST COPYING FILENAME + CHANNEL NAME


def czi_to_image(czi_image_path, output_dir, downsize_factor, file_prefix, text_file_name):
    file_name = czi_image_path.split('/')[-1]

    with czi.open_czi(czi_image_path) as czi_image:
        print("\nResizing and saving image channels for file: " + file_name)

        # save original dimensions, spacing, and downsize_factor to a text file
        with open(text_file_name, 'a') as file:
            spacing = [CziScaling(czi_image_path).X, CziScaling(czi_image_path).Y]
            dims = f"{file_name},  original dims, {CziDimensions(czi_image_path).SizeX} {CziDimensions(czi_image_path).SizeY},  spacing, {spacing},  downscaling factor, {downsize_factor}\n"
            file.write(dims)
        #for each channel in czi file
        channels = CziChannelInfo(czi_image_path).names
        bounding_box = czi_image.total_bounding_rectangle[2:]
        for i in range(len(channels)):
            channel_name = CziChannelInfo(czi_image_path).names[i].replace(" ","").replace("-","").replace("/","-")

            print("Resizing and saving image for channel: " + channel_name)
            frame = czi_image.read(plane={'C': i, 'Z': 0, 'T': 0})

            img = resize(frame[..., 0], (bounding_box[1] // downsize_factor, bounding_box[0] // downsize_factor), anti_aliasing=True)

            postfix = file_name.split("\\")[-1].strip()[len(file_prefix):].replace('.czi','').replace('czi','').replace(" ", "") #anything after file prefix
            #if sub-folder of channel name exists then save
            #else create sub-folder and save
            if os.path.exists(output_dir + channel_name):
                matplotlib.image.imsave(output_dir + channel_name + '\\' + file_prefix + '_' + channel_name + "_" +  postfix + '.png', img)
            else:
                os.makedirs(output_dir + channel_name)
                matplotlib.image.imsave(output_dir + channel_name + '\\' + file_prefix + '_' + channel_name + "_" + postfix + '.png', img)


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
            #create a text file or append to an existing one for all czis that are going to be processed
            text_file_name = output_dir + 'dims.txt'

            if not os.path.exists(text_file_name):  # if file doesn't exist already
                os.makedirs(output_dir, exist_ok=True) #make parent folder if doesn't exist
                with open(text_file_name, 'w') as text_file: #make text file
                    text_file.write("OG CZI INFO:\n\n")

            czi_to_image(file, output_dir, downsize_factor, file_prefix, text_file_name)
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
        description="Please use an input folder with files that you've selected."
                    "Note the file prefix parameter: this looks at the folder and processes all the files with the same prefix, "
                    "- then uses this prefix to name the new file. "
                    "Z-stacks are not yet adapted."
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
