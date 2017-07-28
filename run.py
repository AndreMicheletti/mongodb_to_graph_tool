import os, sys


"""###############
   # MAIN OBJECT class
   ##################"""

class CondominioModel(object):

    def __init__(self):
        self.name = ""
        self.fields = []
        self.reference_fields = []
        self.comment = ""

    def add_field(self, field_text):
        self.fields.append(field_text)

    def add_reference(self, reference_name):
        self.reference_fields.append(reference_name)


"""###############
   # HELPER FUNCTIONS
   ##################"""

# Clear comments in the line
# =========================
def strip_and_clear_comments(line):
    if ('#' in line):
        index = line.index("#")
        return line[:index].strip()
    return line.strip()


# Process if line contains a Class declaration
# =========================
def format_class(model, line):
    index = line.index("(")
    model.name = line[:index].replace("class","").strip()
    return model


# Process if line contains a Field declaration
# =========================
def format_field(model, line):
    try:
        if ("ReferenceField" in line):
            # Pick string starting from ReferenceField declaration
            start = line.index("db.ReferenceField(")
            line = line[start:].replace("db.ReferenceField(","")
            # Cut string after comma
            end = line.index(",")
            line = line[:end].replace(",","")
            # Insert as a reference
            model.add_reference(line.replace('"','').replace("'",'').strip())
        else:
            line = line.replace("db.", "").replace(" =", ":")
            index = line.index("(")
            model.add_field(line[:index])
        return model
    except:
        #print("substring not found for:\n{}".format(line))
        return model


# Check if line can be skipped
# =========================
def can_skip_line(line):
    # Skip if blank Line
    if (line == '' or line.startswith('#')):
        return True
    # Skip if it does not include class or field
    if ("class" not in line and "Field" not in line):
        return True
    if (line.startswith("@")):
        return True
    return False


# Process File
# =========================
def process_file(file_full_path):
    new_models = []
    model_current_working = False
    with open(file_full_path, 'r') as f:
        rd = f.readlines
        multiline_comment_flag = False
        try:
            for line in rd():
                line = line.strip()

                # Multiline comment detected
                if (line.count('"""') == 1):
                    multiline_comment_flag = not multiline_comment_flag
                    continue
                # Skip if it is inside a multiline comment
                if (multiline_comment_flag and isinstance(model_current_working, CondominioModel)):
                    model_current_working.comment += line.strip() + "\n"
                    continue

                # Skip if line has not what we want
                if (can_skip_line(line)): continue

                line = strip_and_clear_comments(line)
                if (line.startswith("class")):
                    # It's a class
                    if (isinstance(model_current_working, CondominioModel)):
                        new_models.append(model_current_working)
                    model_current_working = CondominioModel()
                    model_current_working = format_class(model_current_working, line)
                else:
                    # It's a Field
                    model_current_working = format_field(model_current_working, line)
            if (isinstance(model_current_working, CondominioModel)):
                new_models.append(model_current_working)

        except UnicodeDecodeError:
            return False
    if (len(new_models) <= 0):
        new_models = False
    return new_models


# Process Folder
# =========================
def process_folder(path):
    models = []

    for rootdir, dirs, files in os.walk(path):
        #print ("rootdir: " + str(rootdir))
        #print ("dirs:" + str(dirs))
        #print ("files:" + str(files))

        for folder in dirs:
            if (folder != rootdir): process_folder(rootdir + "/" + folder)

        for filename in files:
            if (filename != "models.py"):
                continue
            #print("looking into file {}".format(filename))
            new_models = process_file(rootdir + "/" + filename)
            if (new_models):
                for each_model in new_models:
                    models.append(each_model)

    return models

"""###############
   # MAIN PROGRAM
   ##################"""
if __name__ == '__main__':

    if (len(sys.argv) < 2):
        look_in = '.'
    else:
        look_in = str(sys.argv[1])

    models = process_folder(look_in)
    if (len(models) <= 0):
        print("No models found for specified path: {}".format(look_in))
        exit()

    print("\n DONE! {} Models found:\n".format(len(models)))
    for model in models:
        print("> " + model.name + " [" + str(len(model.fields)) + " FIELDS]")

    print("\n\nRendering...")
    from output import create_digraph_for_models, print_to_output
    output_name = create_digraph_for_models(models)
    print("DONE! File: {}\n".format(output_name))
