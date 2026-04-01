# get all files from user_ids

import os

from f import id_generator

for file in os.listdir("user_ids"):
    if file.endswith(".txt"):
        # read file
        with open(os.path.join("user_ids", file), "r") as f:
            # get all content from file and write to new file old_user_ids/file.txt

            with open(os.path.join("old_user_ids", file), "w") as f2:
                f2.write(f.read())

            new_data = []
            for i in range(0, 10000):
                new_data.append(id_generator())

            with open(os.path.join("user_ids", file), "w") as f3:
                f3.write("\n".join(new_data))

        print("Done with file: " + file)
